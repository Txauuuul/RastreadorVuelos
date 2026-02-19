"""
main.py - Punto de entrada del Flight Tracker

Este es el archivo que ejecutarás para iniciar el rastreador.
Aquí se orquestan todos los módulos (API, BD, alertas, etc.)

MODO DE USO:
  - Local (desarrollo):   python main.py (con DEBUG=True en .env)
  - Nube (producción):    python main.py (con DEBUG=False en .env)
  - Gestionar vuelos:     python manage_flights.py

MODO DE EJECUCIÓN:
  - El bot Telegram corre en polling (escuchando comandos)
  - El scheduler corre en paralelo (buscando vuelos cada 2h)
  - Servidor web dummy escucha en puerto Render (para detect active process)
"""

import sys
import os
import argparse
import asyncio
import threading
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Agregar src al path para importar nuestros módulos
sys.path.insert(0, str(Path(__file__).parent))

from src.logger import logger
from src.config import DEBUG, TELEGRAM_BOT_TOKEN
from src.scheduler import FlightTrackerScheduler
from src.telegram_commands import TelegramBotCommands


# ============================================================================
# SERVIDOR WEB DUMMY (para Render)
# ============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """
    Handler HTTP simple que responde a health checks
    Esto mantiene a Render "contento" sabiendo que hay un puerto abierto
    """
    
    def do_GET(self):
        """Responder a GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running\n')
    
    def log_message(self, format, *args):
        """Silenciar logs del servidor HTTP"""
        pass


def start_health_check_server():
    """
    Inicia servidor web en un hilo secundario
    
    CONCEPTO EDUCATIVO - Threading:
    Un thread permite ejecutar código en paralelo sin bloquear.
    Así el bot y el scheduler pueden correr simultáneamente.
    """
    port = int(os.getenv('PORT', 10000))
    
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    logger.info(f"🌐 Health check server escuchando en puerto {port}")
    return server


def main():
    """Función principal del programa"""
    logger.info("=" * 70)
    logger.info("🛫 FLIGHT TRACKER - Rastreador de Vuelos")
    logger.info("=" * 70)
    
    if DEBUG:
        logger.debug("🧪 MODO DEBUG: Ejecutando un check único")
    else:
        logger.info("🌐 MODO PRODUCCIÓN: Iniciando scheduler 24/7 + Bot Telegram")
    
    try:
        # PASO 1: Iniciar servidor web dummy (para Render)
        logger.info("\n📡 PASO 1: Preparar servidor web...")
        start_health_check_server()
        
        # PASO 2: Iniciar el scheduler (búsquedas cada 2h)
        logger.info("\n⏱️ PASO 2: Iniciar scheduler de búsquedas...")
        scheduler = FlightTrackerScheduler()
        
        # PASO 3: Iniciar el bot Telegram
        logger.info("\n💬 PASO 3: Iniciar bot de Telegram...")
        bot_commands = TelegramBotCommands()
        
        # En modo DEBUG, solo ejecutar un check
        if DEBUG:
            scheduler.run_once()
            logger.info("✅ Check completado. Programa terminado.\n")
        else:
            # MODO PRODUCCIÓN: Correr scheduler y bot en paralelo
            logger.info("\n🚀 INICIADO - Scheduler + Bot Telegram ejecutándose\n")
            
            # Hilo 1: Scheduler (búsquedas cada 2 horas)
            scheduler_thread = threading.Thread(
                target=scheduler.run,
                daemon=True,
                name="SchedulerThread"
            )
            scheduler_thread.start()
            logger.info("✅ Scheduler iniciado en thread secundario")
            
            # Hilo 2: Bot Telegram (polling permanente)
            try:
                async def run_bot():
                    """Correr el bot Telegram con polling"""
                    from telegram.ext import Application
                    
                    # Crear application
                    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
                    
                    # Registrar handlers de comandos
                    handlers = bot_commands.get_handlers()
                    for handler in handlers:
                        app.add_handler(handler)
                    
                    logger.info("✅ Bot Telegram inicializado con handlers")
                    
                    # Ejecutar polling
                    logger.info("🔔 Bot escuchando en polling...")
                    async with app:
                        await app.start()
                        
                        # Mantener el bot corriendo
                        while True:
                            await asyncio.sleep(1)
                        
                        await app.stop()
                
                # Correr el bot en el event loop actual
                asyncio.run(run_bot())
            
            except KeyboardInterrupt:
                logger.info("\n⏹️ Programa detenido por el usuario")
            except Exception as e:
                logger.error(f"❌ Error en bot Telegram: {e}")
                raise
    
    except KeyboardInterrupt:
        logger.info("\n⏹️ Programa detenido por el usuario\n")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}\n")
        sys.exit(1)


def cli_interface():
    """Interfaz de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="🛫 Flight Tracker - Rastreador de Vuelos"
    )
    
    parser.add_argument(
        '--mode',
        choices=['run', 'test', 'manage'],
        default='run',
        help='Modo de ejecución: run (default), test, manage'
    )
    
    parser.add_argument(
        '--check-once',
        action='store_true',
        help='Ejecutar un único check y salir'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'manage':
        # Ejecutar gestor de vuelos
        import manage_flights
        manage_flights.main()
    elif args.mode == 'test':
        # Ejecutar pruebas
        logger.info("🧪 Ejecutando pruebas del sistema...\n")
        scheduler = FlightTrackerScheduler()
        scheduler.run_once()
    else:
        # Modo normal
        main()


if __name__ == "__main__":
    # Si se pasan argumentos, usar CLI
    if len(sys.argv) > 1:
        cli_interface()
    else:
        # Comportamiento normal
        main()

