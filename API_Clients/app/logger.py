import logging
import os
import sys

def setup_logger(name: str):
    """
    Configure un logger standardisé pour toute l'application
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger