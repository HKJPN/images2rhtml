# Security Notes

## Restricted Viewer Is Not DRM

MD//WORKS Restricted Viewer Format v1 can discourage ordinary copying, selection, dragging, context menus, and printing, but it cannot prevent screenshots, camera capture, browser developer tools, memory inspection, or HTML/runtime modification.

## Display Data Is Not Confidential

The Display box AES key is stored inside the generated HTML. Display encryption avoids leaving display HTML as obvious plaintext in the source, but it does not hide content from a determined viewer.

## Recovery Data Depends on Password Strength

The Recovery payload is encrypted with AES-256-GCM using a key derived from the recovery password via PBKDF2-HMAC-SHA256. Weak passwords remain vulnerable to offline guessing. Users should choose long, non-reused passphrases and store them safely.

## Password Handling Requirements

The generator must pass the exact password string to UTF-8 encoding and PBKDF2. It must not:

- trim whitespace
- add or remove newlines
- change case
- apply Unicode normalization
- replace similar characters
- convert full-width or half-width characters

## Markdown Preservation

The generator should not automatically Unicode-normalize Markdown before storing it in the Recovery payload. Compatibility tests may compare NFC-normalized text separately from byte-for-byte preservation.

## Cryptography Implementation

Do not implement AES, GCM, PBKDF2, or random generation manually. Use reviewed library functionality from `cryptography` and Python's standard secure randomness APIs as appropriate.

## Repository Hygiene

Do not commit real passwords, secrets, private documents, or sensitive source images. Samples must use harmless dummy data only.
