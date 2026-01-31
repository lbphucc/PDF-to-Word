"""
History Model - Lưu trữ lịch sử chuyển đổi và các công cụ PDF
"""
from datetime import datetime
from app.extensions import db


class History(db.Model):
    """Model lưu lịch sử chuyển đổi PDF và các công cụ"""
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)  # Tên file PDF gốc
    docx_filename = db.Column(db.String(100))  # Tên file đã chuyển đổi (cho convert)
    result_filename = db.Column(db.String(100))  # Tên file kết quả (cho các tool khác)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20))  # 'Success' hoặc 'Failed'
    mode = db.Column(db.String(20))  # 'Local' hoặc 'Cloud'
    output_format = db.Column(db.String(10))  # 'word', 'excel', 'powerpoint'
    tool_type = db.Column(db.String(20), default='convert')  # 'convert', 'split', 'merge', 'rotate', 'page_number', 'watermark'
    message = db.Column(db.String(200))

    def __repr__(self):
        return f'<History {self.filename} -> {self.tool_type}>'
    
    def get_output_filename(self):
        """Lấy tên file kết quả dựa trên loại tool"""
        if self.tool_type in ['convert', None, ''] or not self.tool_type:
            return self.docx_filename
        return self.result_filename or self.docx_filename
