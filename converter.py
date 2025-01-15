import tiktoken
import PyPDF2
from pathlib import Path
from typing import Callable, Optional
import re

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

            for page_num in range(total_pages):
                if progress_callback:
                    progress_callback(page_num + 1, total_pages)

                page = pdf_reader.pages[page_num]
                text = page.extract_text()

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

    def _clean_whitespace(self, text: str) -> str:
        """Gereksiz boşlukları temizler."""
        # Ardışık boş satırları tekil boş satıra dönüştür
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Satır sonlarındaki boşlukları temizle
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        return text.strip()