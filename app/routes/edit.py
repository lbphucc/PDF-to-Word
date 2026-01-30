"""
Edit Routes - Xoay, watermark, đánh số trang
"""
import os
import uuid
import traceback
from flask import Blueprint, render_template, request, send_file, current_app, jsonify, url_for

from app.services.modifier import rotate_pdf_logic, number_pdf_logic, watermark_text, watermark_image

# Tạo Blueprint
edit_bp = Blueprint('edit', __name__)


@edit_bp.route('/rotate', methods=['GET', 'POST'])
def rotate_pdf():
    """Xoay trang PDF"""
    if request.method == 'GET':
        return render_template('rotate.html')

    try:
        pdf = request.files.get('pdf')
        angle = int(request.form.get('angle', 90))
        page_range = request.form.get('page_range', '')

        if not pdf:
            return jsonify({'error': 'Chưa chọn file PDF'}), 400

        pdf.stream.seek(0)
        output_pdf = rotate_pdf_logic(pdf.stream, angle, page_range)

        # Lưu file kết quả
        output_name = f'rotated_{uuid.uuid4().hex}.pdf'
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_name)
        
        with open(output_path, 'wb') as f:
            f.write(output_pdf.read())

        return jsonify({
            'success': True,
            'filename': output_name,
            'preview_url': url_for('merge.preview_result', filename=output_name),
            'download_url': url_for('merge.download_result', filename=output_name)
        })

    except Exception as e:
        print('ROTATE ERROR FULL:')
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@edit_bp.route('/page_number', methods=['GET', 'POST'])
def page_number():
    """Thêm số trang vào PDF"""
    if request.method == 'GET':
        return render_template('page_number.html')

    try:
        pdf = request.files.get('pdf')
        if not pdf:
            return jsonify({'error': 'Không có file PDF'}), 400

        page_range = request.form.get('page_range', '').strip()
        start_number = int(request.form.get('start_number', 1))

        end_number_raw = request.form.get('end_number')
        end_number = int(end_number_raw) if end_number_raw else None

        fmt = request.form.get('format', 'n')

        pdf.stream.seek(0)

        output = number_pdf_logic(
            pdf.stream,
            page_range=page_range,
            start_number=start_number,
            end_number=end_number,
            fmt=fmt
        )

        output.seek(0)

        # Lưu file kết quả
        output_name = f'numbered_{uuid.uuid4().hex}.pdf'
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_name)
        
        with open(output_path, 'wb') as f:
            f.write(output.read())

        return jsonify({
            'success': True,
            'filename': output_name,
            'preview_url': url_for('merge.preview_result', filename=output_name),
            'download_url': url_for('merge.download_result', filename=output_name)
        })

    except Exception as e:
        print('PAGE NUMBER ERROR:')
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@edit_bp.route('/watermark', methods=['GET', 'POST'])
def watermark():
    """Thêm watermark vào PDF"""
    if request.method == 'GET':
        return render_template('watermark.html')

    try:
        pdf = request.files.get('pdf')
        if not pdf:
            return jsonify({'error': 'Thiếu file PDF'}), 400

        text = request.form.get('wmText', 'WATERMARK')
        font_size = int(request.form.get('fontSize', 40))
        opacity = float(request.form.get('opacity', 30)) / 100

        output = watermark_text(pdf, text, font_size, opacity)

        # Lưu file kết quả
        output_name = f'watermarked_{uuid.uuid4().hex}.pdf'
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_name)
        
        with open(output_path, 'wb') as f:
            f.write(output.read())

        return jsonify({
            'success': True,
            'filename': output_name,
            'preview_url': url_for('merge.preview_result', filename=output_name),
            'download_url': url_for('merge.download_result', filename=output_name)
        })

    except Exception as e:
        print('WATERMARK ERROR:')
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
