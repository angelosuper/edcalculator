"""Backend module initialization"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the backend directory is in the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
    logger.info(f"Added backend directory to Python path: {backend_dir}")

try:
    from . import database
    from . import models
    from . import schemas
    from . import api

    logger.info("Successfully imported all backend modules")

    __all__ = ['database', 'models', 'schemas', 'api']
except Exception as e:
    logger.error(f"Error importing backend modules: {str(e)}")
    raise