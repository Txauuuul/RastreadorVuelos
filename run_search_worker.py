"""
run_search_worker.py - Ejecutar el Buscador Automático de Vuelos

Este script inicia el motor de búsqueda que:
- Busca vuelos cada 5 horas automáticamente
- Guarda precios en la BD
- Detecta ofertas
- Envía alertas a Telegram

USO:
    python run_search_worker.py

PARA USAR CON UPTIMEROBOT:
    Configura UptimeRobot para hacer ping a tu servidor web cada 5 minutos.
    El bot/worker deben estar corriendo en background (ej: PM2, supervisor, etc)
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
        
        # Importar y ejecutar worker
        from src.flight_search_worker import iniciar_buscador_automatico
        
        logger.info("🔄 Iniciando Buscador Automático de Vuelos...")
        logger.info("⏰ Buscará cada 5 horas")
        logger.info("💡 NOTA: Para prevenir sleep en Render, usa UptimeRobot")
        
        await iniciar_buscador_automatico(intervalo_segundos=5*3600)  # 5 horas
    
    except KeyboardInterrupt:
        logger.info("⛔ Buscador detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
