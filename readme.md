# images2rhtml

[🇺🇸 English](readme.md) or [🇯🇵 日本語](readme-ja.md)
<img width="1280" height="720" alt="プレゼンテーション1" src="https://github.com/user-attachments/assets/a5279906-2db3-4e67-9a60-9e645ae6e726" />

 **What is images2rHTML.py?**
 A Python CLI tool that compiles multiple images from a folder into a single "Restricted Viewer HTML" file with an Outline (table of contents).
 **Key Features**
 * **Viewing Restrictions and Protection:** The generated HTML can be viewed directly in a standalone browser. It restricts user actions such as text selection, copying, right-clicking, image dragging, and printing.
 * **Data Recovery and Re-editing:** By using the "Recovery password" set during generation, you can restore the original Markdown in [MD//WORKS](https://github.com/HKJPN/markdown-editor), allowing you to modify headings or add/remove images.
 * **Support for Large Files:** Since it operates via the command line, there is practically no limit to the file generation size. It is ideal for bundling a massive amount of image files. (*Note: The GUI-based [MD//WORKS](https://github.com/HKJPN/markdown-editor) has a similar feature, but with a file size limit of approximately 50MB.*)
`images2rHTML.py` is a Python CLI tool that compiles multiple images from a folder into a single **Restricted Viewer HTML** file, complete with a navigable Outline (Table of Contents).

```text
Image Folder
    ↓
images2rHTML.py
    ↓
Restricted Viewer HTML (with Outline)
    ↓
Distribute and View in Browser

[When editing is needed]
    ↓
Enter Recovery password in MD//WORKS
    ↓
Restore original Markdown & Re-edit

```

> ⚠️ **IMPORTANT: Restricted Viewer is NOT DRM.**
> It is designed to deter casual copying, printing, dragging, and unintended edits. It cannot completely prevent users from capturing the content via screenshots, screen recordings, browser developer tools, or advanced HTML parsing.

---

## ✨ Key Features

* Combines PNG, JPEG, and WebP images into a single HTML file.
* Sorts files using "Natural Sort Order" (e.g., Slide1, Slide2, Slide10).
* Automatically generates headings based on image filenames.
* Includes a clickable Outline for quick navigation between images.
* Embeds images directly into the HTML using Base64 encoding.
* Creates a single standalone HTML file for easy offline viewing.
* Restricts text selection, copying, right-clicking, dragging, and printing.
* Encrypts and securely stores the original Markdown data using a Recovery password.
* Allows restoration and re-editing of the Markdown via MD//WORKS.
* Never modifies or deletes your original image files.
* Operates 100% offline (no external server communication).
* Uses atomic saving to prevent incomplete or corrupted files if the process fails mid-way.

---

## 🛠️ Prerequisites

* **Python 3.11 or higher**
* The Python package **`cryptography`**
* The `images2rHTML.py` script and its dedicated HTML template.

### Installing `cryptography`

Open Windows PowerShell or a macOS/Linux Terminal and run the following command:

```bash
python -m pip install cryptography

```

*(If you have multiple versions of Python on Windows, try `py -m pip install cryptography` instead.)*

**To verify the installation:**

```bash
python -c "import cryptography; print(cryptography.__version__)"

```

If you see an error saying `ModuleNotFoundError: No module named 'cryptography'`, the package is not installed in the Python environment you are currently using.

### Supported Environments

* **Creation:** Windows, macOS, Linux, or any environment where Python and `cryptography` can run. (Note: `images2rHTML.py` cannot be run on an iPad, but you can create Restricted Viewer HTML files directly within the MD//WORKS app on an iPad).
* **Viewing:** Chrome, Edge, Firefox, Brave, Safari, and any modern browser that supports the Web Crypto API. Viewers can easily open the files on computers, tablets, and iPads.

---

## ⚠️ Keep the `templates` Folder Intact

`images2rHTML.py` relies on the following HTML template to work:
`templates/restricted-viewer-v1.html`

Please maintain the following directory structure:

```text
📂 images2rhtml
├── 📄 images2rHTML.py
└── 📂 templates
    └── 📄 restricted-viewer-v1.html

```

> **If you move `images2rHTML.py` to another folder without the `templates` folder, it will fail to generate the Restricted Viewer.** Keep them together exactly as they are configured.

To check if the template is in the right place (Windows PowerShell):

```powershell
Test-Path .\templates\restricted-viewer-v1.html

```

If it returns `True`, the template is correctly located.

---

## 🚀 Basic Usage

### 1. Prepare Your Working Directory

For this example, let's assume the following structure:

```text
📂 work
├── 📂 tools
│   └── 📂 images2rhtml
│       ├── 📄 images2rHTML.py
│       └── 📂 templates
│           └── 📄 restricted-viewer-v1.html
│
└── 📂 slides
    ├── 🖼️ Slide1.JPG
    ├── 🖼️ Slide2.JPG
    ├── 🖼️ Slide10.JPG
    └── ...

```

### 2. Open Your Command Line

**🪟 Windows**
Open your working folder in File Explorer. Click an empty space in the address bar at the top, type `powershell`, and press Enter. This will open PowerShell in that exact location.

**🍎 macOS**
Open "Terminal" via Spotlight. Type `cd ` (c-d-space), drag and drop your working folder into the Terminal window, and press Enter to navigate to that location.

### 3. Run the Command

**Example for Windows PowerShell:**

```powershell
python .\tools\images2rhtml\images2rHTML.py .\slides `
  -o .\presentation.restricted.view.html `
  --title "Presentation" `
  --recovery-password

```

*(You can also run it all on a single line without the ``` backticks).*

**Example for macOS/Linux:**

```bash
python3 ./tools/images2rhtml/images2rHTML.py ./slides \
  -o ./presentation.restricted.view.html \
  --title "Presentation" \
  --recovery-password

```

### 4. Enter the Recovery Password

After running the command, you will be prompted:

```text
Recovery password:
Confirm recovery password:

```

Type your password twice and press Enter.

> 💡 **The password is invisible!** When typing, no characters or asterisks (●) will appear on the screen. This is normal security behavior. Just type and press Enter.
> 
> 💡 **This password is NOT for viewing.** Viewers do not need a password to open the HTML file. The Recovery password is strictly for the author/editor to restore and edit the original Markdown later in MD//WORKS.
> 
> ⚠️ **Keep it safe:** If you lose this Recovery password, you will not be able to restore the encrypted Markdown data.

*Note: The Recovery password is strictly case-sensitive and distinguishes between spaces, symbols, and double-byte/single-byte characters.*

### 5. Check the Output

If successful, you will see a message like this:

```text
Wrote Restricted Viewer HTML: presentation.restricted.view.html
Final output size: 21682497 bytes

```

The file will be saved in the folder where you ran the command.

---

## 📖 How to Use the Viewer

Simply double-click the generated `.restricted.view.html` file, or drag and drop it into a web browser.

**Features of the Viewer:**

* Navigate to specific images using the Outline (sidebar) on the left.
* Toggle the Outline open or closed.
* Responsive design for PCs, tablets, and smartphones.
* Restricts text selection, copying, and cutting.
* Disables the right-click menu.
* Prevents dragging and dropping of images.
* Deters standard printing operations.

Viewers can review the presentation seamlessly in their browser, without needing PowerPoint or Markdown editors.

---

## ⚙️ Options

**Basic Syntax:**
`python images2rHTML.py INPUT_DIR [options]`

| Option | Description | Default |
| --- | --- | --- |
| `INPUT_DIR` | The folder containing your input images. | **Required** |
| `-o FILE` / `--output FILE` | Destination path for the generated HTML. | Prompts during generation |
| `--title "TITLE"` | The document title displayed at the top of the Viewer. | `Presentation` |
| `--recovery-password` | Prompts for the Recovery password securely. (Do not write the actual password in the command line). | Prompts during generation |
| `--max-kb NUMBER` | Max file size per image (in KiB). Larger images are skipped. | `300` KiB |
| `--warning-mb NUMBER` | Warns if the estimated HTML size exceeds this limit. (Generation continues anyway). | `20` MiB |
| `--overwrite` | Force overwrite if a file with the same name exists. | Disabled |
| `--dry-run` | Simulates the process to check file sizes, skip reasons, and ordering without writing any files or asking for a password. | Disabled |
| `--version` | Display the tool's version. | - |
| `-h`, `--help` | Show the help screen. | - |

*(You can run `python images2rHTML.py --help` to see all available options).*

### A Note on Size Units

Although the flags use `KB` and `MB`, the script calculates limits using exact computer units (KiB / MiB).

* `300 KiB` = 300 × 1024 = 307,200 bytes
* `20 MiB` = 20 × 1024 × 1024 = 20,971,520 bytes

---

## 🚦 Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | **Success:** All images processed and file written successfully. |
| `1` | **Fatal Error:** Check your input folder, template path, password matching, arguments, or write permissions. |
| `2` | **Completed with Skips:** Output was successful, but one or more images were skipped (check the console for reasons). |

---

## 🔍 Simulation Mode: `--dry-run`

You can check estimated file sizes and processing order before actually creating the file.

```powershell
python .\tools\images2rhtml\images2rHTML.py .\slides -o .\presentation.html --title "Presentation" --dry-run

```

**`--dry-run` shows you:** Target image count, natural sort order, formats, individual file sizes, reasons for any skipped images, total original size, estimated Markdown size, and estimated final HTML size. It does not create files or ask for a password.

---

## 📂 Supported Images and Ordering

* **Supported formats:** `.png`, `.jpg`, `.jpeg`, `.webp` (Case-insensitive). The tool verifies basic file signatures, not just extensions. Mismatched extensions, empty files, or corrupted files are skipped.
* **Search scope:** It only scans the root of the provided input folder. It does not recursively scan subfolders.
* **Natural Order:** `Slide1` -> `Slide2` -> `Slide10`. It reads numbers intelligently so your slides stay in the correct presentation sequence. Headings are automatically created from the filenames (e.g., `Slide1.JPG` becomes `## Slide1`).

---

## 📦 File Size and Performance Guidelines

The final HTML file will be significantly larger than the sum of your original images. This is normal, as it contains both the display data for the Viewer and the encrypted Markdown data for recovery.

**Benchmark Example:**

* 44 Images (Original total: ~6.1 MB) -> Generated HTML: **~21.7 MB**

**Performance Guidelines:**

* **Viewing:** Fast and smooth across all tested browsers and devices.
* **Restoring/Editing in MD//WORKS:**
* **~20 images:** Very smooth, even on older PCs and iPads.
* **40+ images images:** Viewing is fine, but restoring the Markdown inside MD//WORKS may take 15–30 seconds on older devices and editing may feel slightly sluggish. Consider splitting massive presentations into "Part 1" and "Part 2".


---

## 🔓 Restoring Markdown via MD//WORKS

The generated HTML securely stores your original Markdown using AES-GCM encryption.

**How to restore:**

1. Open [MD//WORKS](https://github.com/HKJPN/markdown-editor).
2. Go to `File` → `Open` and select your `.restricted.view.html` file.
3. Enter the Recovery password you set during creation.
4. The Markdown is restored! You can now edit text, change headings, or adjust images.
5. Save it as standard Markdown or export a fresh Viewer HTML.

*(Note: The Viewer HTML itself does not have a "restore" button. Restoration must be done through MD//WORKS).*

---

## 🔐 Security and Limitations

* **Offline Processing:** No data is sent to external servers. Original files are untouched.
* **Password Handling:** Passwords are used to derive an encryption key. No automatic Unicode normalization is applied, meaning uppercase/lowercase, spaces, and half-width/full-width characters must match perfectly. The password itself is never saved in the HTML.
* **Display Data:** The data meant for browser viewing is accessible within the HTML structure. Restricted Viewer deters casual copying, but it does not encrypt the visible display data against technical extraction.
* **Recovery Data:** The underlying Markdown meant for MD//WORKS is heavily encrypted via AES-GCM and cannot be extracted without the password.
* **What it deters:** Unintended text selection, casual copy/paste, standard printing, right-clicking, image dragging, and accidental modifications by the viewer.
* **What it CANNOT prevent:** Screenshots, camera photos of the screen, browser Developer Tools extraction, raw HTML parsing. Do not rely solely on this tool for strict legal DRM or highly confidential trade secrets. Consider using tools equipped with encryption features, such as MD//WORKS.

---

## 🧯 Troubleshooting

**`No module named 'cryptography'`**
You haven't installed the cryptography package in your current Python environment. Run `python -m pip install cryptography`. If you use Windows and have multiple Python versions, try `py -m pip install cryptography`.

**Error: `externally-managed-environment` (macOS / Linux)**
Modern macOS/Linux environments may block standard pip installs. Add the `--break-system-packages` flag:

```bash
python3 -m pip install cryptography --break-system-packages

```

**`Restricted Viewer template is missing or unreadable`**
You moved `images2rHTML.py` without taking the `templates` folder with it. Make sure `templates/restricted-viewer-v1.html` exists in the exact same directory structure as the script.

**I can't type my Recovery password!**
The password is intentionally invisible for security. Keep typing and press Enter.

**MD//WORKS won't restore my file**
Ensure your Recovery password is an exact match (case, spaces, symbols). If the password is lost, the Markdown cannot be recovered.

**Output file already exists**
Use the `--overwrite` flag to replace the existing file.

**Some images were skipped**
Often due to exceeding the `--max-kb` limit (default 300 KiB). You can increase this limit (e.g., `--max-kb 500`), but it will increase the final HTML size.

---

## 🔄 Comparing `images2rHTML.py` vs `images2md.py`

| Tool | Output Format | Best Used For... |
| --- | --- | --- |
| `images2md.py` | Markdown | Converting images to Markdown so you can add heavy text, PDFs, or meeting minutes. |
| `images2rHTML.py` | Restricted Viewer HTML | Distributing slide decks instantly while deterring casual copying, printing, and modification. |
| MD//WORKS | Markdown / Viewer | Deep editing, restoring restricted files, and managing various Markdown exports. |

**Workflow 1: Edit, then distribute**
`Images` -> `images2md.py` -> `Edit in MD//WORKS` -> `Export as Restricted Viewer`

**Workflow 2: Distribute instantly**
`Images` -> `images2rHTML.py` -> `Share Restricted Viewer`

---

## 🚧 Unimplemented Features

The following features are not supported in the current version:

* Image resizing or recompression
* Adjusting JPEG quality or auto-converting formats (e.g., PNG to JPEG)
* EXIF data removal/modification
* OCR (Optical Character Recognition)
* Direct import from `.pptx` or `.pdf` files (export to images first)
* Recursive subfolder scanning
* Embedding videos or PDFs inside the Viewer
* Restoring or editing Markdown *directly inside* the Viewer
* Password recovery / Resetting a forgotten password
* Graphical User Interface (GUI) or Drag-and-Drop app window
* External server communication / Auto-updates
* 100% Screenshot prevention / True DRM
* A standalone script that doesn't require the `templates` folder

*(Development/Testing Options like `--emit-markdown` and `--emit-recovery-box` are available but not needed for standard use).*

---

## 📄 License

MIT License
