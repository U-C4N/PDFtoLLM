#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

from converter import PDFConverter
from console import setup_logger, create_progress_bar
from utils import validate_file, ensure_output_dir

def main():
    parser = argparse.ArgumentParser(
        description="PDF dosyalarını Markdown formatına dönüştürür"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Dönüştürülecek PDF dosyası"
    )
    parser.add_argument(
        "-o", 
        "--output",
        type=str,
        help="Çıktı dosyası (varsayılan: input_file.md)",
        default=None
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug modunu aktifleştirir"
    )

    args = parser.parse_args()
    
    console = Console()
    logger = setup_logger(debug=args.debug)

    try:
        # Girdi dosyasını doğrula
        input_path = validate_file(args.input_file)
        
        # Çıktı dosyası yolu
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix('.md')
        
        ensure_output_dir(output_path)

        # Dönüştürücüyü başlat
        converter = PDFConverter(logger)
        
        with Progress() as progress:
            # PDF'i oku ve dönüştür
            markdown_content, token_count = converter.convert_pdf(
                input_path,
                progress_callback=create_progress_bar(progress)
            )
            
            # Markdown dosyasını kaydet
            output_path.write_text(markdown_content, encoding='utf-8')
            
            console.print(f"\n[green]Dönüştürme tamamlandı![/green]")
            console.print(f"Çıktı dosyası: {output_path}")
            console.print(f"Toplam token sayısı: {int(token_count):,}")

    except Exception as e:
        console.print(f"[red]Hata: {str(e)}[/red]")
        logger.exception("İşlem sırasında hata oluştu")
        sys.exit(1)

if __name__ == "__main__":
    main()
