from pathlib import Path
import os

def validate_file(file_path: str) -> Path:
    """Dosya yolunu doğrular ve Path nesnesini döndürür."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Belirtilen yol bir dosya değil: {file_path}")
        
    if path.suffix.lower() != '.pdf':
        raise ValueError(f"Dosya PDF formatında değil: {file_path}")
    
    return path

def ensure_output_dir(output_path: Path) -> None:
    """Çıktı dizininin var olduğundan emin olur."""
    output_dir = output_path.parent
    
    if not output_dir.exists():
        os.makedirs(output_dir)
    
    if output_path.exists():
        raise FileExistsError(f"Çıktı dosyası zaten mevcut: {output_path}")
