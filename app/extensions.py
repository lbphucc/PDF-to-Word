"""
Flask Extensions
Khởi tạo các extension để tránh circular imports
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions (without app)
db = SQLAlchemy()
