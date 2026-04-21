# PDF Text Replacement Tool

A simple, generic command-line utility to search and replace text strings within PDF files. 

This tool uses the **PyMuPDF** library to identify text locations, redact (remove) the original text, and overlay new text in the same position while attempting to maintain the original font size.

## Features
- **Redaction-based replacement:** Properly removes old text rather than just covering it.
- **Font Size Detection:** Scans the original document to match the font size of the replacement text.
- **Batch Processing:** Can process individual files, a list of files, or entire directories.
- **Standard PDF Fonts:** Uses standard Helvetica to ensure maximum compatibility without external font files.

## Prerequisites

You must have **Python 3** installed and the **PyMuPDF** library:

```bash
pip install pymupdf
```

## Installation

Simply copy `pdf_replace.py` to your desired working directory.

## Usage

Run the script using the following syntax:

```bash
python pdf_replace.py "SEARCH_STRING" "REPLACE_STRING" "PATH_TO_FILES_OR_DIRS"
```

### Examples

**1. Replace text in a specific file:**
```bash
python pdf_replace.py "Old Text" "New Text" "example.pdf"
```

**2. Replace text in all PDF files in the current folder:**
```bash
python pdf_replace.py "old text" "new text" "."
```

**3. Replace text across multiple paths:**
```bash
python pdf_replace.py "OLD TEXT" "NEW TEXT" "dir1/" "dir2/example.pdf"
```

## How it Works
1. **Search:** The script locates all occurrences of the search string on every page.
2. **Analysis:** It inspects the surrounding text blocks to determine the original font size.
3. **Redaction:** It creates a redaction annotation over the original text, effectively "whiting it out."
4. **Insertion:** It inserts the new string at the exact same coordinates (X, Y) using the detected font size.
5. **Safe Save:** It saves to a temporary file first, then replaces the original to prevent data loss in case of a crash.

## Troubleshooting
- **Permission Errors:** If you receive a "Permission Denied" error, ensure the PDF file is not open in another application (like Adobe Acrobat or Chrome).
- **Complex Layouts:** In some highly complex or layered PDFs, the text extraction may vary. Always keep a backup of your original files before running batch replacements.

## License
MIT
