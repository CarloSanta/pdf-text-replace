import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass
class TextStyle:
    font: str = "Helvetica"
    size: float = 10.0
    color: tuple = (0.0, 0.0, 0.0)
    flags: int = 0
    baseline: float | None = None
    direction: tuple = (1.0, 0.0)


@dataclass
class FontResource:
    name: str
    font: fitz.Font


def _normalise_font_name(name):
    """Remove a PDF subset prefix and punctuation used only as separators."""
    name = (name or "").split("+", 1)[-1]
    return "".join(char.lower() for char in name if char.isalnum())


def _intersection_area(first, second):
    intersection = fitz.Rect(first) & fitz.Rect(second)
    return max(0.0, intersection.width) * max(0.0, intersection.height)


def _style_for_match(page, match_rect):
    """Return the style of the span that covers most of a search result."""
    best_style = TextStyle()
    best_area = -1.0

    for block in page.get_text("dict").get("blocks", []):
        for line in block.get("lines", []):
            direction = tuple(line.get("dir", (1.0, 0.0)))
            for span in line.get("spans", []):
                if not span.get("text"):
                    continue
                area = _intersection_area(span["bbox"], match_rect)
                if area <= best_area:
                    continue
                best_area = area
                best_style = TextStyle(
                    font=span.get("font", "Helvetica"),
                    size=float(span.get("size", 10.0)),
                    color=fitz.sRGB_to_pdf(span.get("color", 0)),
                    flags=int(span.get("flags", 0)),
                    baseline=float(span.get("origin", (0.0, match_rect.y1))[1]),
                    direction=direction,
                )

    return best_style


def _base14_font_for_style(style):
    """Choose a styled built-in fallback when the original font is not embedded."""
    bold = bool(style.flags & fitz.TEXT_FONT_BOLD)
    italic = bool(style.flags & fitz.TEXT_FONT_ITALIC)
    serif = bool(style.flags & fitz.TEXT_FONT_SERIFED)
    mono = bool(style.flags & fitz.TEXT_FONT_MONOSPACED)
    family = "cour" if mono else "tiro" if serif else "helv"
    variants = {
        (False, False): family,
        (True, False): {"cour": "cobo", "tiro": "tibo", "helv": "hebo"}[family],
        (False, True): {"cour": "coit", "tiro": "tiit", "helv": "heit"}[family],
        (True, True): {"cour": "cobi", "tiro": "tibi", "helv": "hebi"}[family],
    }
    return variants[(bold, italic)]


def _font_resource_for_style(doc, page, style, cache):
    """Register a font and return its page resource plus a measuring font."""
    key = _normalise_font_name(style.font)
    if key in cache:
        return cache[key]

    candidates = []
    for font in page.get_fonts(full=True):
        xref, _ext, _type, basefont, resource_name = font[:5]
        base_key = _normalise_font_name(basefont)
        if key == base_key:
            candidates.append((0, xref, resource_name))
        elif key and (key in base_key or base_key in key):
            candidates.append((1, xref, resource_name))

    # An exact family+variant match must win over a partial family match:
    # e.g. DejaVuSansCondensed-Bold must not resolve to DejaVuSansCondensed.
    for _score, xref, _resource_name in sorted(candidates):
        try:
            _name, _ext, _type, font_buffer = doc.extract_font(xref)
            if font_buffer:
                resource = f"RPL{len(cache) + 1}"
                page.insert_font(fontname=resource, fontbuffer=font_buffer)
                cached = FontResource(
                    resource, fitz.Font(fontbuffer=font_buffer)
                )
                cache[key] = cached
                return cached
        except (RuntimeError, ValueError):
            pass

    fallback = _base14_font_for_style(style)
    cached = FontResource(fallback, fitz.Font(fontname=fallback))
    cache[key] = cached
    print(
        f"Warning: font '{style.font}' is not embedded; using '{fallback}' as fallback.",
        file=sys.stderr,
    )
    return cached


def _rotation_for_direction(direction):
    x, y = direction
    cardinal = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}
    rounded = (round(x), round(y))
    if abs(x - rounded[0]) < 0.01 and abs(y - rounded[1]) < 0.01:
        return cardinal.get(rounded, 0)
    return 0


