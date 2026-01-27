import os
import requests
from dotenv import load_dotenv # Import thư viện quản lý biến môi trường
from pdf2docx import Converter

# 1. Nạp biến môi trường từ file .env
load_dotenv()

# 2. Lấy API Key an toàn (Không còn Hardcode)
MY_API_KEY = os.getenv('CONVERT_API_SECRET')

def convert_local(pdf_file, docx_file):
    """Chuyển đổi bằng thư viện local (pdf2docx)"""
    try:
        cv = Converter(pdf_file)
        cv.convert(docx_file, start=0, end=None)
        cv.close()
        return {"status": True, "message": "Chuyển đổi Local thành công!"}
    except Exception as e:
        return {"status": False, "message": f"Lỗi Local: {str(e)}"}

def convert_cloud(pdf_file, docx_file):
    """Chuyển đổi Cloud: Lấy Link -> Tải về (Bảo mật + An toàn)"""
    try:
        # Kiểm tra bảo mật: Nếu chưa có Key thì báo lỗi ngay
        if not MY_API_KEY:
            return {"status": False, "message": "Lỗi bảo mật: Chưa cấu hình API Key trong file .env"}

        print(f"1. Đang gửi file lên ConvertAPI ")
        
        url = "https://v2.convertapi.com/convert/pdf/to/docx"
        
        params = {
            'Secret': MY_API_KEY, # Dùng key lấy từ .env
            'StoreFile': 'true', 
        }
        
        with open(pdf_file, 'rb') as f:
            files = {'File': f}
            response = requests.post(url, params=params, files=files)

        try:
            data = response.json()
        except:
            return {"status": False, "message": "Lỗi: Server trả về dữ liệu không hợp lệ."}

        if 'Files' in data:
            file_url = data['Files'][0]['Url']
            print(f"2. Chuyển đổi xong.")
            
            file_content = requests.get(file_url).content
            
            with open(docx_file, 'wb') as f_out:
                f_out.write(file_content)
                
            return {"status": True, "message": "Chuyển đổi Cloud thành công!"}
            
        else:
            error_message = data.get('Message', 'Lỗi không xác định từ API')
            print(f"LỖI API: {error_message}")
            return {"status": False, "message": f"Lỗi từ ConvertAPI: {error_message}"}

    except Exception as e:
        print(f"LỖI HỆ THỐNG: {str(e)}")
        return {"status": False, "message": f"Lỗi kết nối: {str(e)}"}

def pdf_to_word(pdf_file, docx_file, mode='local'):
    if not os.path.exists(pdf_file):
        return {"status": False, "message": "Không tìm thấy file đầu vào"}

    if mode == 'cloud':
        return convert_cloud(pdf_file, docx_file)
    else:
        return convert_local(pdf_file, docx_file)


def convert_cloud_generic(pdf_file, output_file, output_format):
    """Chuyển đổi PDF sang định dạng khác bằng ConvertAPI (xlsx, pptx)"""
    try:
        if not MY_API_KEY:
            return {"status": False, "message": "Lỗi bảo mật: Chưa cấu hình API Key trong file .env"}

        print(f"--- Đang chuyển đổi PDF sang {output_format.upper()} bằng ConvertAPI ---")

        url = f"https://v2.convertapi.com/convert/pdf/to/{output_format}"

        params = {
            'Secret': MY_API_KEY,
            'StoreFile': 'true',
        }

        with open(pdf_file, 'rb') as f:
            files = {'File': f}
            response = requests.post(url, params=params, files=files)

        try:
            data = response.json()
        except:
            return {"status": False, "message": "Lỗi: Server trả về dữ liệu không hợp lệ."}

        if 'Files' in data:
            file_url = data['Files'][0]['Url']
            print(f"Chuyển đổi xong.")

            file_content = requests.get(file_url).content

            with open(output_file, 'wb') as f_out:
                f_out.write(file_content)

            return {"status": True, "message": f"Chuyển đổi sang {output_format.upper()} thành công!"}

        else:
            error_message = data.get('Message', 'Lỗi không xác định từ API')
            print(f"LỖI API: {error_message}")
            return {"status": False, "message": f"Lỗi từ ConvertAPI: {error_message}"}

    except Exception as e:
        print(f"LỖI HỆ THỐNG: {str(e)}")
        return {"status": False, "message": f"Lỗi kết nối: {str(e)}"}


