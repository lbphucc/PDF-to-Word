"""
Merger Service - Handle PDF merge and split operations
"""
from PyPDF2 import PdfMerger
from pypdf import PdfReader, PdfWriter


def merge_pdfs(input_paths, output_path):
    """Merge multiple PDF files into one"""
    try:
        merger = PdfMerger()

        for pdf in input_paths:
            merger.append(pdf)

        merger.write(output_path)
        merger.close()

        return {
            "status": True,
            "message": "Merge thành công"
        }

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }


def parse_ranges(page_ranges, total_pages):
    """Parse page range strings into list of page indices"""
    pages = []
    for r in page_ranges:
        r = r.strip()

        if "-" in r:
            start, end = r.split("-")

            if not start.isdigit() or not end.isdigit():
                return None, f"Range không hợp lệ: {r}"

            start, end = int(start), int(end)

            if start < 1 or end < 1:
                return None, f"Trang phải >= 1 ({r})"

            if start > end:
                return None, f"Range sai thứ tự: {r}"

            if end > total_pages:
                return None, f"Trang {end} không tồn tại (PDF chỉ có {total_pages} trang)"

            pages.extend(range(start - 1, end))

        else:
            if not r.isdigit():
                return None, f"Trang không hợp lệ: {r}"

            page = int(r)

            if page < 1 or page > total_pages:
                return None, f"Trang {page} không tồn tại (PDF chỉ có {total_pages} trang)"

            pages.append(page - 1)

    return sorted(set(pages)), None


def split_pdf(pdf_stream, ranges, mode="merge"):
    """
    Split PDF by page ranges

    Args:
        pdf_stream: PDF file stream
        ranges: List of page range strings (e.g., ["1-3", "5"])
        mode: "merge" to combine all ranges into one file, "separate" to create separate files

    Returns:
        For merge mode: single PdfWriter
        For separate mode: list of PdfWriter objects
    """
    reader = PdfReader(pdf_stream)
    total_pages = len(reader.pages)

    if mode == "merge":
        pages, error = parse_ranges(ranges, total_pages)
        if error:
            return None, error

        writer = PdfWriter()
        for i in pages:
            writer.add_page(reader.pages[i])

        return writer, None

    else:  # separate mode
        writers = []
        for r in ranges:
            pages, error = parse_ranges([r], total_pages)
            if error:
                return None, error

            writer = PdfWriter()
            for i in pages:
                writer.add_page(reader.pages[i])
            writers.append(writer)

        return writers, None
