import os
from datetime import datetime
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy # Import Database
from mylogic import pdf_to_word, docx_to_pdf  # Import logic

app = Flask(__name__)

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
    docx_filename = db.Column(db.String(100))  # Tên file Word đã chuyển đổi
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20)) # 'Success' hoặc 'Failed'
    mode = db.Column(db.String(20))   # 'Local' hoặc 'Cloud'
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

    if file:
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)

        docx_filename = os.path.splitext(filename)[0] + '.docx'
        docx_path = os.path.join(app.config['UPLOAD_FOLDER'], docx_filename)

        # 1. Thực hiện chuyển đổi (Logic cũ)
        result = pdf_to_word(pdf_path, docx_path, mode=mode)

        # 2. Lưu vào Database
        new_record = History(
            filename=filename,
            docx_filename=docx_filename if result['status'] else None,
            status='Success' if result['status'] else 'Failed',
            mode=mode,
            message=result['message']
        )
        db.session.add(new_record)
        db.session.commit()

        if result['status']:
            # Tạo PDF preview từ file DOCX
            pdf_preview_filename = os.path.splitext(docx_filename)[0] + '_preview.pdf'
            pdf_preview_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_preview_filename)

            preview_result = docx_to_pdf(docx_path, pdf_preview_path)

            if preview_result['status']:
                # Trả về trang preview với PDF
                return render_template('preview.html',
                                       pdf_filename=pdf_preview_filename,
                                       docx_filename=docx_filename)
            else:
                # Nếu không tạo được PDF preview, vẫn cho tải file DOCX
                return render_template('preview.html',
                                       pdf_filename=None,
                                       docx_filename=docx_filename,
                                       error_message=preview_result['message'])
        else:
            return f"Lỗi: {result['message']}", 500

# --- ROUTE XEM PREVIEW TỪ LỊCH SỬ ---
@app.route('/preview/<docx_filename>')
def preview_history(docx_filename):
    docx_path = os.path.join(app.config['UPLOAD_FOLDER'], docx_filename)

    # Kiểm tra file Word có tồn tại không
    if not os.path.exists(docx_path):
        return "File không tồn tại hoặc đã bị xóa!", 404

    # Tên file PDF preview
    pdf_preview_filename = os.path.splitext(docx_filename)[0] + '_preview.pdf'
    pdf_preview_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_preview_filename)

    # Kiểm tra nếu PDF preview chưa có thì tạo mới
    if not os.path.exists(pdf_preview_path):
        preview_result = docx_to_pdf(docx_path, pdf_preview_path)
        if not preview_result['status']:
            return render_template('preview.html',
                                   pdf_filename=None,
                                   docx_filename=docx_filename,
                                   error_message=preview_result['message'])

    return render_template('preview.html',
                           pdf_filename=pdf_preview_filename,
                           docx_filename=docx_filename)

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

if __name__ == '__main__':
    app.run(debug=True)