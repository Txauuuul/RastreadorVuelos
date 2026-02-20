"""
run_combined.py - Ejecutar Bot + Worker en PARALELO (ideal para Render)

Este script combina ambos procesos en UN SOLO PROGRAMA:
- Bot de Telegram (escucha en background)
- Search Worker (busca cada 5 horas en background)

USO LOCAL (desarrollo - sin necesidad de 2 terminales):
    python run_combined.py

USO EN RENDER (producción - 1 dyno = 1 comando):
    En Procfile: worker: python run_combined.py
    O en Render: Command: python run_combined.py

VENTAJAS:
✅ UN SOLO proceso necesario
✅ Funciona perfecto en Render (1 dyno)
✅ Sin necesidad de 2 terminales
✅ Usuario no necesita instrucciones complicadas
✅ Logs combinados y ordenados

CONCEPTO EDUCATIVO - Event Loop Unificado:
Ambos procesos (bot + worker) corren en el MISMO event loop asyncio.
Es como tener 2 "tareas" corriendo concurrentemente pero en el mismo thread.
Ambas pueden "esperar" sin bloquear la otra.
"""

import asyncio
import sys
from src.logger import logger
from src.database import inicializar_bd

async def main():
    try:
        # Inicializar BD una sola vez
        logger.info("🔗 Inicializando base de datos (único para ambos procesos)...")
        inicializar_bd()
        logger.info("✅ Base de datos inicializada")
        
        # Importar módulos (DESPUÉS de inicializar BD)
        from src.telegram_bot import iniciar_bot
        from src.flight_search_worker import iniciar_buscador_automatico
        
        logger.info("=" * 60)
        logger.info("🚀 FLIGHT TRACKER - MODO COMBINADO (Bot + Buscador)")
        logger.info("=" * 60)
        logger.info("📱 Bot de Telegram escuchando...")
        logger.info("⏰ Buscador automático: cada 5 horas")
        logger.info("=" * 60)
        
        # CONCEPTO EDUCATIVO - asyncio.gather():
        # Ejecuta múltiples funciones asincrónicas CONCURRENTEMENTE
        # Si una está esperando (await), la otra puede ejecutarse
        # Es como tener 2 procesos en paralelo en el mismo thread
        
        # Crear tareas
        bot_task = asyncio.create_task(iniciar_bot())
        worker_task = asyncio.create_task(iniciar_buscador_automatico())
        
        # Ejecutar ambas concurrentemente
        # Si una falla, mostrar el error pero continuar
        await asyncio.gather(
            bot_task,
            worker_task,
            return_exceptions=True  # Continuar si una falla
        )
    
    except KeyboardInterrupt:
        logger.info("⛔ Flight Tracker detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
