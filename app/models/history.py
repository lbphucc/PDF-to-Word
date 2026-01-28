"""
History Model - Lưu trữ lịch sử chuyển đổi
"""
from datetime import datetime
from app.extensions import db


class History(db.Model):
    """Model lưu lịch sử chuyển đổi PDF"""
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)  # Tên file PDF gốc
    docx_filename = db.Column(db.String(100))  # Tên file đã chuyển đổi
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20))  # 'Success' hoặc 'Failed'
    mode = db.Column(db.String(20))  # 'Local' hoặc 'Cloud'
    output_format = db.Column(db.String(10))  # 'word', 'excel', 'powerpoint'
    message = db.Column(db.String(200))

    def __repr__(self):
        return f'<History {self.filename} -> {self.output_format}>'
