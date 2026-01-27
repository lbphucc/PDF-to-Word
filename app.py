import os
from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy # Import Database
from mylogic import pdf_to_word, pdf_to_excel, pdf_to_powerpoint, docx_to_pdf, xlsx_to_pdf, pptx_to_pdf  # Import logic
<<<<<<< HEAD

app = Flask(__name__)
=======
from PyPDF2 import PdfMerger

app = Flask(__name__)
@app.route("/merge", methods=["GET"])
def merge():
    return render_template("merge.html")


@app.route("/split")
def split():
    return render_template("split.html")

@app.route("/compress")
def compress():
    return render_template("compress.html")
>>>>>>> 6ef115f (add watermark feature)

# --- CẤU HÌNH ---
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Cấu hình SQLite (File db sẽ tên là project.db nằm cùng thư mục)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Khởi tạo Database
db = SQLAlchemy(app)

# --- ĐỊNH NGHĨA MODEL (Bảng dữ liệu) ---
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)  # Tên file PDF gốc
    docx_filename = db.Column(db.String(100))  # Tên file đã chuyển đổi (docx, xlsx, pptx)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20)) # 'Success' hoặc 'Failed'
    mode = db.Column(db.String(20))   # 'Local' hoặc 'Cloud'
    output_format = db.Column(db.String(10))  # 'word', 'excel', 'powerpoint'
    message = db.Column(db.String(200))

# Tạo file Database nếu chưa có (Chạy 1 lần đầu)
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    # Lấy 10 lần chuyển đổi gần nhất từ DB để hiển thị ra Web
    recent_conversions = History.query.order_by(History.timestamp.desc()).limit(10).all()

    # Kiểm tra file có tồn tại không cho mỗi record
    for item in recent_conversions:
        if item.docx_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], item.docx_filename)
            item.file_exists = os.path.exists(file_path)
        else:
            item.file_exists = False

    return render_template('index.html', history=recent_conversions)

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdf_file' not in request.files:
        return "Lỗi: Không có file", 400

    file = request.files['pdf_file']
    if file.filename == '':
        return "Lỗi: Tên file rỗng", 400

    mode = request.form.get('mode', 'local')
    output_format = request.form.get('output_format', 'word')

    if file:
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)

        # Xác định đuôi file và hàm chuyển đổi dựa trên output_format
        format_config = {
            'word': {'ext': '.docx', 'func': pdf_to_word},
            'excel': {'ext': '.xlsx', 'func': pdf_to_excel},
            'powerpoint': {'ext': '.pptx', 'func': pdf_to_powerpoint}
        }

        config = format_config.get(output_format, format_config['word'])
        output_ext = config['ext']
        convert_func = config['func']

        output_filename = os.path.splitext(filename)[0] + output_ext
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # 1. Thực hiện chuyển đổi
        result = convert_func(pdf_path, output_path, mode=mode)

        # 2. Lưu vào Database
        new_record = History(
            filename=filename,
            docx_filename=output_filename if result['status'] else None,
            status='Success' if result['status'] else 'Failed',
            mode=mode,
            output_format=output_format,
            message=result['message']
        )
        db.session.add(new_record)
        db.session.commit()

        if result['status']:
            # Tạo PDF preview cho tất cả định dạng
            pdf_preview_filename = os.path.splitext(output_filename)[0] + '_preview.pdf'
            pdf_preview_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_preview_filename)

            # Chọn hàm convert phù hợp
            preview_funcs = {
                'word': docx_to_pdf,
                'excel': xlsx_to_pdf,
                'powerpoint': pptx_to_pdf
            }
            preview_func = preview_funcs.get(output_format, docx_to_pdf)
            preview_result = preview_func(output_path, pdf_preview_path)

            if preview_result['status']:
                return render_template('preview.html',
                                       pdf_filename=pdf_preview_filename,
                                       docx_filename=output_filename,
                                       output_format=output_format)
            else:
                return render_template('preview.html',
                                       pdf_filename=None,
                                       docx_filename=output_filename,
                                       output_format=output_format,
                                       error_message=preview_result['message'])
        else:
            return f"Lỗi: {result['message']}", 500