def pdf_to_excel(pdf_file, xlsx_file, mode='local'):
    """Chuyển đổi PDF sang Excel"""
    if not os.path.exists(pdf_file):
        return {"status": False, "message": "Không tìm thấy file đầu vào"}

    # Excel chỉ hỗ trợ cloud mode (ConvertAPI)
    return convert_cloud_generic(pdf_file, xlsx_file, 'xlsx')


def pdf_to_powerpoint(pdf_file, pptx_file, mode='local'):
    """Chuyển đổi PDF sang PowerPoint"""
    if not os.path.exists(pdf_file):
        return {"status": False, "message": "Không tìm thấy file đầu vào"}

    # PowerPoint chỉ hỗ trợ cloud mode (ConvertAPI)
    return convert_cloud_generic(pdf_file, pptx_file, 'pptx')


def docx_to_pdf(docx_file, pdf_file):
    """Chuyển đổi DOCX sang PDF bằng ConvertAPI"""
    return file_to_pdf(docx_file, pdf_file, 'docx')


def xlsx_to_pdf(xlsx_file, pdf_file):
    """Chuyển đổi XLSX sang PDF bằng ConvertAPI"""
    return file_to_pdf(xlsx_file, pdf_file, 'xlsx')


def pptx_to_pdf(pptx_file, pdf_file):
    """Chuyển đổi PPTX sang PDF bằng ConvertAPI"""
    return file_to_pdf(pptx_file, pdf_file, 'pptx')

<<<<<<< HEAD
=======
from PyPDF2 import PdfMerger, PdfReader


def merge_pdfs(input_paths, output_path):
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
from pypdf import PdfReader, PdfWriter

def parse_ranges(page_ranges, total_pages):
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

from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

def rotate_pdf_logic(pdf_stream, angle, page_range):
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
            page.rotate(angle)   # API ĐÚNG
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output


import fitz  # PyMuPDF
from io import BytesIO

def number_pdf_logic(
    pdf_stream,
    page_range="",
    start_number=1,
    end_number=None,
    fmt="n"
):
    pdf_stream.seek(0)
    doc = fitz.open(stream=pdf_stream.read(), filetype="pdf")

    total_pages = len(doc)

    # ---- Parse page range ----
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

        # ---- Insert textbox (an toàn nhất) ----
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


from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from PIL import Image

def watermark_image(pdf_file, image_file, scale, opacity):
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    img = Image.open(image_file)
    img_width, img_height = img.size
    ratio = scale / 100

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.setFillAlpha(opacity)

        w = img_width * ratio
        h = img_height * ratio

        # LƯU ẢNH RA BUFFER
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        can.drawImage(
            img_buffer,
            (width - w) / 2,
            (height - h) / 2,
            w,
            h,
            mask='auto'
        )

        can.save()

        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        page.merge_page(watermark_pdf.pages[0])

        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    return output


from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import io

def watermark_text(input_pdf, text, font_size=40, opacity=0.3):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        packet = io.BytesIO()
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

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

import pikepdf
from PIL import Image
import io

def watermark_image(pdf_file, image_file, scale=0.3, opacity=0.5):
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



>>>>>>> 6ef115f (add watermark feature)

def file_to_pdf(input_file, pdf_file, input_format):
    """Chuyển đổi file (docx/xlsx/pptx) sang PDF bằng ConvertAPI"""
    try:
        if not MY_API_KEY:
            return {"status": False, "message": "Lỗi bảo mật: Chưa cấu hình API Key trong file .env"}

        print(f"Đang tạo PDF preview từ {input_format.upper()} bằng ConvertAPI")

        url = f"https://v2.convertapi.com/convert/{input_format}/to/pdf"

        params = {
            'Secret': MY_API_KEY,
            'StoreFile': 'true',
        }

        with open(input_file, 'rb') as f:
            files = {'File': f}
            response = requests.post(url, params=params, files=files)

        try:
            data = response.json()
        except:
            return {"status": False, "message": "Lỗi: Server trả về dữ liệu không hợp lệ."}

        if 'Files' in data:
            file_url = data['Files'][0]['Url']
            print(f"Tạo PDF thành công. Đang tải về")

            file_content = requests.get(file_url).content

            with open(pdf_file, 'wb') as f_out:
                f_out.write(file_content)

            return {"status": True, "message": "Tạo PDF preview thành công!"}

        else:
            error_message = data.get('Message', 'Lỗi không xác định từ API')
            print(f"LỖI API: {error_message}")
            return {"status": False, "message": f"Lỗi từ ConvertAPI: {error_message}"}

    except Exception as e:
        print(f"LỖI HỆ THỐNG: {str(e)}")
        return {"status": False, "message": f"Lỗi tạo PDF: {str(e)}"}