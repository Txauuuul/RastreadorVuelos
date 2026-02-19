"""
logger.py - Sistema centralizado de logging

CONCEPTO EDUCATIVO: Logging vs Print
- print(): Para debugging rápido, no es profesional
- logging: Para aplicaciones reales, permite guardar registro de todo

Niveles de log (de menos a más grave):
- DEBUG: Información para desarrolladores
- INFO: Información general
- WARNING: Algo podría estar mal
- ERROR: Algo salió mal
- CRITICAL: El programa podría fallar
"""

import logging
from pathlib import Path
from src.config import LOG_FILE, LOG_LEVEL, DEBUG

# Crear carpeta de logs si no existe
Path(LOG_FILE).parent.mkdir(exist_ok=True)

# Crear logger
logger = logging.getLogger("FlightTracker")
logger.setLevel(LOG_LEVEL)

# Formato: [2025-02-19 14:30:45] [INFO] mensaje
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler: guardar en archivo
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler: mostrar en consola también
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

if __name__ == "__main__":
    logger.debug("Este es un mensaje DEBUG")
    logger.info("Este es un mensaje INFO")
    logger.warning("Este es un mensaje WARNING")
    logger.error("Este es un mensaje ERROR")
