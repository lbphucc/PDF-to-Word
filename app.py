import os
from datetime import datetime
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy # Import Database
from mylogic import pdf_to_word # Import logic cũ của bạn

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
    filename = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20)) # 'Success' hoặc 'Failed'
    mode = db.Column(db.String(20))   # 'Local' hoặc 'Cloud'
    message = db.Column(db.String(200))

# Tạo file Database nếu chưa có (Chạy 1 lần đầu)
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    # Lấy 5 lần chuyển đổi gần nhất từ DB để hiển thị ra Web
    # Sắp xếp giảm dần theo thời gian
    recent_conversions = History.query.order_by(History.timestamp.desc()).limit(10).all()
    
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

        # Gọi logic xử lý
        result = pdf_to_word(pdf_path, docx_path, mode=mode)

        # --- LƯU VÀO DATABASE ---
        new_record = History(
            filename=filename,
            status='Success' if result['status'] else 'Failed',
            mode=mode,
            message=result['message']
        )
        db.session.add(new_record)
        db.session.commit()
        # ------------------------

        if result['status']:
            return send_file(docx_path, as_attachment=True)
        else:
            return f"Lỗi: {result['message']}", 500

if __name__ == '__main__':
    app.run(debug=True)