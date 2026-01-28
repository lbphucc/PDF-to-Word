"""
Application Factory
Tạo và cấu hình Flask application theo pattern chuẩn
"""
import os
from flask import Flask

from app.config import config
from app.extensions import db
from app.routes import register_blueprints


def create_app(config_name=None):
    """
    Application Factory Pattern

    Args:
        config_name: Tên cấu hình ('development', 'production', 'testing')

    Returns:
        Flask application instance
    """
    # Lấy config từ environment hoặc mặc định
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Tạo Flask app
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )

    # Load configuration
    app.config.from_object(config[config_name])

    # Đảm bảo thư mục upload tồn tại
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Khởi tạo extensions
    db.init_app(app)

    # Đăng ký blueprints
    register_blueprints(app)

    # Tạo database tables
    with app.app_context():
        db.create_all()

    return app
