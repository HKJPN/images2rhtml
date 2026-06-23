# MD//WORKS Compatibility Notes

This document summarizes compatibility-critical requirements extracted from `docs/restricted-viewer-format-v1.md`. The source specification remains authoritative.

## Target

- Format identifier: `mdworks-restricted-viewer`
- Format version: `1`
- Initial reader target: MD//WORKS v1.5.7
- `images2rHTML.py` target profile: Full Restricted Viewer Generator and Single-File Restricted Viewer Generator

## HTML Container

- The HTML file must be UTF-8 and include `<meta charset="utf-8">`.
- The Restricted Viewer JSON must be stored in exactly one `<script>` element with:
  - `id="mdworks-restricted-viewer-box"`
  - `type="application/json"`
- Recommended metadata:
  - `mdworks-viewer-format = mdworks-restricted-viewer`
  - `mdworks-viewer-format-version = 1`

## Top-Level JSON

Required object fields:

```json
{
  "format": "mdworks-restricted-viewer",
  "formatVersion": 1,
  "display": {},
  "recovery": {}
}
```

Generators must not emit duplicate keys. Readers should ignore unknown fields where possible.

## Display Box

Required fields and constants:

- `alg`: `AES-GCM`
- `keyFormat`: `raw-base64`
- `key`: standard Base64 of a 32-byte raw key
- `iv`: standard Base64 of a 12-byte IV
- `data`: standard Base64 of ciphertext followed by a 128-bit authentication tag
- AAD: none
- Plaintext encoding: UTF-8 JSON

The display key is stored in the HTML, so this box is not a confidentiality boundary.

## Display Payload

Required fields:

- `v`: `1`
- `type`: `mdworks-restricted-viewer-display`
- `title`: viewer title string
- `createdAt`: ISO 8601 timestamp, preferably `YYYY-MM-DDTHH:mm:ss.sssZ`
- `html`: sanitized display HTML string

Display HTML must not contain executable or unsafe content such as scripts, iframes, event handler attributes, or `javascript:` URLs.

## Recovery Box

Required fields and constants:

- `v`: `1`
- `label`: `restricted-viewer-recovery`
- `alg`: `AES-GCM`
- `kdf`: `PBKDF2`
- `hash`: `SHA-256`
- `iterations`: `310000`
- `salt`: standard Base64 of 16 random bytes
- `iv`: standard Base64 of 12 random bytes
- `data`: standard Base64 of ciphertext followed by a 128-bit authentication tag

## Recovery Key Derivation

- Password encoding: UTF-8
- Password preprocessing: none
- KDF: PBKDF2-HMAC-SHA256
- Iterations: 310,000
- Salt length: 16 bytes
- Derived key length: 32 bytes
- Resulting encryption: AES-256-GCM

Passwords must not be trimmed, normalized, case-converted, or otherwise changed before key derivation.

## Recovery Payload

Required fields:

- `v`: `1`
- `type`: `mdworks-restricted-viewer-recovery`
- `title`: source document title
- `filename`: recovery Markdown filename, normally ending in `.md`
- `createdAt`: generation timestamp
- `format`: `mdworks-restricted-viewer`
- `markdown`: full Markdown string

Source Markdown should be preserved without automatic Unicode normalization before encryption.

## Base64

Use RFC 4648 standard Base64 with `+`, `/`, and retained `=` padding. Do not use Base64URL.

## Safe JSON Embedding

Before embedding JSON into a `<script>` element, escape at least:

- `<` as `\u003c`
- `>` as `\u003e`
- `&` as `\u0026`
- U+2028 as `\u2028`
- U+2029 as `\u2029`
