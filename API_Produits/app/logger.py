# Fichier accueillant la configuration des différents logs
import logging
import sys
import os


def setup_logger(name: str):
    """
    Configure un logger avec un format standardisé.

    Args:
        name (str): Nom du logger (ex: 'api', 'worker', 'producer')

    Returns:
        logging.Logger: Logger configuré
    """
    # Format des logs : date [niveau] [nom du service] message
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # On envoie les logs sur la sortie standard (affichée dans Docker)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Création du logger
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))  # Par défaut : INFO
    logger.addHandler(handler)
    logger.propagate = False  # Évite les doublons de logs

    return logger
