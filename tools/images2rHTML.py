#!/usr/bin/env python3
"""images2rHTML Restricted Viewer Format v1 generator."""

from __future__ import annotations

import argparse
import base64
import binascii
import getpass
import html
import os
import tempfile
import hashlib
import json
import math
import secrets
import sys
import unicodedata
from datetime import UTC, datetime
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path
from typing import Any, Literal

VERSION = "0.1.0.dev3"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MIME_TYPES = {"png": "image/png", "jpeg": "image/jpeg", "webp": "image/webp"}
EXIT_SUCCESS = 0
EXIT_FATAL = 1
EXIT_PARTIAL = 2
RECOVERY_PAYLOAD_TYPE = "mdworks-restricted-viewer-recovery"
RECOVERY_FORMAT = "mdworks-restricted-viewer"
RECOVERY_BOX_LABEL = "restricted-viewer-recovery"
RECOVERY_KDF_ITERATIONS = 310_000
RECOVERY_SALT_BYTES = 16
RECOVERY_IV_BYTES = 12
RECOVERY_KEY_BYTES = 32
AES_GCM_TAG_BYTES = 16
DISPLAY_PAYLOAD_TYPE = "mdworks-restricted-viewer-display"
DISPLAY_KEY_BYTES = 32
DISPLAY_IV_BYTES = 12
VIEWER_BOX_SCRIPT_ID = "mdworks-restricted-viewer-box"
RECOMMENDED_VIEWER_SUFFIX = ".restricted.view.html"
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "restricted-viewer-v1.html"

ImageKind = Literal["png", "jpeg", "webp"]


@dataclass(frozen=True)
class CandidateImage:
    """A filesystem entry with a supported image extension."""

    path: Path


@dataclass(frozen=True)
class ValidImage:
    """A validated source image ready for Markdown embedding."""

    path: Path
    kind: ImageKind
    size_bytes: int


@dataclass(frozen=True)
class SkippedImage:
    """A skipped image and the reason it was not processed."""

    path: Path
    reason: str


@dataclass(frozen=True)
class PipelineResult:
    """Aggregated Phase 1 processing result."""

    valid_images: list[ValidImage]
    skipped_images: list[SkippedImage]
    markdown: str | None = None


