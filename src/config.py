"""
config.py - Configuración centralizada del proyecto

Este módulo carga todas las variables de entorno y proporciona
una configuración única para toda la aplicación.

CONCEPTO EDUCATIVO:
Las variables de entorno es una BEST PRACTICE en producción porque:
- No hardcodeas secretos en el código
- Cambias configuración sin tocar código
- Es seguro para versionado Git (.env en .gitignore)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de .env
load_dotenv()

# ==================== RUTAS ====================
# Path base del proyecto (donde está config.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Rutas de carpetas importantes
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Crear carpetas si no existen
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ==================== BASE DE DATOS ====================
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "vuelos.db"))

# ==================== API AMADEUS ====================
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID", "")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET", "")

# Validar que tenemos las credenciales
if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
    raise ValueError(
        "❌ ERROR: Credenciales de Amadeus no están definidas en .env\n"
        "1. Copia .env.example a .env\n"
        "2. Obtén tus credenciales en: https://developers.amadeus.com/\n"
        "3. Rellena AMADEUS_CLIENT_ID y AMADEUS_CLIENT_SECRET en .env"
    )

# ==================== ALERTAS ====================
# Precio mínimo absoluto (€)
MIN_PRICE_THRESHOLD = float(os.getenv("MIN_PRICE_THRESHOLD", 50.0))

# Porcentaje de reducción respecto a la media histórica (%)
PRICE_REDUCTION_PERCENTAGE = float(os.getenv("PRICE_REDUCTION_PERCENTAGE", 15.0))

# ==================== LOGGING ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "rastreador.log"))

# ==================== NOTIFICACIONES TELEGRAM ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Validar que tenemos las credenciales de Telegram
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError(
        "❌ ERROR: Credenciales de Telegram no están definidas en .env\n"
        "1. Copia .env.example a .env\n"
        "2. Crea un bot en Telegram siguiendo los pasos documentados\n"
        "3. Rellena TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env"
    )

# ==================== DEBUG ====================
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

if __name__ == "__main__":
    # Este bloque se ejecuta si llamas: python src/config.py
    print("✅ Configuración cargada exitosamente")
    print(f"Base dir: {BASE_DIR}")
    print(f"DB path: {DB_PATH}")
    print(f"Amadeus configurado: {AMADEUS_CLIENT_ID[:10]}...")