# --- ROUTE XEM PREVIEW TỪ LỊCH SỬ ---
@app.route('/preview/<output_filename>')
def preview_history(output_filename):
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    # Kiểm tra file có tồn tại không
    if not os.path.exists(output_path):
        return "File không tồn tại hoặc đã bị xóa!", 404

    # Xác định định dạng file dựa trên extension
    ext = os.path.splitext(output_filename)[1].lower()
    format_map = {
        '.docx': ('word', docx_to_pdf),
        '.xlsx': ('excel', xlsx_to_pdf),
        '.pptx': ('powerpoint', pptx_to_pdf)
    }
    output_format, preview_func = format_map.get(ext, ('word', docx_to_pdf))

    # Tên file PDF preview
    pdf_preview_filename = os.path.splitext(output_filename)[0] + '_preview.pdf'
    pdf_preview_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_preview_filename)

    # Kiểm tra nếu PDF preview chưa có thì tạo mới
    if not os.path.exists(pdf_preview_path):
        preview_result = preview_func(output_path, pdf_preview_path)
        if not preview_result['status']:
            return render_template('preview.html',
                                   pdf_filename=None,
                                   docx_filename=output_filename,
                                   output_format=output_format,
                                   error_message=preview_result['message'])

    return render_template('preview.html',
                           pdf_filename=pdf_preview_filename,
                           docx_filename=output_filename,
                           output_format=output_format)

# --- ROUTE XEM FILE PDF (Không download, hiển thị trong browser) ---
@app.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        # as_attachment=False để browser hiển thị thay vì tải về
        return send_file(file_path, as_attachment=False)
    else:
        return "File không tồn tại hoặc đã bị xóa!", 404

# --- ROUTE TẢI FILE ---
@app.route('/download/<filename>')
def download_file(filename):
    # Đường dẫn file cần tải
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Kiểm tra file có tồn tại không để tránh lỗi
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File không tồn tại hoặc đã bị xóa!", 404


# --- ROUTE XÓA LỊCH SỬ ĐƠN LẺ ---
@app.route('/delete/<int:id>')
def delete_history(id):
    record = History.query.get(id)
    if record:
        # Xóa file đã chuyển đổi nếu tồn tại
        if record.docx_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], record.docx_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            # Xóa file preview PDF nếu có
            preview_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        os.path.splitext(record.docx_filename)[0] + '_preview.pdf')
            if os.path.exists(preview_path):
                os.remove(preview_path)

        db.session.delete(record)
        db.session.commit()

    return redirect(url_for('index'))


# --- ROUTE XÓA TẤT CẢ LỊCH SỬ ---
@app.route('/delete-all')
def delete_all_history():
    # Lấy tất cả records
    records = History.query.all()

    for record in records:
        # Xóa file đã chuyển đổi nếu tồn tại
        if record.docx_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], record.docx_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            # Xóa file preview PDF nếu có
            preview_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        os.path.splitext(record.docx_filename)[0] + '_preview.pdf')
            if os.path.exists(preview_path):
                os.remove(preview_path)

    # Xóa tất cả records trong database
    History.query.delete()
    db.session.commit()

    return redirect(url_for('index'))

<<<<<<< HEAD
=======
from mylogic import merge_pdfs   # nhớ import ở đầu file
@app.route("/merge", methods=["POST"])
def merge_post():
    files = request.files.getlist("pdf_files")
    print("FILES:", files)

    if not files or len(files) < 2:
        return "Cần chọn ít nhất 2 file PDF", 400

    merger = PdfMerger()

    for file in files:
        if file.filename == "":
            continue
        merger.append(file)

    output_name = f"merged_{int(datetime.now().timestamp())}.pdf"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_name)

    merger.write(output_path)
    merger.close()

    return send_file(
        output_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="merged.pdf"
    )


from flask import request, send_file
from pypdf import PdfReader, PdfWriter
from mylogic import parse_ranges
import zipfile, os, uuid

