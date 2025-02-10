import logging
from rich.progress import Progress, TaskID
from typing import Callable
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    ProgressColumn,
    TimeRemainingColumn,
    TextColumn,
    TaskProgressColumn,
)

def setup_logger(debug: bool = False) -> logging.Logger:
    """Logging yapılandırmasını oluşturur."""
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    logger = logging.getLogger("pdf2md")
    return logger

def create_progress_bar(progress: Progress) -> Callable:
    """İlerleme çubuğu oluşturur ve callback fonksiyonu döndürür."""
    task = progress.add_task(
        "[cyan]Dönüştürülüyor...",
        total=None
    )
    
    def update_progress(current: int, total: int) -> None:
        if progress.tasks[task].total != total:
            progress.update(task, total=total)
        progress.update(task, completed=current)
    
    return update_progress
