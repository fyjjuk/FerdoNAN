import logging
import sys
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
from core.tracing import get_request_id

# Silenciar warnings molestos
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*CUDA initialization.*")
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")

class FerdonanLogger:
    def __init__(self):
        self.logger = logging.getLogger("ferdonan")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
            file_handler = RotatingFileHandler("logs/ferdonan.log", maxBytes=5*1024*1024, backupCount=5)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            # Solo logs de INFO o superior en consola, menos ruido
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

# Instancia exportable
instance = FerdonanLogger()
logger = instance.logger

# Silenciar loggers de otras librerías
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
