"""
Modifier Service - Handle PDF editing operations (rotate, watermark, page numbers)
"""
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import fitz  # PyMuPDF


def rotate_pdf_logic(pdf_stream, angle, page_range):
    """
    Rotate PDF pages by specified angle

    Args:
        pdf_stream: PDF file stream
        angle: Rotation angle (90, 180, 270)
        page_range: Page range string (e.g., "1-3,5" or empty for all pages)

    Returns:
        BytesIO object containing the rotated PDF
    """
    reader = PdfReader(pdf_stream)
    writer = PdfWriter()

    total_pages = len(reader.pages)

    pages_to_rotate = set()

    if not page_range.strip():
        pages_to_rotate = set(range(total_pages))
    else:
        for part in page_range.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-")
                for i in range(int(start) - 1, int(end)):
                    pages_to_rotate.add(i)
            else:
                pages_to_rotate.add(int(part) - 1)

    for i, page in enumerate(reader.pages):
        if i in pages_to_rotate:
            page.rotate(angle)
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def number_pdf_logic(pdf_stream, page_range="", start_number=1, end_number=None, fmt="n"):
    """
    Add page numbers to PDF

    Args:
        pdf_stream: PDF file stream
        page_range: Page range string (empty for all pages)
        start_number: Starting page number
        end_number: Ending page number (None for no limit)
        fmt: Format - "n" for "Trang {n}", "n_p" for "Trang {n} trên {p}"

    Returns:
        BytesIO object containing the numbered PDF
    """
    pdf_stream.seek(0)
    doc = fitz.open(stream=pdf_stream.read(), filetype="pdf")

    total_pages = len(doc)

    # Parse page range
    pages = []
    if not page_range.strip():
        pages = list(range(total_pages))
    else:
        for part in page_range.split(","):
            part = part.strip()
            if "-" in part:
                s, e = map(int, part.split("-"))
                pages.extend(range(s - 1, e))
            else:
                pages.append(int(part) - 1)

    current_number = start_number

    for i in pages:
        if i < 0 or i >= total_pages:
            continue

        if end_number and current_number > end_number:
            break

        page = doc[i]
        p = total_pages

        if fmt == "n":
            text = f"Trang {current_number}"
        else:
            text = f"Trang {current_number} trên {p}"

        # Insert textbox at bottom of page
        rect = fitz.Rect(
            0,
            page.rect.height - 40,
            page.rect.width,
            page.rect.height - 10
        )

        page.insert_textbox(
            rect,
            text,
            fontsize=11,
            fontname="helv",
            align=fitz.TEXT_ALIGN_CENTER,
            color=(0, 0, 0),
        )

        current_number += 1

    output = BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output


def watermark_text(input_pdf, text, font_size=40, opacity=0.3):
    """
    Add text watermark to PDF

    Args:
        input_pdf: PDF file object
        text: Watermark text
        font_size: Font size for watermark
        opacity: Opacity (0-1)

    Returns:
        BytesIO object containing the watermarked PDF
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        packet = BytesIO()
        can = canvas.Canvas(packet)

        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        can.setFont("Helvetica", font_size)
        can.setFillColor(Color(0, 0, 0, alpha=opacity))
        can.saveState()
        can.translate(width / 2, height / 2)
        can.rotate(45)
        can.drawCentredString(0, 0, text)
        can.restoreState()
        can.save()

        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        page.merge_page(watermark_pdf.pages[0])
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output


def watermark_image(pdf_file, image_file, scale=0.3, opacity=0.5):
    """
    Add image watermark to PDF

    Args:
        pdf_file: PDF file object
        image_file: Image file object
        scale: Image scale (0-1)
        opacity: Opacity (0-1)

    Returns:
        BytesIO object containing the watermarked PDF
    """
    import pikepdf
    from PIL import Image
    import io

    pdf = pikepdf.open(pdf_file)

    img = Image.open(image_file).convert("RGBA")
    alpha = img.split()[3].point(lambda x: int(x * opacity))
    img.putalpha(alpha)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    wm = pdf.make_stream(img_bytes.read())

    for page in pdf.pages:
        page.add_overlay(wm)

    out = io.BytesIO()
    pdf.save(out)
    out.seek(0)
    return out
