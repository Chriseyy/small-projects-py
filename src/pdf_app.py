from __future__ import annotations

import tempfile
from pathlib import Path

import fitz
import streamlit as st
from pypdf import PdfReader

from pdf_tool import (
    delete_pages,
    extract_pages,
    merge_pdfs,
    parse_page_selection,
    reorder_pages,
    rotate_pages,
    split_pdf,
)


OPERATIONS = ["Merge", "Extract", "Split", "Rotate", "Reorder", "Delete"]
PREVIEW_INITIAL_LIMIT = 12
PREVIEW_CHUNK_SIZE = 12
PREVIEW_MAXIMUM = 30


def save_upload(uploaded_file, directory: Path) -> Path:
    path = directory / uploaded_file.name
    path.write_bytes(uploaded_file.getvalue())
    return path


def output_download(path: Path, label: str = "Download PDF") -> None:
    st.download_button(
        label=label,
        data=path.read_bytes(),
        file_name=path.name,
        mime="application/pdf",
        type="primary",
    )


def render_thumbnails(document: Path | bytes, title: str, limit: int) -> int:
    if isinstance(document, Path):
        pdf = fitz.open(document)
    else:
        pdf = fitz.open(stream=document, filetype="pdf")

    with pdf:
        visible_count = min(len(pdf), limit)
        st.subheader(title)
        columns = st.columns(3)
        for index in range(visible_count):
            page = pdf[index]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(0.8, 0.8), alpha=False)
            with columns[index % 3]:
                st.image(
                    pixmap.tobytes("png"),
                    caption=f"Page {index + 1}",
                    use_container_width=True,
                )
        if len(pdf) > visible_count:
            st.caption(f"Showing {visible_count} of {len(pdf)} pages.")
        return len(pdf)


def show_comparison(source: Path, result_bytes: bytes | None) -> None:
    preview_limit = st.session_state.get("preview_limit", PREVIEW_INITIAL_LIMIT)
    if result_bytes:
        before, after = st.columns(2)
        with before:
            source_count = render_thumbnails(source, "Before changes", preview_limit)
        with after:
            result_count = render_thumbnails(result_bytes, "After changes", preview_limit)
    else:
        source_count = render_thumbnails(source, "Before changes", preview_limit)
        result_count = 0

    largest_count = max(source_count, result_count)
    can_load_more = preview_limit < min(largest_count, PREVIEW_MAXIMUM)
    if can_load_more and st.button("Load more pages", type="secondary"):
        st.session_state["preview_limit"] = min(
            preview_limit + PREVIEW_CHUNK_SIZE,
            PREVIEW_MAXIMUM,
        )
        st.rerun()
    elif largest_count > PREVIEW_MAXIMUM:
        st.caption(
            f"Preview is limited to {PREVIEW_MAXIMUM} pages. The full PDF was still processed."
        )


def reset_result(signature: tuple) -> None:
    if st.session_state.get("source_signature") != signature:
        st.session_state["source_signature"] = signature
        st.session_state["preview_limit"] = PREVIEW_INITIAL_LIMIT
        st.session_state.pop("preview_result", None)
        st.session_state.pop("preview_name", None)


st.set_page_config(page_title="Local PDF Toolbox", page_icon="📄")
st.title("Local PDF Toolbox")
st.caption("Files are processed in memory on this machine and are not uploaded to a service.")

operation = st.radio("Operation", OPERATIONS, horizontal=True)
multiple = operation == "Merge"
uploads = st.file_uploader(
    "Choose PDF file" + ("s" if multiple else ""),
    type="pdf",
    accept_multiple_files=multiple,
)

if uploads:
    upload_list = list(uploads) if multiple else [uploads]
    signature = (operation, tuple((upload.name, upload.size) for upload in upload_list))
    reset_result(signature)

    with tempfile.TemporaryDirectory() as temporary_directory:
        work_dir = Path(temporary_directory)
        input_paths = [save_upload(upload, work_dir) for upload in upload_list]
        source = input_paths[0]
        page_count = len(PdfReader(source).pages)
        output_path = work_dir / f"{source.stem}_{operation.lower()}.pdf"

        try:
            if operation == "Merge":
                if len(input_paths) < 2:
                    st.info("Choose at least two PDFs to merge.")
                elif st.button("Merge PDFs"):
                    result = merge_pdfs(input_paths, output_path)
                    st.success(f"Merged {len(input_paths)} PDFs into {result.name}.")
                    output_download(result)
            elif operation == "Extract":
                selection = st.text_input("Pages to extract", placeholder="1,3-5")
                if selection and st.button("Apply changes"):
                    pages = parse_page_selection(selection, page_count)
                    result = extract_pages(source, pages, output_path)
                    st.session_state["preview_result"] = result.read_bytes()
                    st.session_state["preview_name"] = result.name
            elif operation == "Split":
                selection = st.text_input("Split after pages", placeholder="2,5")
                if selection and st.button("Split PDF"):
                    points = parse_page_selection(selection, page_count - 1)
                    results = split_pdf(source, points, work_dir / "split")
                    st.success(f"Created {len(results)} PDF files.")
                    for result in results:
                        output_download(result, f"Download {result.name}")
            elif operation == "Rotate":
                selection = st.text_input("Pages to rotate (blank for all)", placeholder="1,3-5")
                angle = st.selectbox("Rotation", [90, 180, 270], format_func=lambda value: f"{value} degrees")
                if st.button("Apply changes"):
                    pages = parse_page_selection(selection, page_count) if selection else None
                    result = rotate_pages(source, pages, angle, output_path)
                    st.session_state["preview_result"] = result.read_bytes()
                    st.session_state["preview_name"] = result.name
            elif operation == "Reorder":
                selection = st.text_input("New page order", placeholder="3,1,2")
                if selection and st.button("Apply changes"):
                    order = parse_page_selection(selection, page_count)
                    result = reorder_pages(source, order, output_path)
                    st.session_state["preview_result"] = result.read_bytes()
                    st.session_state["preview_name"] = result.name
            elif operation == "Delete":
                selection = st.text_input("Pages to delete", placeholder="2,4-5")
                if selection and st.button("Apply changes"):
                    pages = parse_page_selection(selection, page_count)
                    result = delete_pages(source, pages, output_path)
                    st.session_state["preview_result"] = result.read_bytes()
                    st.session_state["preview_name"] = result.name
        except (FileNotFoundError, ValueError) as error:
            st.error(str(error))

        result_bytes = st.session_state.get("preview_result")
        if operation in {"Extract", "Rotate", "Reorder", "Delete"}:
            st.divider()
            show_comparison(source, result_bytes)
            if result_bytes:
                st.download_button(
                    "Download changed PDF",
                    data=result_bytes,
                    file_name=st.session_state["preview_name"],
                    mime="application/pdf",
                    type="primary",
                )
