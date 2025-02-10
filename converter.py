import tiktoken
import PyPDF2
from pathlib import Path
from typing import Callable, Optional, List, Tuple
import re
import pytesseract
from PIL import Image
import io
import zipfile

class PDFConverter:
    def __init__(self, logger):
        self.logger = logger
        # GPT-3.5-turbo için tiktoken encoder'ı
        self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def count_tokens(self, text: str) -> int:
        """GPT-3.5-turbo modeli için token sayısını hesaplar."""
        try:
            # Metni tokenlara böl
            tokens = self.encoder.encode(text)
            return len(tokens)
        except Exception as e:
            self.logger.error(f"Token sayımı sırasında hata: {e}")
            return 0

    def convert_pdf(self, 
                   pdf_path: Path, 
                   progress_callback: Optional[Callable] = None) -> tuple[str, int]:
        """PDF dosyasını Markdown'a dönüştürür ve token sayısını döndürür."""
        self.logger.info(f"'{pdf_path}' dönüştürülüyor...")

        markdown_content = []
        total_tokens = 0

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            # Extract images and perform OCR
            self.logger.info("Extracting images and performing OCR...")
            images = self.extract_images(pdf_path)
            ocr_text = []
            for _, image_data in images:
                text = self.perform_ocr(image_data)
                if text.strip():
                    ocr_text.append(text)
            if ocr_text:
                self.logger.info(f"Found {len(ocr_text)} text blocks from OCR")

            for page_num in range(total_pages):
                if progress_callback:
                    progress_callback(page_num + 1, total_pages)

                page = pdf_reader.pages[page_num]
                try:
                    text = str(page.extract_text())
                    # Add OCR text if available for this page
                    if ocr_text:
                        text += "\n\n### OCR Text from Images\n\n" + "\n\n".join(ocr_text)
                except Exception as e:
                    self.logger.error(f"Sayfa {page_num + 1} metin çıkarma hatası: {e}")
                    text = ""  # Hata durumunda boş metin döndür

                # Markdown formatlaması
                formatted_text = self._format_text(text)
                markdown_content.append(formatted_text)

                # Token sayısını hesapla
                page_tokens = self.count_tokens(formatted_text)
                total_tokens += page_tokens
                self.logger.debug(f"Sayfa {page_num + 1}: {page_tokens:,} token")

                self.logger.debug(f"Sayfa {page_num + 1} dönüştürüldü")

        final_markdown = "\n\n".join(markdown_content)
        # Son bir kez tüm metin için token sayısını hesapla
        total_tokens = self.count_tokens(final_markdown)
        
        return final_markdown, total_tokens

    def _format_text(self, text: str) -> str:
        """Metni Markdown formatına dönüştürür."""
        # Başlıkları işle
        text = self._process_headers(text)

        # Listeleri işle
        text = self._process_lists(text)

        # Tabloları işle
        text = self._process_tables(text)

        # Gereksiz boşlukları temizle
        text = self._clean_whitespace(text)

        return text

    def _process_headers(self, text: str) -> str:
        """Başlıkları Markdown formatına dönüştürür."""
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            # Başlık olabilecek satırları tespit et
            stripped = line.strip()
            if stripped and len(stripped) < 100:  # Makul uzunlukta
                if stripped.isupper():  # Tümü büyük harfse muhtemelen başlık
                    processed_lines.append(f"# {stripped.title()}")
                    continue

            processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _process_lists(self, text: str) -> str:
        """Liste öğelerini Markdown formatına dönüştürür."""
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            # Madde işaretli listeleri tespit et
            if re.match(r'^\s*[•·⋅∙○●]\s+', line):
                line = re.sub(r'^\s*[•·⋅∙○●]\s+', '- ', line)
            # Numaralı listeleri tespit et
            elif re.match(r'^\s*\d+[\.\)]\s+', line):
                line = re.sub(r'^\s*(\d+[\.\)])\s+', r'\1 ', line)

            processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _process_tables(self, text: str) -> str:
        """Tablo yapısını Markdown formatına dönüştürür."""
        # Basit tablo tespiti
        lines = text.split('\n')
        in_table = False
        table_lines = []
        processed_lines = []

        for line in lines:
            if '|' in line or '\t' in line:
                if not in_table:
                    in_table = True
                table_lines.append(line)
            else:
                if in_table:
                    if table_lines:
                        processed_lines.extend(self._convert_table_to_markdown(table_lines))
                        table_lines = []
                    in_table = False
                processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _convert_table_to_markdown(self, table_lines: list) -> list:
        """Tablo satırlarını Markdown tablo formatına dönüştürür."""
        # Tab karakterli tabloları pipe karakterine dönüştür
        table_lines = [line.replace('\t', ' | ') for line in table_lines]

        # Markdown tablo formatı oluştur
        markdown_table = []
        header = table_lines[0]
        markdown_table.append(f"|{header}|")

        # Ayraç satırı ekle
        separator = "|" + "|".join(["---" for _ in header.split('|')]) + "|"
        markdown_table.append(separator)

        # Diğer satırları ekle
        for line in table_lines[1:]:
            markdown_table.append(f"|{line}|")

        return markdown_table

    def extract_images(self, pdf_path: Path) -> List[Tuple[str, bytes]]:
        """Extract images from PDF with names and data"""
        images = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf.pages):
                    if '/Resources' in page and '/XObject' in page['/Resources']:
                        xObject = page['/Resources']['/XObject']
                        if hasattr(xObject, 'get_object'):
                            xObject = xObject.get_object()
                        for obj_name, obj in xObject.items():
                            if hasattr(obj, 'get_object'):
                                obj = obj.get_object()
                            if obj.get('/Subtype') in ['/Image', '/Form']:
                                try:
                                    data = obj.get_data()
                                    # Skip invalid images (data size < 100 bytes)
                                    if len(data) < 100:
                                        self.logger.warning(f"Skipping invalid image {obj_name} on page {page_num + 1} (size: {len(data)} bytes)")
                                        continue
                                    name = f"image_{page_num}_{obj_name}.png"
                                    images.append((name, data))
                                    self.logger.info(f"Extracted image {name} from page {page_num + 1} (size: {len(data)} bytes)")
                                except Exception as e:
                                    self.logger.error(f"Error extracting {obj_name} from page {page_num + 1}: {e}")
        except Exception as e:
            self.logger.error(f"Error processing PDF for image extraction: {e}")
        return images

    def create_image_zip(self, images: List[Tuple[str, bytes]]) -> bytes:
        """Create ZIP file containing extracted images"""
        try:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for name, data in images:
                    zip_file.writestr(name, data)
            return zip_buffer.getvalue()
        except Exception as e:
            self.logger.error(f"Error creating ZIP file: {e}")
            return b""

    def perform_ocr(self, image_data: bytes) -> str:
        """Perform OCR on image data"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return pytesseract.image_to_string(image)
        except Exception as e:
            self.logger.error(f"Error performing OCR: {e}")
            return ""
    def _clean_whitespace(self, text: str) -> str:
        """Gereksiz boşlukları temizler."""
        # Ardışık boş satırları tekil boş satıra dönüştür
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Satır sonlarındaki boşlukları temizle
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        return text.strip()