def _insertion_point(match_rect, style, rotation, text_length, alignment):
    """Place replacement on its original baseline and align it in the old width."""
    baseline = style.baseline
    available_length = (
        match_rect.height if rotation in (90, 270) else match_rect.width
    )
    offset = (available_length - text_length) / 2 if alignment == "center" else 0

    if rotation == 90:
        return fitz.Point(match_rect.x0, match_rect.y1 - offset)
    if rotation == 180:
        return fitz.Point(match_rect.x1 - offset, baseline or match_rect.y0)
    if rotation == 270:
        return fitz.Point(match_rect.x1, match_rect.y0 + offset)
    return fitz.Point(match_rect.x0 + offset, baseline or match_rect.y1)


def replace_text_in_pdf(
    source_path,
    destination_path,
    search_str,
    replace_str,
    alignment="center",
):
    """Create a new PDF with matching text replaced and its style preserved."""
    source_path = Path(source_path).resolve()
    destination_path = Path(destination_path).resolve()

    if source_path == destination_path:
        raise ValueError("Source and destination must be different files.")
    if not source_path.is_file() or source_path.suffix.lower() != ".pdf":
        raise ValueError(f"Invalid source PDF: {source_path}")
    if destination_path.suffix.lower() != ".pdf":
        raise ValueError("The destination file must have a .pdf extension.")
    if alignment not in {"center", "left"}:
        raise ValueError("Alignment must be 'center' or 'left'.")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(source_path)
    changed = False
    replacement_count = 0

    try:
        for page in doc:
            matches = page.search_for(search_str)
            if not matches:
                continue

            changed = True
            replacements = []
            font_cache = {}

            # Capture styling before redaction changes the page text layer.
            for match in matches:
                style = _style_for_match(page, match)
                replacements.append((fitz.Rect(match), style))
                page.add_redact_annot(match, fill=(1, 1, 1))

            # Keep images and vector graphics intact while removing only text.
            page.apply_redactions(images=0, graphics=0, text=0)

            for match, style in replacements:
                font_resource = _font_resource_for_style(
                    doc, page, style, font_cache
                )
                rotation = _rotation_for_direction(style.direction)
                text_length = font_resource.font.text_length(
                    replace_str, fontsize=style.size
                )
                page.insert_text(
                    _insertion_point(
                        match,
                        style,
                        rotation,
                        text_length,
                        alignment,
                    ),
                    replace_str,
                    fontsize=style.size,
                    fontname=font_resource.name,
                    color=style.color,
                    rotate=rotation,
                    overlay=True,
                )
                replacement_count += 1

        if not changed:
            print(f"No matches found in: {source_path}")
            return False

        # Garbage collection removes the redacted text from the saved file.
        doc.save(destination_path, garbage=4, deflate=True)
    finally:
        doc.close()

    suffix = "s" if replacement_count != 1 else ""
    print(f"Created: {destination_path} ({replacement_count} replacement{suffix})")
    return True


def _default_destination(source):
    source = Path(source)
    return source.with_name(f"{source.stem}_replaced.pdf")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Replace text in a source PDF, preserve its font styling, and write "
            "the result to a separate destination PDF."
        )
    )
    parser.add_argument("search", help="Text to search for")
    parser.add_argument("replace", help="Replacement text")
    parser.add_argument("source", help="Source PDF (never modified)")
    parser.add_argument(
        "destination",
        nargs="?",
        help="Destination PDF (default: SOURCE_replaced.pdf)",
    )
    parser.add_argument(
        "--align",
        choices=("center", "left"),
        default="center",
        help=(
            "Align replacement within the removed text width "
            "(default: center; use left for the previous behavior)"
        ),
    )
    args = parser.parse_args()

    destination = args.destination or _default_destination(args.source)
    try:
        changed = replace_text_in_pdf(
            args.source,
            destination,
            args.search,
            args.replace,
            alignment=args.align,
        )
    except (ValueError, OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0 if changed else 2


if __name__ == "__main__":
    raise SystemExit(main())
