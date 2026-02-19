"""
main.py - Punto de entrada del Flight Tracker

ARQUITECTURA CORREGIDA (python-telegram-bot v20+):
- Thread Principal: Bot Telegram run_polling() 
- Thread Secundario 1: Servidor web dummy (puerto Render)
- Thread Secundario 2: Scheduler de búsquedas cada 2h

Nota CRÍTICA: La versión 20+ de python-telegram-bot REQUIERE que
Application.run_polling() corra en el thread principal.
Moverlo a un thread secundario rompe los callbacks internos del Updater.

MODO DE USO:
  - Local (desarrollo):   python main.py (con DEBUG=True en .env)
  - Nube (producción):    python main.py (con DEBUG=False en .env)
  - Gestionar vuelos:     python manage_flights.py
"""

import sys
import os
import argparse
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
    
    Esto mantiene a Render "contento" sabiendo que hay un puerto abierto.
    Se ejecuta en daemon thread para no bloquear el programa principal.
    """
    port = int(os.getenv('PORT', 10000))
    
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    logger.info(f"🌐 Health check server escuchando en puerto {port}")
    return server


def start_scheduler_thread():
    """
    Inicia el scheduler en un hilo secundario
    
    El scheduler busca vuelos cada 2 horas automáticamente.
    Se ejecuta como daemon thread para no bloquear el thread principal.
    
    CONCEPTO EDUCATIVO - Threading:
    Un daemon thread se detiene cuando el programa principal termina.
    Así no hay threads huérfanos.
    """
    try:
        scheduler = FlightTrackerScheduler()
        thread = threading.Thread(
            target=scheduler.run,
            daemon=True,
            name="SchedulerThread"
        )
        thread.start()
        logger.info("✅ Scheduler iniciado en thread secundario")
        return scheduler
    
    except Exception as e:
        logger.error(f"❌ Error iniciando scheduler: {e}")
        raise


def main():
    """
    Función principal - THREAD PRINCIPAL dedicado al Bot Telegram
    
    ARQUITECTURA:
    - Este thread ejecuta app.run_polling() (requerido para v20+ de python-telegram-bot)
    - Threads secundarios manejan servidor web y scheduler
    """
    logger.info("=" * 70)
    logger.info("🛫 FLIGHT TRACKER - Rastreador de Vuelos")
    logger.info("=" * 70)
    
    if DEBUG:
        logger.debug("🧪 MODO DEBUG: Ejecutando un check único")
    else:
        logger.info("🌐 MODO PRODUCCIÓN: Bot Telegram + Scheduler 24/7")
    
    try:
        # ====================================================================
        # MODO DEBUG: Solo ejecutar un check y salir
        # ====================================================================
        if DEBUG:
            logger.debug("\n📡 (DEBUG) Saltando servidor web...")
            logger.debug("⏱️ (DEBUG) Ejecutando scheduler una sola vez...")
            
            scheduler = FlightTrackerScheduler()
            scheduler.run_once()
            
            logger.info("✅ Check completado. Programa terminado.\n")
            return
        
        # ====================================================================
        # MODO PRODUCCIÓN: Iniciar todos los servicios
        # ====================================================================
        logger.info("\n🚀 INICIANDO SERVICIOS...\n")
        
        # PASO 1: Iniciar servidor web dummy (thread secundario)
        logger.info("📡 PASO 1: Iniciar servidor web...")
        start_health_check_server()
        
        # PASO 2: Iniciar scheduler (thread secundario)
        logger.info("⏱️ PASO 2: Iniciar scheduler de búsquedas...")
        start_scheduler_thread()
        
        # PEQUEÑA PAUSA para que los threads inicien
        time.sleep(0.5)
        
        # ====================================================================
        # PASO 3: Iniciar Bot Telegram (THREAD PRINCIPAL)
        # ====================================================================
        # ESTO ES CRÍTICO: El bot DEBE ejecutarse en el thread principal
        # para python-telegram-bot v20+. Si lo movemos a un thread secundario,
        # los callbacks internos del Updater se rompen.
        # ====================================================================
        
        logger.info("💬 PASO 3: Iniciar Bot Telegram en thread principal...\n")
        
        bot_commands = TelegramBotCommands()
        
        # Crear la aplicación del bot
        from telegram.ext import Application
        
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Registrar todos los handlers
        handlers = bot_commands.get_handlers()
        for handler in handlers:
            app.add_handler(handler)
        
        logger.info("✅ Bot Telegram inicializado con handlers")
        logger.info("🔔 Bot escuchando en polling...\n")
        logger.info("=" * 70)
        logger.info("✅ SISTEMA COMPLETAMENTE OPERATIVO")
        logger.info("=" * 70)
        logger.info("- Servidor web: puerto 10000")
        logger.info("- Scheduler: búsquedas cada 2 horas")
        logger.info("- Bot Telegram: escuchando comandos")
        logger.info("=" * 70 + "\n")
        
        # EJECUTAR EL BOT EN EL THREAD PRINCIPAL
        # Este es el evento bloqueante que mantiene el programa corriendo
        app.run_polling(allowed_updates=None)
    
    except KeyboardInterrupt:
        logger.info("\n⏹️ Programa detenido por el usuario\n")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}\n")
        import traceback
        traceback.print_exc()
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

