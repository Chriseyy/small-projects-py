import os
from pypdf import PdfReader, PdfWriter

# ==========================================
# 1. SPLIT
# ==========================================
def split_pdf(input_path, split_points):
    """
    Splits a PDF at multiple points.
    split_points: List of page numbers AFTER which to split.
    """
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    split_points = sorted(list(set(split_points)))
    
    start = 0
    base_name = os.path.splitext(input_path)[0]
    all_limits = split_points + [total_pages]

    for i, end in enumerate(all_limits):
        if start >= total_pages:
            break
            
        writer = PdfWriter()
        # Add pages from start to end
        for page_idx in range(start, end):
            if page_idx < total_pages:
                writer.add_page(reader.pages[page_idx])
        
        output_filename = f"{base_name}_split_{start+1}-{end}.pdf"
        
        with open(output_filename, "wb") as f:
            writer.write(f)
        
        print(f"Created: {output_filename}")
        start = end 


# ==========================================
# 2. EXTRACT
# ==========================================
def extract_pages(input_path, pages_to_extract, mode="single"):
    """
    Extracts pages.
    mode="single": All pages in one PDF.
    mode="separate": Each page in a separate PDF.
    """
    reader = PdfReader(input_path)
    base_name = os.path.splitext(input_path)[0]

    if mode == "single":
        writer = PdfWriter()
        real_pages = []
        for p in pages_to_extract:
            idx = p - 1
            if 0 <= idx < len(reader.pages):
                writer.add_page(reader.pages[idx])
                real_pages.append(p)
        
        if real_pages:
            output_filename = f"{base_name}_extract_combined.pdf"
            with open(output_filename, "wb") as f:
                writer.write(f)
            print(f"Extracted pages {real_pages} to: {output_filename}")

    elif mode == "separate":
        for p in pages_to_extract:
            idx = p - 1
            if 0 <= idx < len(reader.pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[idx])
                
                output_filename = f"{base_name}_page_{p}.pdf"
                with open(output_filename, "wb") as f:
                    writer.write(f)
                print(f"Extracted single page: {output_filename}")


# ==========================================
# 3. MERGE (UPDATED - NO PdfMerger)
# ==========================================
def merge_pdfs(pdf_list, output_filename="merged_result.pdf"):
    """
    Merges PDFs using PdfWriter (fixes ImportError).
    """
    writer = PdfWriter()

    for pdf in pdf_list:
        if os.path.exists(pdf):
            writer.append(pdf)
        else:
            print(f"File missing: {pdf}")

    with open(output_filename, "wb") as f:
        writer.write(f)
    
    print(f"Merged into: {output_filename}")


# ==========================================
# 4. ROTATE
# ==========================================
def rotate_pages(input_path, rotation_config):
    """
    Rotates pages.
    rotation_config:
      - int (90): Rotate all
      - tuple ([1,3], 90): Rotate specific pages
      - dict {1:90, 2:180}: Mixed rotation
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Case 1: Rotate ALL (Input is just a number)
    if isinstance(rotation_config, int):
        global_angle = rotation_config
        for page in reader.pages:
            page.rotate(global_angle)
            writer.add_page(page)
        suffix = f"all_{global_angle}"

    # Case 2: List + Angle (Input: ([1,3], 90))
    elif isinstance(rotation_config, tuple):
        target_pages = [p - 1 for p in rotation_config[0]] 
        angle = rotation_config[1]
        
        for i, page in enumerate(reader.pages):
            if i in target_pages:
                page.rotate(angle)
            writer.add_page(page)
        suffix = "selected_rotated"

    # Case 3: Dictionary (Input: {1:90, 2:180})
    elif isinstance(rotation_config, dict):
        rotation_map = {k - 1: v for k, v in rotation_config.items()}
        
        for i, page in enumerate(reader.pages):
            if i in rotation_map:
                angle = rotation_map[i]
                page.rotate(angle)
            writer.add_page(page)
        suffix = "mixed_rotation"

    else:
        print("Invalid input for rotation.")
        return

    output_filename = f"{os.path.splitext(input_path)[0]}_{suffix}.pdf"
    with open(output_filename, "wb") as f:
        writer.write(f)
    print(f"Rotated PDF saved: {output_filename}")


# ==========================================
# CONTROL
# ==========================================
if __name__ == "__main__":
    
    my_pdf = "irgendwass.pdf"
    # split_pdf(my_pdf, [50])
    
    # extract_pages(my_pdf, [1, 2, 3], mode="single")

    # rotate_pages(my_pdf, 90)
    rotate_pages(my_pdf, ([1], 180))


    # merge_pdfs(["teil1.pdf", "teil2.pdf"], "fertig.pdf")
    
    print("Skript fertig geladen. Bitte einkommentieren, was du tun willst.")