from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from converter import PDFConverter
from console import setup_logger

app = Flask(__name__)
app.secret_key = 'pdf2md-secret-key'  # Required for flash messages

# Upload folder configuration
UPLOAD_FOLDER = Path('uploads')
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload folder exists
UPLOAD_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    markdown_content = None
    token_count = 0

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return render_template('index.html')

        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return render_template('index.html')

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = UPLOAD_FOLDER / filename
                file.save(filepath)

                # Convert PDF to Markdown
                logger = setup_logger(debug=True)  # Enable debug mode
                converter = PDFConverter(logger)

                # Conversion process
                logger.info(f"Converting: {filename}")
                markdown_content, token_count = converter.convert_pdf(filepath)
                logger.info(f"Conversion completed: {token_count:.3f} tokens")

                # Remove uploaded file
                os.remove(filepath)
                logger.info(f"Temporary file deleted: {filepath}")

            except Exception as e:
                logger.error(f"Error occurred: {str(e)}")
                flash(f'Error: {str(e)}')
                if filepath.exists():
                    os.remove(filepath)
                return render_template('index.html')

    return render_template('index.html', 
                       markdown_content=markdown_content,
                       token_count=token_count)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)