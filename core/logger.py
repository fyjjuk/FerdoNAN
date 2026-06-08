import logging
import sys
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
from core.tracing import get_request_id

class FerdonanLogger:
    def __init__(self):
        self.logger = logging.getLogger("ferdonan")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
            file_handler = RotatingFileHandler("logs/ferdonan.log", maxBytes=5*1024*1024, backupCount=5)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

# Instancia exportable
instance = FerdonanLogger()
logger = instance.logger
