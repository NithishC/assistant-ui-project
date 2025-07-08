import logging
from logging.handlers import RotatingFileHandler
import os

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'backend.log')

# Configure root logger
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s'
))

logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[file_handler, console_handler],
    force=True  # Overwrite any prior config
)

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance with the given name (or root if None)"""
    return logging.getLogger(name) 