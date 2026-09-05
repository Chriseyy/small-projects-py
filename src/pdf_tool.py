from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter


def parse_page_selection(selection: str, page_count: int) -> list[int]:
    """Parse a 1-based selection such as ``1,3-5,8``."""
    if page_count < 1:
        raise ValueError("The PDF must contain at least one page.")

    pages: list[int] = []
    for part in selection.replace(" ", "").split(","):
        if not part:
            raise ValueError("Page selections cannot contain empty items.")
        if "-" in part:
            bounds = part.split("-")
            if len(bounds) != 2 or not all(bound.isdigit() for bound in bounds):
                raise ValueError(f"Invalid page range: {part}")
            start, end = (int(bound) for bound in bounds)
            if start > end:
                raise ValueError(f"Page range must be ascending: {part}")
            pages.extend(range(start, end + 1))
        elif part.isdigit():
            pages.append(int(part))
        else:
            raise ValueError(f"Invalid page selection: {part}")

    if any(page < 1 or page > page_count for page in pages):
        raise ValueError(f"Pages must be between 1 and {page_count}.")
    if len(set(pages)) != len(pages):
        raise ValueError("A page may only appear once in a selection.")
    return pages


def _reader(input_path: str | Path) -> PdfReader:
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")
    return PdfReader(path)


def _write(writer: PdfWriter, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as output_file:
        writer.write(output_file)
    return path


def _add_pages(writer: PdfWriter, reader: PdfReader, page_numbers: Iterable[int]) -> None:
    for page_number in page_numbers:
        writer.add_page(reader.pages[page_number - 1])


def merge_pdfs(input_paths: Iterable[str | Path], output_path: str | Path) -> Path:
    paths = [Path(path) for path in input_paths]
    if not paths:
        raise ValueError("At least one input PDF is required.")
    writer = PdfWriter()
    for path in paths:
        reader = _reader(path)
        for page in reader.pages:
            writer.add_page(page)
    return _write(writer, output_path)


def extract_pages(
    input_path: str | Path, pages: Iterable[int], output_path: str | Path
) -> Path:
    reader = _reader(input_path)
    page_numbers = list(pages)
    _validate_pages(page_numbers, len(reader.pages))
    writer = PdfWriter()
    _add_pages(writer, reader, page_numbers)
    return _write(writer, output_path)


def split_pdf(
    input_path: str | Path,
    split_points: Iterable[int],
    output_dir: str | Path,
) -> list[Path]:
    reader = _reader(input_path)
    total_pages = len(reader.pages)
    points = sorted(set(split_points))
    if any(point < 1 or point >= total_pages for point in points):
        raise ValueError(f"Split points must be between 1 and {total_pages - 1}.")

    boundaries = [0, *points, total_pages]
    source_stem = Path(input_path).stem
    outputs: list[Path] = []
    for start, end in zip(boundaries, boundaries[1:]):
        writer = PdfWriter()
        for page_index in range(start, end):
            writer.add_page(reader.pages[page_index])
        output_path = Path(output_dir) / f"{source_stem}_split_{start + 1}-{end}.pdf"
        outputs.append(_write(writer, output_path))
    return outputs


def rotate_pages(
    input_path: str | Path,
    pages: Iterable[int] | None,
    angle: int,
    output_path: str | Path,
) -> Path:
    if angle not in {90, 180, 270}:
        raise ValueError("Rotation angle must be 90, 180, or 270 degrees.")
    reader = _reader(input_path)
    page_numbers = set(range(1, len(reader.pages) + 1)) if pages is None else set(pages)
    _validate_pages(page_numbers, len(reader.pages))
    writer = PdfWriter()
    for page_number, page in enumerate(reader.pages, start=1):
        if page_number in page_numbers:
            page.rotate(angle)
        writer.add_page(page)
    return _write(writer, output_path)


def reorder_pages(
    input_path: str | Path, page_order: Iterable[int], output_path: str | Path
) -> Path:
    reader = _reader(input_path)
    order = list(page_order)
    if sorted(order) != list(range(1, len(reader.pages) + 1)):
        raise ValueError("Page order must contain every page exactly once.")
    writer = PdfWriter()
    _add_pages(writer, reader, order)
    return _write(writer, output_path)


def delete_pages(
    input_path: str | Path, pages: Iterable[int], output_path: str | Path
) -> Path:
    reader = _reader(input_path)
    pages_to_delete = set(pages)
    _validate_pages(pages_to_delete, len(reader.pages))
    remaining = [page for page in range(1, len(reader.pages) + 1) if page not in pages_to_delete]
    if not remaining:
        raise ValueError("At least one page must remain.")
    writer = PdfWriter()
    _add_pages(writer, reader, remaining)
    return _write(writer, output_path)


def _validate_pages(pages: Iterable[int], page_count: int) -> None:
    page_numbers = list(pages)
    if not page_numbers or any(page < 1 or page > page_count for page in page_numbers):
        raise ValueError(f"Pages must be between 1 and {page_count}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Perform common PDF operations.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--extract", metavar="PAGES", help="Extract pages, e.g. 1,3-5")
    parser.add_argument("--rotate", type=int, metavar="DEGREES")
    args = parser.parse_args()

    if args.extract:
        reader = _reader(args.input)
        extract_pages(args.input, parse_page_selection(args.extract, len(reader.pages)), args.output)
    elif args.rotate:
        rotate_pages(args.input, None, args.rotate, args.output)
    else:
        parser.error("Choose an operation, such as --extract or --rotate.")


if __name__ == "__main__":
    main()
