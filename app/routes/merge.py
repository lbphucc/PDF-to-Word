"""
Merge Routes - Ghép và tách PDF
"""
import os
import uuid
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, request, send_file, current_app, jsonify, url_for
from PyPDF2 import PdfMerger
from pypdf import PdfReader, PdfWriter

from app.services.merger import parse_ranges

# Tạo Blueprint
merge_bp = Blueprint('merge', __name__)


@merge_bp.route('/merge', methods=['GET'])
def merge():
    """Trang ghép PDF"""
    return render_template('merge.html')


@merge_bp.route('/merge', methods=['POST'])
def merge_post():
    """Xử lý ghép PDF"""
    files = request.files.getlist('pdf_files')
    print('FILES:', files)

    if not files or len(files) < 2:
        return jsonify({'error': 'Cần chọn ít nhất 2 file PDF'}), 400

    merger = PdfMerger()

    for file in files:
        if file.filename == '':
            continue
        merger.append(file)

    output_name = f'merged_{uuid.uuid4().hex}.pdf'
    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_name)

    merger.write(output_path)
    merger.close()

    # Trả về JSON để frontend hiển thị preview
    return jsonify({
        'success': True,
        'filename': output_name,
        'preview_url': url_for('merge.preview_result', filename=output_name),
        'download_url': url_for('merge.download_result', filename=output_name)
    })


@merge_bp.route('/split', methods=['GET'])
def split():
    """Trang tách PDF"""
    return render_template('split.html')


@merge_bp.route('/split', methods=['POST'])
def split_post():
    """Xử lý tách PDF"""
    file = request.files.get('pdf_file')
    ranges = request.form.getlist('page_range')
    mode = request.form.get('split_mode', 'merge')

    if not file:
        return jsonify({'error': 'Chưa chọn file PDF'}), 400

    reader = PdfReader(file)
    total_pages = len(reader.pages)

    # MERGE MODE - Gộp các range thành 1 file
    if mode == 'merge':
        pages, error = parse_ranges(ranges, total_pages)
        if error:
            return jsonify({'error': error}), 400

        writer = PdfWriter()
        for i in pages:
            writer.add_page(reader.pages[i])

        output_name = f'split_{uuid.uuid4().hex}.pdf'
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_name)
        with open(output_path, 'wb') as f:
            writer.write(f)

        return jsonify({
            'success': True,
            'filename': output_name,
            'preview_url': url_for('merge.preview_result', filename=output_name),
            'download_url': url_for('merge.download_result', filename=output_name),
            'is_zip': False
        })

    # SEPARATE MODE - Tách riêng từng range
    zip_name = f'split_{uuid.uuid4().hex}.zip'
    zip_path = os.path.join(current_app.config['UPLOAD_FOLDER'], zip_name)
    
    # Cũng tạo một file PDF preview từ range đầu tiên
    preview_name = f'preview_{uuid.uuid4().hex}.pdf'
    preview_path = os.path.join(current_app.config['UPLOAD_FOLDER'], preview_name)
    first_range_saved = False
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for idx, r in enumerate(ranges, start=1):
            pages, error = parse_ranges([r], total_pages)
            if error:
                return jsonify({'error': error}), 400

            writer = PdfWriter()
            for i in pages:
                writer.add_page(reader.pages[i])

            pdf_name = f'range_{idx}.pdf'
            pdf_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_name)
            with open(pdf_path, 'wb') as f:
                writer.write(f)

            # Lưu range đầu tiên làm preview
            if not first_range_saved:
                import shutil
                shutil.copy(pdf_path, preview_path)
                first_range_saved = True

            zipf.write(pdf_path, pdf_name)
            os.remove(pdf_path)

    return jsonify({
        'success': True,
        'filename': zip_name,
        'preview_url': url_for('merge.preview_result', filename=preview_name),
        'download_url': url_for('merge.download_result', filename=zip_name),
        'is_zip': True,
        'preview_filename': preview_name
    })


@merge_bp.route('/preview-result/<filename>')
def preview_result(filename):
    """Xem preview file PDF kết quả"""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='application/pdf')
    else:
        return "File không tồn tại", 404


@merge_bp.route('/download-result/<filename>')
def download_result(filename):
    """Tải file kết quả về"""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        # Xác định download_name dựa trên extension
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.zip':
            download_name = 'split.zip'
        elif 'split' in filename:
            download_name = 'split.pdf'
        elif 'merged' in filename:
            download_name = 'merged.pdf'
        elif 'rotated' in filename:
            download_name = 'rotated.pdf'
        elif 'numbered' in filename:
            download_name = 'numbered.pdf'
        elif 'watermarked' in filename:
            download_name = 'watermarked.pdf'
        else:
            download_name = filename
            
        return send_file(file_path, as_attachment=True, download_name=download_name)
    else:
        return "File không tồn tại", 404


@merge_bp.route('/cancel-result/<filename>')
def cancel_result(filename):
    """Xóa file kết quả khi người dùng hủy"""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    
    return jsonify({'success': True})


@merge_bp.route('/compress')
def compress():
    """Trang nén PDF (placeholder)"""
    return render_template('compress.html')
