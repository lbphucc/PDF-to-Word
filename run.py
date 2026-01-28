"""
Entry Point - Điểm khởi chạy ứng dụng
"""
from app import create_app

# Tạo application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