@app.route("/split", methods=["POST"])
def split_post():
    file = request.files.get("pdf_file")
    ranges = request.form.getlist("page_range")
    mode = request.form.get("split_mode", "merge")

    if not file:
        return "Chưa chọn file PDF", 400

    reader = PdfReader(file)
    total_pages = len(reader.pages)

    # ===== MERGE MODE =====
    if mode == "merge":
        pages, error = parse_ranges(ranges, total_pages)
        if error:
            return error, 400

        writer = PdfWriter()
        for i in pages:
            writer.add_page(reader.pages[i])

        output = f"merged_{uuid.uuid4().hex}.pdf"
        with open(output, "wb") as f:
            writer.write(f)

        return send_file(
            output,
            as_attachment=True,
            download_name="split.pdf"
        )

    # ===== SEPARATE MODE =====
    zip_name = f"split_{uuid.uuid4().hex}.zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for idx, r in enumerate(ranges, start=1):
            pages, error = parse_ranges([r], total_pages)
            if error:
                return error, 400

            writer = PdfWriter()
            for i in pages:
                writer.add_page(reader.pages[i])

            pdf_name = f"range_{idx}.pdf"
            with open(pdf_name, "wb") as f:
                writer.write(f)

            zipf.write(pdf_name)
            os.remove(pdf_name)

    return send_file(
        zip_name,
        as_attachment=True,
        download_name="split.zip"
    )

import traceback
from flask import request, render_template, send_file
from mylogic import rotate_pdf_logic

@app.route("/rotate", methods=["GET", "POST"])
def rotate_pdf():
    if request.method == "GET":
        return render_template("rotate.html")

    try:
        pdf = request.files.get("pdf")
        angle = int(request.form.get("angle", 90))
        page_range = request.form.get("page_range", "")

        if not pdf:
            return "Chưa chọn file PDF", 400

        pdf.stream.seek(0)
        output_pdf = rotate_pdf_logic(pdf.stream, angle, page_range)

        return send_file(
            output_pdf,
            as_attachment=True,
            download_name="rotated.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("❌ ROTATE ERROR FULL:")
        traceback.print_exc()
        return str(e), 500
from mylogic import number_pdf_logic

@app.route("/page_number", methods=["GET", "POST"])
def page_number():
    if request.method == "GET":
        return render_template("page_number.html")

    try:
        # ---- Get file ----
        pdf = request.files.get("pdf")
        if not pdf:
            return "Không có file PDF", 400

        # ---- Get options ----
        page_range = request.form.get("page_range", "").strip()
        start_number = int(request.form.get("start_number", 1))

        end_number_raw = request.form.get("end_number")
        end_number = int(end_number_raw) if end_number_raw else None

        fmt = request.form.get("format", "n")

        # ---- Process ----
        pdf.stream.seek(0)

        output = number_pdf_logic(
            pdf.stream,
            page_range=page_range,
            start_number=start_number,
            end_number=end_number,
            fmt=fmt
        )

        output.seek(0)

        # ---- Return file ----
        return send_file(
            output,
            as_attachment=True,
            download_name="numbered.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("❌ PAGE NUMBER ERROR:")
        traceback.print_exc()
        return str(e), 500

from flask import request, send_file, render_template
from mylogic import watermark_text, watermark_image


@app.route("/watermark", methods=["GET", "POST"])
def watermark():
    if request.method == "GET":
        return render_template("watermark.html")

    pdf = request.files.get("pdf")
    if not pdf:
        return "Thiếu file PDF", 400

    text = request.form.get("wmText", "WATERMARK")
    font_size = int(request.form.get("fontSize", 40))
    opacity = float(request.form.get("opacity", 30)) / 100

    output = watermark_text(pdf, text, font_size, opacity)

    return send_file(
        output,
        as_attachment=True,
        download_name="watermarked.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)



>>>>>>> 6ef115f (add watermark feature)

if __name__ == '__main__':
    app.run(debug=True)