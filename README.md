# PDF to Markdown Converter with OCR & Image Extraction

![PDF to Markdown](screen1.png)
![PDF to Markdown](screen2.png)
A powerful web-based PDF to Markdown converter that combines OCR technology with advanced image extraction capabilities. Convert your PDF files to Markdown format while preserving images and extracting text from scanned documents. Perfect for researchers, developers, and content creators who need to convert complex PDFs with images and tables into clean, structured Markdown.


## ✨ Features

- 📄 Smart Document Processing
  - Drag-and-drop file upload
  - Fast conversion process
  - Automatic table format conversion
  - Precise header and list detection
  
- 🔍 Advanced OCR & Image Handling
  - OCR support for scanned documents
  - Automatic image extraction
  - Image preview in grid layout
  - Bulk image download as ZIP
  
- 📊 Performance & Analytics
  - Smart token calculation
  - Real-time processing feedback
  - Conversion progress tracking
  
- 💫 User Experience
  - One-click copy functionality
  - Mobile-responsive interface
  - Clean, modern UI design
  - Secure file handling

## 🛠️ Technologies

- Backend
  - Python Flask for web server
  - PyPDF2 for PDF processing
  - Tesseract OCR for image text extraction
  - Rich for terminal UI and logging
  
- Frontend
  - Modern HTML5/CSS3/JavaScript
  - Bootstrap 5 for responsive design
  - Base64 image encoding for secure display
  - Dynamic grid layout for images

## 🚀 Installation

1. Prerequisites:
   - Python 3.8 or higher
   - [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html)
   - Git

2. Setup:
   ```bash
   # Clone repository
   git clone https://github.com/U-C4N/PDFtoLLM.git
   cd PDFtoLLM

   # Install dependencies
   python -m pip install -r requirements.txt

   # Start application
   python app.py
   ```

3. Configure and run:
   ```bash
   # Set environment variables (optional)
   export FLASK_ENV=development
   export PORT=8080  # or your preferred port

   # Start application
   python app.py
   ```

4. Access the application in your browser at the URL shown in the console output

## 💡 Usage

1. Open the application in your browser
2. Drag and drop or select your PDF file
3. Click the "Convert" button to process the PDF:
   - Text is converted to Markdown format
   - Images are automatically extracted
   - OCR is applied to scanned text
4. View and manage the results:
   - Copy the generated Markdown content
   - Browse extracted images in the grid view
   - Download all images as a ZIP file
5. Track token usage and processing statistics

## 🔜 Upcoming Features

- [x] OCR support for scanned documents
- [x] Image extraction and management
- [ ] Batch file processing support
- [ ] Custom OCR language support
- [ ] Enhanced table detection with image tables
- [ ] Markdown preview with image rendering
- [ ] PDF annotation extraction
- [ ] Custom formatting templates

## Author

<p align="left">
<b>Umutcan Edizaslan:</b>
<a href="https://github.com/U-C4N" target="blank"><img align="center" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Github-Dark.svg" alt="TutTrue" height="30" width="40" /></a>
<a href="https://x.com/UEdizaslan" target="blank"><img align="center" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Twitter.svg" height="30" width="40" /></a>
<a href="https://discord.gg/2Tutcj6u" target="blank"><img align="center" src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Discord.svg" height="30" width="40" /></a>
</p>

## 📝 License

This project is licensed under the [MIT](LICENSE) license.
