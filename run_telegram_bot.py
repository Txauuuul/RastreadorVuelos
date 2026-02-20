"""
run_telegram_bot.py - Ejecutar el Bot de Telegram

Este script inicia el bot de Telegram que permite:
- Agregar nuevas rutas (/agregar)
- Listar rutas activas (/listar)
- Buscar vuelos manualmente (/buscar)

USO:
    python run_telegram_bot.py
"""

import asyncio
import sys
from src.logger import logger
from src.database import inicializar_bd

async def main():
    try:
        # Inicializar BD
        logger.info("🔗 Inicializando base de datos...")
        inicializar_bd()
        
        # Importar y ejecutar bot
        from src.telegram_bot import iniciar_bot
        
        logger.info("🤖 Iniciando Bot de Telegram...")
        await iniciar_bot()
    
    except KeyboardInterrupt:
        logger.info("⛔ Bot detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
