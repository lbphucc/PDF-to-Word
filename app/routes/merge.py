"""
Merge Routes - Ghép và tách PDF
"""
import os
import uuid
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, request, send_file, current_app
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
        return 'Cần chọn ít nhất 2 file PDF', 400

    merger = PdfMerger()

    for file in files:
        if file.filename == '':
            continue
        merger.append(file)

    output_name = f'merged_{int(datetime.now().timestamp())}.pdf'
    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_name)

    merger.write(output_path)
    merger.close()

    return send_file(
        output_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='merged.pdf'
    )


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
        return 'Chưa chọn file PDF', 400

    reader = PdfReader(file)
    total_pages = len(reader.pages)

    # MERGE MODE - Gộp các range thành 1 file
    if mode == 'merge':
        pages, error = parse_ranges(ranges, total_pages)
        if error:
            return error, 400

        writer = PdfWriter()
        for i in pages:
            writer.add_page(reader.pages[i])

        output = f'merged_{uuid.uuid4().hex}.pdf'
        with open(output, 'wb') as f:
            writer.write(f)

        return send_file(
            output,
            as_attachment=True,
            download_name='split.pdf'
        )

    # SEPARATE MODE - Tách riêng từng range
    zip_name = f'split_{uuid.uuid4().hex}.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for idx, r in enumerate(ranges, start=1):
            pages, error = parse_ranges([r], total_pages)
            if error:
                return error, 400

            writer = PdfWriter()
            for i in pages:
                writer.add_page(reader.pages[i])

            pdf_name = f'range_{idx}.pdf'
            with open(pdf_name, 'wb') as f:
                writer.write(f)

            zipf.write(pdf_name)
            os.remove(pdf_name)

    return send_file(
        zip_name,
        as_attachment=True,
        download_name='split.zip'
    )


@merge_bp.route('/compress')
def compress():
    """Trang nén PDF (placeholder)"""
    return render_template('compress.html')
