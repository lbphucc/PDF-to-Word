"""
Routes Package - Đăng ký tất cả blueprints
"""
from app.routes.main import main_bp
from app.routes.merge import merge_bp
from app.routes.edit import edit_bp


def register_blueprints(app):
    """Đăng ký tất cả blueprints vào app"""
    app.register_blueprint(main_bp)
    app.register_blueprint(merge_bp)
    app.register_blueprint(edit_bp)
