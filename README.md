# PDF Text Replacement Tool

A command-line utility for replacing text in a PDF while creating a new file and leaving the source unchanged.

When the font is embedded in the PDF, the replacement preserves:

- font family and variant;
- font size;
- bold and italic styling;
- color;
- baseline and cardinal text orientation.

By default, replacement text is centered within the width occupied by the
original text. Use `--align left` to retain the previous left-aligned behavior.

If the original font is not embedded, the script uses a standard PDF font that matches the available characteristics (serif/sans-serif/monospaced, regular/bold/italic).

## Requirements

- Python 3.10 or later
- PyMuPDF

### Installing PyMuPDF

Install PyMuPDF through the same Python interpreter that you will use to run
the script. Using `python -m pip` avoids installing the package into a different
Python environment by mistake:

```bash
python -m pip install --upgrade pip
python -m pip install pymupdf
```

To keep the dependency isolated, you can create a virtual environment first.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pymupdf
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pymupdf
```

Verify that PyMuPDF is available to the active interpreter:

```bash
python -c "import fitz; print(fitz.__doc__)"
```

PyMuPDF is installed with the package name `pymupdf`, while this script imports
it as `fitz`. If `python3 pdf_replace.py ...` reports `ModuleNotFoundError: No
module named 'fitz'`, install the package specifically for that interpreter:

```bash
python3 -m pip install pymupdf
```

## Usage

```bash
python pdf_replace.py "TEXT_TO_FIND" "REPLACEMENT_TEXT" "source.pdf" "destination.pdf"
```

To align the replacement to the original text's starting edge:

```bash
python pdf_replace.py "TEXT_TO_FIND" "REPLACEMENT_TEXT" "source.pdf" --align left
```

The destination file is optional. If omitted, it is automatically created next to the source file with the `_replaced` suffix:

```bash
python pdf_replace.py "Mario Rossi" "Luigi Bianchi" "document.pdf"
```

This example creates `document_replaced.pdf` and leaves `document.pdf` unchanged.

## How It Works

1. Searches every page for all occurrences of the specified text.
2. Identifies the text span that covers each occurrence.
3. Extracts and registers the font embedded in the PDF, including its bold/italic variant.
4. Removes only the original text through redaction while preserving images and vector graphics.
5. Inserts the replacement on the original baseline using the detected size, color, and orientation, centered within the original text width by default.
6. Saves the result as a new PDF; the source and destination paths cannot be the same.

## Notes

- If the replacement is much longer than the original text, it may overlap other elements. The font size is intentionally preserved to maintain the source formatting.
- PyMuPDF text matching is case-insensitive.
- If an occurrence contains multiple styles, the script preserves the style of the span that covers most of it.

## License

MIT
