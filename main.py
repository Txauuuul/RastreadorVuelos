"""
main.py - Punto de entrada del Flight Tracker

Este es el archivo que ejecutarás para iniciar el rastreador.
Aquí se orquestan todos los módulos (API, BD, alertas, etc.)

MODO DE USO:
  - Local (desarrollo):   python main.py (con DEBUG=True en .env)
  - Nube (producción):    python main.py (con DEBUG=False en .env)
  - Gestionar vuelos:     python manage_flights.py
"""

import sys
import argparse
from pathlib import Path

# Agregar src al path para importar nuestros módulos
sys.path.insert(0, str(Path(__file__).parent))

from src.logger import logger
from src.config import DEBUG
from src.scheduler import FlightTrackerScheduler


def main():
    """Función principal del programa"""
    logger.info("=" * 70)
    logger.info("🛫 FLIGHT TRACKER - Rastreador de Vuelos")
    logger.info("=" * 70)
    
    if DEBUG:
        logger.debug("🧪 MODO DEBUG: Ejecutando un check único")
    else:
        logger.info("🌐 MODO PRODUCCIÓN: Iniciando scheduler 24/7")
    
    try:
        # Crear scheduler
        scheduler = FlightTrackerScheduler()
        
        # Ejecutar
        if DEBUG:
            # Un único check (para testing)
            scheduler.run_once()
            logger.info("✅ Check completado. Programa terminado.\n")
        else:
            # Loop infinito (para nube)
            scheduler.run()
    
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

