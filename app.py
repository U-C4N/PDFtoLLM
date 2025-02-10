from flask import Flask, render_template, request, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import io
import base64
from pathlib import Path
from converter import PDFConverter
from console import setup_logger
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')  # Better security practice

UPLOAD_FOLDER = Path('uploads')
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
total_tokens = 0

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_uploads():
    """Uploads klasöründeki tüm PDF dosyalarını temizler"""
    for file in UPLOAD_FOLDER.glob('*.pdf'):
        try:
            file.unlink()
        except Exception as e:
            print(f"Dosya silinirken hata oluştu: {e}")

def handle_pdf_upload(file):
    """Handle PDF file upload and return filepath"""
    if not file or file.filename == '':
        raise ValueError('No file selected')
    
    if not allowed_file(file.filename):
        raise ValueError('Invalid file type')
        
    filename = secure_filename(file.filename)
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)
    return filepath

# Uygulama başlatıldığında uploads klasörünü temizle
clear_uploads()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global total_tokens
    markdown_content = None
    current_tokens = 0

    if request.method == 'POST':
        clear_uploads()
        try:
            filepath = handle_pdf_upload(request.files.get('file'))
            logger = setup_logger(debug=True)
            converter = PDFConverter(logger)

            logger.info(f"Converting: {filepath.name}")
            markdown_content, current_tokens = converter.convert_pdf(filepath)
            total_tokens += current_tokens
            logger.info(f"Conversion completed: {current_tokens:.3f} tokens")
            logger.info(f"Total tokens so far: {total_tokens:.3f}")

            os.remove(filepath)
            logger.info(f"Temporary file deleted: {filepath}")

            flash(f'File converted successfully! Tokens in this file: {int(current_tokens):,}')
            return render_template('index.html', 
                                 markdown_content=markdown_content,
                                 current_tokens=int(current_tokens),
                                 total_tokens=int(total_tokens))

        except Exception as e:
            flash(f'Error: {str(e)}')
            if 'filepath' in locals() and filepath.exists():
                os.remove(filepath)

    return render_template('index.html', total_tokens=int(total_tokens))

@app.route('/extract-images', methods=['POST'])
def extract_images():
    try:
        filepath = handle_pdf_upload(request.files.get('file'))
        logger = setup_logger(debug=True)
        converter = PDFConverter(logger)
        
        # Yeni PyMuPDF metodunu kullan
        images = converter.extract_images_mupdf(filepath)
        
        # Return image data directly in response
        image_list = []
        for name, data in images:
            try:
                # Görüntü verilerini kontrol et
                img = Image.open(io.BytesIO(data))
                width, height = img.size
                
                # Base64 formatına çevir
                base64_data = base64.b64encode(data).decode('utf-8')
                
                # Dosya uzantısına göre MIME type belirle
                ext = name.split('.')[-1].lower()
                mime_type = 'image/jpeg' if ext in ['jpg', 'jpeg'] else f'image/{ext}'
                
                image_list.append({
                    'name': name,
                    'data': f'data:{mime_type};base64,{base64_data}',
                    'width': width,
                    'height': height,
                    'size': len(data)
                })
                logger.info(f"Processed {name} ({width}x{height}, {len(data)} bytes)")
            except Exception as e:
                logger.error(f"Error processing image {name}: {e}")
        
        logger.info(f"Extracted {len(image_list)} valid images from {filepath.name}")
        os.remove(filepath)
        
        if not image_list:
            return jsonify({'error': 'No valid images found in PDF'}), 404
            
        return jsonify({'images': image_list})
        
    except Exception as e:
        if 'filepath' in locals() and filepath.exists():
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/download-images', methods=['POST'])
def download_images():
    try:
        filepath = handle_pdf_upload(request.files.get('file'))
        logger = setup_logger(debug=True)
        converter = PDFConverter(logger)
        
        # Yeni PyMuPDF metodunu kullan
        images = converter.extract_images_mupdf(filepath)
        zip_data = converter.create_image_zip(images)
        
        os.remove(filepath)
        logger.info(f"Created ZIP with {len(images)} images from {filepath.name}")
        
        return send_file(
            io.BytesIO(zip_data),
            mimetype='application/zip',
            as_attachment=True,
            download_name='images.zip'
        )
    except Exception as e:
        if 'filepath' in locals() and filepath.exists():
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.template_filter('thousands_separator')
def thousands_separator(number):
    return "{:,}".format(number)

if __name__ == '__main__':
    clear_uploads()
    app.run(host='0.0.0.0', port=3000, debug=True)
