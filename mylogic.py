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