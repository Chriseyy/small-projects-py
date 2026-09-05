from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from pdf_tool import (
    delete_pages,
    extract_pages,
    merge_pdfs,
    parse_page_selection,
    reorder_pages,
    rotate_pages,
    split_pdf,
)


def make_pdf(path: Path, page_count: int) -> Path:
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=100, height=100)
    with path.open("wb") as output_file:
        writer.write(output_file)
    return path


def page_count(path: Path) -> int:
    return len(PdfReader(path).pages)


def test_parse_page_selection_supports_ranges() -> None:
    assert parse_page_selection("1, 3-5,8", 8) == [1, 3, 4, 5, 8]


def test_parse_page_selection_rejects_invalid_pages() -> None:
    with pytest.raises(ValueError):
        parse_page_selection("1,9", 8)


def test_merge_extract_split_and_delete(tmp_path: Path) -> None:
    first = make_pdf(tmp_path / "first.pdf", 2)
    second = make_pdf(tmp_path / "second.pdf", 3)

    merged = merge_pdfs([first, second], tmp_path / "merged.pdf")
    assert page_count(merged) == 5

    extracted = extract_pages(merged, [5, 2], tmp_path / "extracted.pdf")
    assert page_count(extracted) == 2

    split_outputs = split_pdf(merged, [2], tmp_path / "splits")
    assert [page_count(path) for path in split_outputs] == [2, 3]

    deleted = delete_pages(merged, [1, 3], tmp_path / "deleted.pdf")
    assert page_count(deleted) == 3


def test_reorder_and_rotate(tmp_path: Path) -> None:
    source = make_pdf(tmp_path / "source.pdf", 3)
    reordered = reorder_pages(source, [3, 1, 2], tmp_path / "reordered.pdf")
    assert page_count(reordered) == 3

    rotated = rotate_pages(source, [2], 90, tmp_path / "rotated.pdf")
    assert PdfReader(rotated).pages[1].rotation == 90
