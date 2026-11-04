# PDF Text Replacement Tool

A command-line utility for replacing text in a PDF while creating a new file and leaving the source unchanged.

When the font is embedded in the PDF, the replacement preserves:

- font family and variant;
- font size;
- bold and italic styling;
- color;
- baseline and cardinal text orientation.

If the original font is not embedded, the script uses a standard PDF font that matches the available characteristics (serif/sans-serif/monospaced, regular/bold/italic).

## Requirements

- Python 3.10 or later
- PyMuPDF

```bash
pip install pymupdf
```

## Usage

```bash
python pdf_replace.py "TEXT_TO_FIND" "REPLACEMENT_TEXT" "source.pdf" "destination.pdf"
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
5. Inserts the replacement on the original baseline using the detected size, color, and orientation.
6. Saves the result as a new PDF; the source and destination paths cannot be the same.

## Notes

- If the replacement is much longer than the original text, it may overlap other elements. The font size is intentionally preserved to maintain the source formatting.
- PyMuPDF text matching is case-insensitive.
- If an occurrence contains multiple styles, the script preserves the style of the span that covers most of it.

## License

MIT