def positive_int(value: str) -> int:
    """Parse a positive integer option value."""
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected an integer, got: {value}") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="images2rHTML.py",
        description=(
            "Generate MD//WORKS Restricted Viewer Format v1 single-file HTML from PNG/JPEG/WebP image folders."
        ),
    )
    parser.add_argument("input_dir", metavar="INPUT_DIR", type=Path, help="Input image directory.")
    parser.add_argument("-o", "--output", type=Path, help="Write final .restricted.view.html output.")
    parser.add_argument("--emit-markdown", type=Path, help="Phase 1 developer option: write generated Markdown to FILE.")
    parser.add_argument("--emit-recovery-box", type=Path, help="Phase 2 developer option: write Recovery box JSON to FILE.")
    parser.add_argument("--title", help="Document title to store in viewer metadata.")
    parser.add_argument(
        "--recovery-password",
        action="store_true",
        help="Prompt twice for the Recovery password when generating Restricted Viewer HTML or --emit-recovery-box.",
    )
    parser.add_argument("--max-kb", type=positive_int, help="Maximum accepted source image size in KiB.")
    parser.add_argument("--warning-mb", type=positive_int, help="Warn when estimated Markdown size exceeds this many MiB.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing emitted Markdown or Recovery box file.")
    parser.add_argument("--dry-run", action="store_true", help="Report planned processing without writing output.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser


def natural_sort_key(path: Path) -> tuple[object, ...]:
    """Return a deterministic natural-sort key based on filename only.

    Unicode NFKC and casefolding are used only for comparison. Filenames are not renamed.
    """
    text = unicodedata.normalize("NFKC", path.name).casefold()
    parts: list[object] = []
    index = 0
    while index < len(text):
        digit = unicodedata.decimal(text[index], None)
        if digit is None:
            start = index
            while index < len(text) and unicodedata.decimal(text[index], None) is None:
                index += 1
            parts.append((1, text[start:index]))
            continue
        digits: list[str] = []
        while index < len(text):
            value = unicodedata.decimal(text[index], None)
            if value is None:
                break
            digits.append(str(value))
            index += 1
        digits_text = "".join(digits)
        parts.append((0, int(digits_text), len(digits_text), digits_text))
    return (*parts, unicodedata.normalize("NFKC", path.name), path.name.encode("utf-8", "surrogatepass"))


def enumerate_input_images(input_dir: Path) -> list[CandidateImage]:
    """Enumerate supported regular files directly under input_dir.

    Path.iterdir() follows symlinks for is_file(); symlinked files are accepted, but
    directories and symlinked directories are not searched recursively.
    """
    return sorted(
        (CandidateImage(entry) for entry in input_dir.iterdir() if entry.is_file() and entry.suffix.lower() in SUPPORTED_EXTENSIONS),
        key=lambda candidate: natural_sort_key(candidate.path),
    )


def expected_kind(path: Path) -> ImageKind:
    """Map a supported filename extension to an image kind."""
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "png"
    if suffix in {".jpg", ".jpeg"}:
        return "jpeg"
    if suffix == ".webp":
        return "webp"
    raise ValueError(f"unsupported extension: {path.suffix}")


def detect_signature(header: bytes) -> ImageKind | None:
    """Detect an image kind using minimal file signatures."""
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if header.startswith(b"\xff\xd8"):
        return "jpeg"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "webp"
    return None


def validate_image(candidate: CandidateImage, max_kb: int | None = None) -> ValidImage | SkippedImage:
    """Validate readability, size, extension/signature match, and non-empty content."""
    path = candidate.path
    try:
        size = path.stat().st_size
    except OSError as exc:
        return SkippedImage(path, f"cannot stat file: {exc.strerror or exc}")
    if size == 0:
        return SkippedImage(path, "empty file")
    if max_kb is not None and size > max_kb * 1024:
        return SkippedImage(path, f"exceeds --max-kb ({max_kb} KiB)")
    try:
        with path.open("rb") as handle:
            header = handle.read(16)
    except OSError as exc:
        return SkippedImage(path, f"cannot read file: {exc.strerror or exc}")
    actual = detect_signature(header)
    if actual is None:
        return SkippedImage(path, "corrupt or unrecognized image signature")
    expected = expected_kind(path)
    if actual != expected:
        return SkippedImage(path, f"extension/signature mismatch: extension is {expected}, signature is {actual}")
    return ValidImage(path, actual, size)


def process_input_images(input_dir: Path, max_kb: int | None = None, include_markdown: bool = False) -> PipelineResult:
    """Run Phase 1 input processing and optionally generate Markdown."""
    candidates = enumerate_input_images(input_dir)
    if not candidates:
        raise RuntimeError(f"No supported images found in input directory: {input_dir}")
    valid: list[ValidImage] = []
    skipped: list[SkippedImage] = []
    for candidate in candidates:
        result = validate_image(candidate, max_kb)
        if isinstance(result, ValidImage):
            valid.append(result)
        else:
            skipped.append(result)
    if not valid:
        raise RuntimeError("No valid images remain after validation.")
    markdown = generate_markdown_document(valid) if include_markdown else None
    return PipelineResult(valid, skipped, markdown)


def sanitize_markdown_text(text: str, *, fallback: str) -> str:
    """Preserve visible text while replacing Markdown-structure-breaking controls."""
    cleaned = "".join(" " if unicodedata.category(ch)[0] == "C" else ch for ch in text)
    cleaned = cleaned.strip()
    return cleaned or fallback


def heading_text(path: Path) -> str:
    """Return safe heading text derived from the original filename stem."""
    return sanitize_markdown_text(path.stem, fallback="Untitled")


def alt_text(path: Path) -> str:
    """Return Markdown-safe alt text derived from the original filename stem."""
    text = sanitize_markdown_text(path.stem, fallback="Untitled")
    return text.replace("\\", "\\\\").replace("]", "\\]")


def image_to_base64(path: Path) -> str:
    """Read an image and encode it using standard RFC 4648 Base64."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


def generate_image_markdown(image: ValidImage) -> str:
    """Generate Markdown for one image."""
    mime = MIME_TYPES[image.kind]
    encoded = image_to_base64(image.path)
    return f"## {heading_text(image.path)}\n\n![{alt_text(image.path)}](data:{mime};base64,{encoded})"


def generate_markdown_document(images: list[ValidImage]) -> str:
    """Generate a full Markdown document from already-sorted images."""
    return "\n\n".join(generate_image_markdown(image) for image in images) + "\n"



def utc_timestamp(created_at: datetime | None = None) -> str:
    """Return a UTC ISO 8601 timestamp with millisecond precision and Z suffix."""
    moment = created_at or datetime.now(UTC)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    moment = moment.astimezone(UTC)
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def create_recovery_payload(
    *,
    title: str,
    filename: str,
    markdown: str,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    """Create a Format v1 Recovery payload without changing Markdown text."""
    if not isinstance(title, str) or not isinstance(filename, str) or not isinstance(markdown, str):
        raise ValueError("title, filename, and markdown must be strings")
    return {
        "v": 1,
        "type": RECOVERY_PAYLOAD_TYPE,
        "title": title,
        "filename": filename,
        "createdAt": utc_timestamp(created_at),
        "format": RECOVERY_FORMAT,
        "markdown": markdown,
    }


def serialize_recovery_payload(payload: dict[str, Any]) -> str:
    """Serialize Recovery payload JSON deterministically enough for tests."""
    validate_recovery_payload(payload)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def derive_recovery_key(password: str, salt: bytes) -> bytes:
    """Derive the AES-256-GCM key from an exact password string."""
    if password == "":
        raise ValueError("recovery password must not be empty")
    if len(salt) != RECOVERY_SALT_BYTES:
        raise ValueError("recovery salt must be 16 bytes")
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        RECOVERY_KDF_ITERATIONS,
        dklen=RECOVERY_KEY_BYTES,
    )


def encrypt_recovery_json(plaintext_json: str, password: str, *, salt: bytes | None = None, iv: bytes | None = None) -> dict[str, Any]:
    """Encrypt serialized Recovery payload JSON and return a Recovery box."""
    actual_salt = salt if salt is not None else secrets.token_bytes(RECOVERY_SALT_BYTES)
    actual_iv = iv if iv is not None else secrets.token_bytes(RECOVERY_IV_BYTES)
    if len(actual_iv) != RECOVERY_IV_BYTES:
        raise ValueError("recovery IV must be 12 bytes")
    key = derive_recovery_key(password, actual_salt)
    data = AESGCM(key).encrypt(actual_iv, plaintext_json.encode("utf-8"), None)
    return {
        "v": 1,
        "label": RECOVERY_BOX_LABEL,
        "alg": "AES-GCM",
        "kdf": "PBKDF2",
        "hash": "SHA-256",
        "iterations": RECOVERY_KDF_ITERATIONS,
        "salt": base64.b64encode(actual_salt).decode("ascii"),
        "iv": base64.b64encode(actual_iv).decode("ascii"),
        "data": base64.b64encode(data).decode("ascii"),
    }


def create_recovery_box(
    *,
    title: str,
    filename: str,
    markdown: str,
    password: str,
    created_at: datetime | None = None,
    salt: bytes | None = None,
    iv: bytes | None = None,
) -> dict[str, Any]:
    """Create and encrypt a Recovery payload."""
    payload = create_recovery_payload(title=title, filename=filename, markdown=markdown, created_at=created_at)
    return encrypt_recovery_json(serialize_recovery_payload(payload), password, salt=salt, iv=iv)


def strict_b64decode(value: Any, field: str) -> bytes:
    """Decode standard Base64 with padding validation."""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a Base64 string")
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        raise ValueError(f"{field} is not valid standard Base64") from exc


def validate_recovery_box(box: dict[str, Any]) -> tuple[bytes, bytes, bytes]:
    """Validate a Recovery box and return decoded salt, IV, and ciphertext/tag."""
    expected = {
        "v": 1,
        "label": RECOVERY_BOX_LABEL,
        "alg": "AES-GCM",
        "kdf": "PBKDF2",
        "hash": "SHA-256",
        "iterations": RECOVERY_KDF_ITERATIONS,
    }
    for field, value in expected.items():
        if box.get(field) != value:
            raise ValueError(f"invalid Recovery box {field}")
    salt = strict_b64decode(box.get("salt"), "salt")
    iv = strict_b64decode(box.get("iv"), "iv")
    data = strict_b64decode(box.get("data"), "data")
    if len(salt) != RECOVERY_SALT_BYTES:
        raise ValueError("invalid Recovery box salt length")
    if len(iv) != RECOVERY_IV_BYTES:
        raise ValueError("invalid Recovery box IV length")
    if len(data) < AES_GCM_TAG_BYTES:
        raise ValueError("invalid Recovery box data length")
    return salt, iv, data


def validate_recovery_payload(payload: dict[str, Any]) -> None:
    """Validate decrypted Recovery payload constants and core field types."""
    if payload.get("v") != 1:
        raise ValueError("invalid Recovery payload version")
    if payload.get("type") != RECOVERY_PAYLOAD_TYPE:
        raise ValueError("invalid Recovery payload type")
    if payload.get("format") != RECOVERY_FORMAT:
        raise ValueError("invalid Recovery payload format")
    if not isinstance(payload.get("markdown"), str):
        raise ValueError("invalid Recovery payload markdown")
    if not isinstance(payload.get("filename"), str):
        raise ValueError("invalid Recovery payload filename")


def decrypt_recovery_box(box: dict[str, Any], password: str) -> dict[str, Any]:
    """Decrypt and validate a Recovery box using the exact password string."""
    salt, iv, data = validate_recovery_box(box)
    key = derive_recovery_key(password, salt)
    try:
        plaintext = AESGCM(key).decrypt(iv, data, None)
    except InvalidTag as exc:
        raise ValueError("Recovery box authentication failed") from exc
    try:
        payload = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Recovery payload is not valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("Recovery payload must be a JSON object")
    validate_recovery_payload(payload)
    return payload


def prompt_recovery_password() -> str:
    """Prompt twice for a Recovery password without echoing it."""
    first = getpass.getpass("Recovery password: ")
    second = getpass.getpass("Confirm recovery password: ")
    if first != second:
        raise ValueError("recovery passwords do not match")
    if first == "":
        raise ValueError("recovery password must not be empty")
    return first


def recovery_filename_for_title(title: str | None) -> str:
    """Choose the Recovery Markdown filename used in Phase 2 developer output."""
    candidate = title if title else "presentation.md"
    return candidate if candidate.endswith(".md") else f"{candidate}.md"


def html_heading_text(path: Path) -> str:
    """Return display heading text derived from the original filename stem."""
    return sanitize_markdown_text(path.stem, fallback="Untitled")


def generate_display_html(images: list[ValidImage]) -> str:
    """Generate image-only safe HTML directly from validated images."""
    sections: list[str] = []
    for index, image in enumerate(images, start=1):
        title = html_heading_text(image.path)
        escaped_title = html.escape(title, quote=True)
        encoded = image_to_base64(image.path)
        mime = MIME_TYPES[image.kind]
        sections.append(
            '<section class="viewer-section">\n'
            f'  <h2 id="slide-{index}">{escaped_title}</h2>\n'
            '  <p class="viewer-image">\n'
            '    <img\n'
            f'      src="data:{mime};base64,{encoded}"\n'
            f'      alt="{escaped_title}"\n'
            '      loading="lazy"\n'
            '      draggable="false">\n'
            '  </p>\n'
            '</section>'
        )
    return "\n".join(sections)


def create_display_payload(*, title: str, html: str, created_at: datetime | None = None) -> dict[str, Any]:
    """Create a Format v1 Display payload."""
    if not isinstance(title, str) or not isinstance(html, str):
        raise ValueError("title and html must be strings")
    return {"v": 1, "type": DISPLAY_PAYLOAD_TYPE, "title": title, "createdAt": utc_timestamp(created_at), "html": html}


def serialize_display_payload(payload: dict[str, Any]) -> str:
    """Serialize Display payload JSON as UTF-8-compatible text."""
    if payload.get("v") != 1 or payload.get("type") != DISPLAY_PAYLOAD_TYPE:
        raise ValueError("invalid Display payload constants")
    if not isinstance(payload.get("title"), str) or not isinstance(payload.get("createdAt"), str) or not isinstance(payload.get("html"), str):
        raise ValueError("invalid Display payload fields")
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def create_display_box(*, title: str, html: str, created_at: datetime | None = None, key: bytes | None = None, iv: bytes | None = None) -> dict[str, Any]:
    """Encrypt the Display payload with AES-256-GCM."""
    actual_key = key if key is not None else secrets.token_bytes(DISPLAY_KEY_BYTES)
    actual_iv = iv if iv is not None else secrets.token_bytes(DISPLAY_IV_BYTES)
    if len(actual_key) != DISPLAY_KEY_BYTES:
        raise ValueError("display key must be 32 bytes")
    if len(actual_iv) != DISPLAY_IV_BYTES:
        raise ValueError("display IV must be 12 bytes")
    payload = create_display_payload(title=title, html=html, created_at=created_at)
    plaintext = serialize_display_payload(payload).encode("utf-8")
    data = AESGCM(actual_key).encrypt(actual_iv, plaintext, None)
    return {
        "alg": "AES-GCM",
        "keyFormat": "raw-base64",
        "key": base64.b64encode(actual_key).decode("ascii"),
        "iv": base64.b64encode(actual_iv).decode("ascii"),
        "data": base64.b64encode(data).decode("ascii"),
    }


def decrypt_display_box(box: dict[str, Any]) -> dict[str, Any]:
    """Decrypt and validate a Display box for tests and interoperability checks."""
    if box.get("alg") != "AES-GCM" or box.get("keyFormat") != "raw-base64":
        raise ValueError("invalid Display box constants")
    key = strict_b64decode(box.get("key"), "key")
    iv = strict_b64decode(box.get("iv"), "iv")
    data = strict_b64decode(box.get("data"), "data")
    if len(key) != DISPLAY_KEY_BYTES or len(iv) != DISPLAY_IV_BYTES or len(data) < AES_GCM_TAG_BYTES:
        raise ValueError("invalid Display box binary lengths")
    try:
        plaintext = AESGCM(key).decrypt(iv, data, None)
    except InvalidTag as exc:
        raise ValueError("Display box authentication failed") from exc
    payload = json.loads(plaintext.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Display payload must be object")
    if payload.get("v") != 1 or payload.get("type") != DISPLAY_PAYLOAD_TYPE:
        raise ValueError("invalid Display payload constants")
    return payload


def create_top_level_json(*, display_box: dict[str, Any], recovery_box: dict[str, Any]) -> dict[str, Any]:
    """Create the top-level Format v1 JSON object."""
    return {"format": RECOVERY_FORMAT, "formatVersion": 1, "display": display_box, "recovery": recovery_box}


def serialize_viewer_json(data: dict[str, Any]) -> str:
    """Serialize top-level JSON without duplicate keys generated by this tool."""
    required = {"format", "formatVersion", "display", "recovery"}
    if set(data) != required or data.get("format") != RECOVERY_FORMAT or data.get("formatVersion") != 1:
        raise ValueError("invalid top-level Restricted Viewer JSON")
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def escape_json_for_script(json_text: str) -> str:
    """Escape JSON text for safe application/json script text content."""
    return (json_text.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def render_template(*, title: str, viewer_json: dict[str, Any], template_path: Path = TEMPLATE_PATH) -> str:
    """Render the Restricted Viewer template using explicit placeholders."""
    try:
        template = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Restricted Viewer template is missing or unreadable: {template_path}") from exc
    replacements = {
        "__TITLE__": html.escape(title, quote=True),
        "__VIEWER_JSON__": escape_json_for_script(serialize_viewer_json(viewer_json)),
    }
    missing = [token for token in replacements if token not in template]
    if missing:
        raise RuntimeError(f"Restricted Viewer template missing placeholders: {', '.join(missing)}")
    rendered = template
    for token, value in replacements.items():
        rendered = rendered.replace(token, value, 1)
    if "__TITLE__" in rendered or "__VIEWER_JSON__" in rendered:
        raise RuntimeError("Restricted Viewer template contains duplicate placeholders")
    return rendered


def atomic_write_text(path: Path, text: str, *, overwrite: bool) -> None:
    """Write text via temporary file and atomic replacement."""
    if path.exists() and not overwrite:
        raise FileExistsError(f"output file already exists; use --overwrite to replace it: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent or Path('.')))
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        if path.exists() and not overwrite:
            raise FileExistsError(f"output file already exists; use --overwrite to replace it: {path}")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise


def estimated_viewer_size(images: list[ValidImage]) -> int:
    """Rough final Restricted Viewer size estimate."""
    markdown = estimated_markdown_size(images)
    display = markdown + 2048
    return int((markdown + display) * 1.45) + 12000

def estimated_base64_size(size_bytes: int) -> int:
    """Return the standard Base64 output length for a byte count."""
    return 4 * math.ceil(size_bytes / 3)


def estimated_markdown_size(images: list[ValidImage]) -> int:
    """Estimate Markdown byte size without materializing Base64 strings."""
    total = 1 if images else 0
    for image in images:
        total += len(f"## {heading_text(image.path)}\n\n![{alt_text(image.path)}](data:{MIME_TYPES[image.kind]};base64,)".encode("utf-8"))
        total += estimated_base64_size(image.size_bytes) + 2
    return total


def validate_input_dir(input_dir: Path) -> list[str]:
    """Validate the input directory path."""
    if not input_dir.exists():
        return [f"Input directory does not exist: {input_dir}"]
    if not input_dir.is_dir():
        return [f"Input path is not a directory: {input_dir}"]
    return []


def print_report(result: PipelineResult, *, dry_run: bool) -> None:
    """Print a human-readable processing report to stderr."""
    print(f"Target images: {len(result.valid_images)}", file=sys.stderr)
    print("Processing order:", file=sys.stderr)
    for index, image in enumerate(result.valid_images, start=1):
        print(
            f"  {index}. {image.path.name} ({image.kind}, {image.size_bytes} bytes, "
            f"estimated Base64 {estimated_base64_size(image.size_bytes)} bytes)",
            file=sys.stderr,
        )
    if result.skipped_images:
        print("Skipped files:", file=sys.stderr)
        for skipped in result.skipped_images:
            print(f"  - {skipped.path.name}: {skipped.reason}", file=sys.stderr)
    print(f"Source image total size: {sum(image.size_bytes for image in result.valid_images)} bytes", file=sys.stderr)
    print(f"Estimated Markdown size: {estimated_markdown_size(result.valid_images)} bytes", file=sys.stderr)
    print(f"Estimated Restricted Viewer size: {estimated_viewer_size(result.valid_images)} bytes", file=sys.stderr)
    if dry_run:
        print("Dry run completed: no encryption or files were written.", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""
    parser = build_parser()
    args = parser.parse_args(argv)

    errors = validate_input_dir(args.input_dir)
    if errors:
        for message in errors:
            print(f"error: {message}", file=sys.stderr)
        return EXIT_FATAL
    final_output = args.output is not None
    developer_output = args.emit_markdown is not None or args.emit_recovery_box is not None
    if args.recovery_password and not (final_output or args.emit_recovery_box is not None):
        print("error: --recovery-password requires -o/--output or --emit-recovery-box.", file=sys.stderr)
        return EXIT_FATAL
    if (final_output or args.emit_recovery_box is not None) and not args.recovery_password and not args.dry_run:
        print("error: Restricted Viewer and Recovery box output require --recovery-password.", file=sys.stderr)
        return EXIT_FATAL
    if final_output and args.output is not None and args.output.suffixes[-3:] != [".restricted", ".view", ".html"]:
        print("warning: recommended output extension is .restricted.view.html", file=sys.stderr)
    for output_path, label in ((args.emit_markdown, "Markdown output"), (args.emit_recovery_box, "Recovery box output"), (args.output, "Restricted Viewer output")):
        if output_path is not None and output_path.exists() and not args.overwrite and not args.dry_run:
            print(f"error: {label} file already exists; use --overwrite to replace it: {output_path}", file=sys.stderr)
            return EXIT_FATAL

    include_markdown = bool((developer_output or final_output) and not args.dry_run)
    try:
        result = process_input_images(args.input_dir, args.max_kb, include_markdown=include_markdown)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FATAL

    print_report(result, dry_run=args.dry_run)
    if args.output is not None:
        print(f"Planned output: {args.output}", file=sys.stderr)
    if args.warning_mb is not None:
        threshold = args.warning_mb * 1024 * 1024
        estimate = estimated_viewer_size(result.valid_images) if final_output else estimated_markdown_size(result.valid_images)
        if estimate > threshold:
            print(f"warning: estimated output size exceeds --warning-mb ({args.warning_mb} MiB).", file=sys.stderr)
        else:
            print(f"Warning threshold exceeded: no", file=sys.stderr)
    if args.dry_run:
        return EXIT_PARTIAL if result.skipped_images else EXIT_SUCCESS

    wrote_output = False
    if args.emit_markdown is not None:
        try:
            atomic_write_text(args.emit_markdown, result.markdown or "", overwrite=args.overwrite)
        except OSError as exc:
            print(f"error: cannot write Markdown output: {exc}", file=sys.stderr)
            return EXIT_FATAL
        wrote_output = True
        print(f"Wrote Phase 1 Markdown: {args.emit_markdown}", file=sys.stderr)

    password: str | None = None
    if final_output or args.emit_recovery_box is not None:
        try:
            password = prompt_recovery_password()
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return EXIT_FATAL

    if args.emit_recovery_box is not None:
        try:
            filename = recovery_filename_for_title(args.title)
            box = create_recovery_box(title=args.title or filename, filename=filename, markdown=result.markdown or "", password=password or "")
            atomic_write_text(args.emit_recovery_box, json.dumps(box, ensure_ascii=False, separators=(",", ":")) + "\n", overwrite=args.overwrite)
        except (ValueError, OSError) as exc:
            print(f"error: cannot write Recovery box output: {exc}", file=sys.stderr)
            return EXIT_FATAL
        wrote_output = True
        print(f"Wrote Phase 2 Recovery box: {args.emit_recovery_box}", file=sys.stderr)

    if final_output and args.output is not None:
        try:
            title = args.title or "Presentation"
            markdown = result.markdown or ""
            recovery = create_recovery_box(title=title, filename=recovery_filename_for_title(args.title), markdown=markdown, password=password or "")
            display_html = generate_display_html(result.valid_images)
            display = create_display_box(title=title, html=display_html)
            document = render_template(title=title, viewer_json=create_top_level_json(display_box=display, recovery_box=recovery))
            atomic_write_text(args.output, document, overwrite=args.overwrite)
            final_size = args.output.stat().st_size
        except (ValueError, RuntimeError, OSError) as exc:
            print(f"error: cannot write Restricted Viewer HTML: {exc}", file=sys.stderr)
            return EXIT_FATAL
        wrote_output = True
        print(f"Wrote Restricted Viewer HTML: {args.output}", file=sys.stderr)
        print(f"Final output size: {final_size} bytes", file=sys.stderr)
        if args.warning_mb is not None and final_size > args.warning_mb * 1024 * 1024:
            print(f"warning: final output size exceeds --warning-mb ({args.warning_mb} MiB).", file=sys.stderr)

    if not wrote_output:
        print("No output was generated. Use -o/--output, --emit-markdown, --emit-recovery-box, or --dry-run.", file=sys.stderr)
        return EXIT_FATAL
    return EXIT_PARTIAL if result.skipped_images else EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
