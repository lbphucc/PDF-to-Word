"""
Main Routes - Trang chính, chuyển đổi, xem trước, tải file, lịch sử
"""
import os
from flask import Blueprint, render_template, request, send_file, redirect, url_for, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.history import History
from app.services.converter import (
    pdf_to_word, pdf_to_excel, pdf_to_powerpoint,
    docx_to_pdf, xlsx_to_pdf, pptx_to_pdf
)

# Tạo Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    """Trang chủ - hiển thị form chuyển đổi và lịch sử"""
    recent_conversions = History.query.order_by(History.timestamp.desc()).limit(10).all()

    for item in recent_conversions:
        if item.docx_filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.docx_filename)
            item.file_exists = os.path.exists(file_path)
        else:
            item.file_exists = False

    return render_template('index.html', history=recent_conversions)


@main_bp.route('/convert', methods=['POST'])
def convert():
    """Xử lý chuyển đổi PDF"""
    if 'pdf_file' not in request.files:
        return "Lỗi: Không có file", 400

    file = request.files['pdf_file']
    if file.filename == '':
        return "Lỗi: Tên file rỗng", 400

    mode = request.form.get('mode', 'local')
    output_format = request.form.get('output_format', 'word')

    if file:
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)

        format_config = {
            'word': {'ext': '.docx', 'func': pdf_to_word},
            'excel': {'ext': '.xlsx', 'func': pdf_to_excel},
            'powerpoint': {'ext': '.pptx', 'func': pdf_to_powerpoint}
        }

        config = format_config.get(output_format, format_config['word'])
        output_ext = config['ext']
        convert_func = config['func']

        output_filename = os.path.splitext(filename)[0] + output_ext
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)

        result = convert_func(pdf_path, output_path, mode=mode)

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
            pdf_preview_filename = os.path.splitext(output_filename)[0] + '_preview.pdf'
            pdf_preview_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_preview_filename)

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


@main_bp.route('/preview/<output_filename>')
def preview_history(output_filename):
    """Xem trước file từ lịch sử"""
    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)

    if not os.path.exists(output_path):
        return "File không tồn tại hoặc đã bị xóa!", 404

    ext = os.path.splitext(output_filename)[1].lower()
    format_map = {
        '.docx': ('word', docx_to_pdf),
        '.xlsx': ('excel', xlsx_to_pdf),
        '.pptx': ('powerpoint', pptx_to_pdf)
    }
    output_format, preview_func = format_map.get(ext, ('word', docx_to_pdf))

    pdf_preview_filename = os.path.splitext(output_filename)[0] + '_preview.pdf'
    pdf_preview_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_preview_filename)

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


@main_bp.route('/view/<filename>')
def view_file(filename):
    """Xem file (không download)"""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=False)
    else:
        return "File không tồn tại hoặc đã bị xóa!", 404


@main_bp.route('/download/<filename>')
def download_file(filename):
    """Tải file về"""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File không tồn tại hoặc đã bị xóa!", 404


@main_bp.route('/delete/<int:id>')
def delete_history(id):
    """Xóa một record trong lịch sử"""
    record = History.query.get(id)
    if record:
        if record.docx_filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record.docx_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            preview_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                        os.path.splitext(record.docx_filename)[0] + '_preview.pdf')
            if os.path.exists(preview_path):
                os.remove(preview_path)

        db.session.delete(record)
        db.session.commit()

    return redirect(url_for('main.index'))


@main_bp.route('/delete-all')
def delete_all_history():
    """Xóa tất cả lịch sử"""
    records = History.query.all()

    for record in records:
        if record.docx_filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record.docx_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            preview_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                        os.path.splitext(record.docx_filename)[0] + '_preview.pdf')
            if os.path.exists(preview_path):
                os.remove(preview_path)

    History.query.delete()
    db.session.commit()

    return redirect(url_for('main.index'))
