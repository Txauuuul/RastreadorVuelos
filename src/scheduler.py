"""
scheduler.py - Ejecutar búsquedas de precios automáticamente

CONCEPTO EDUCATIVO - Scheduler:
Un scheduler es como un "reloj" en tu programa que ejecuta tareas cada X tiempo.
Sin un scheduler, tendrías que ejecutar el programa manualmente.
"""

import schedule
import time
from datetime import datetime
from src.logger import logger


def buscar_precios():
    """Función que se ejecuta cada X horas"""
    logger.info("=" * 60)
    logger.info("🔍 INICIO DE BÚSQUEDA DE PRECIOS")
    logger.info(f"⏰ Timestamp: {datetime.utcnow().isoformat()}")
    logger.info("=" * 60)
    
    try:
        # AQUÍ IRÁ LA LÓGICA COMPLETA:
        # 1. Obtener rutas activas de la BD PostgreSQL
        # 2. Para cada ruta, buscar en Amadeus + Kiwi.com
        # 3. Guardar precios en historial
        # 4. Evaluar alertas
        # 5. Enviar notificaciones por Telegram
        
        logger.info("✅ Búsqueda completada exitosamente")
    
    except Exception as e:
        logger.error(f"❌ Error durante la búsqueda: {e}", exc_info=True)


def configurar_scheduler(intervalo_horas: int = 2):
    """
    Configura el scheduler para ejecutar búsquedas cada N horas
    
    Args:
        intervalo_horas: Cada cuántas horas buscar (default: 2)
    """
    logger.info(f"⏰ Configurando scheduler: búsqueda cada {intervalo_horas} horas")
    schedule.every(intervalo_horas).hours.do(buscar_precios)
    logger.info(f"✅ Scheduler configurado")


def iniciar_scheduler():
    """Inicia el scheduler (corre infinitamente)"""
    logger.info("🚀 Iniciando scheduler perpetuo...")
    
    # Ejecutar primera búsqueda inmediatamente
    buscar_precios()
    
    # Loop: revisar cada 10 segundos si hay tareas pendientes
    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
        self.api = api or AmadeusAPI()
        self.db = db or Database()
        self.notifier = telegram_notifier or TelegramNotifier()
        
        # Crear componentes derivados
        self.detector = AlertDetector(self.db)
        self.analyzer = AlertAnalyzer(self.db)
        self.notification_manager = NotificationManager(
            telegram_notifier=self.notifier,
            db=self.db
        )
        
        # Estado del scheduler
        self.is_running = False
        self.execution_count = 0
        self.last_check_time = None
        
        logger.info("✅ Flight Tracker Scheduler inicializado")
    
    def schedule_jobs(self):
        """
        Programar los trabajos (jobs) periódicos
        
        CONCEPTO EDUCATIVO - Scheduling:
        `schedule` es una librería simple pero poderosa para
        ejecutar tasks en momentos específicos.
        
        Sintaxis:
        - schedule.every(2).hours.do(funcion) → Cada 2 horas
        - schedule.every().day.at("09:00").do(funcion) → A las 9:00 diarias
        - schedule.every().minute.do(funcion) → Cada minuto
        """
        
        logger.info("📅 Programando trabajos periódicos...")
        
        # Job 1: Buscar y detectar alertas cada 2 horas
        schedule.every(2).hours.do(self.check_flights_and_alert)
        logger.info("   ✅ Check each 2 hours programado")
        
        # Job 2: Enviar reporte diario a las 9:00
        schedule.every().day.at("09:00").do(self.send_daily_report)
        logger.info("   ✅ Daily report at 09:00 programado")
        
        # Job 3: Limpiar datos antiguos cada 30 días (mantiene 30 días de historial)
        schedule.every(30).days.do(self.cleanup_old_data)
        logger.info("   ✅ Cleanup cada 30 días programado")
        
        # Job 4: Guardar estadísticas cada hora
        schedule.every(1).hours.do(self.log_statistics)
        logger.info("   ✅ Statistics hourly programado")
        
        logger.info("✅ Todos los trabajos están programados")
    
    def check_flights_and_alert(self):
        """
        JOB PRINCIPAL: Buscar vuelos, detectar alertas, enviar notificaciones
        
        Este es el flujo core del sistema:
        API → BD → Detectar Alertas → Enviar Notificaciones → Registrar
        """
        self.execution_count += 1
        self.last_check_time = datetime.now()
        
        logger.info("=" * 70)
        logger.info(f"🔄 CHECK #{self.execution_count} - {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        try:
            # PASO 1: Obtener vuelos monitoreados
            logger.info("\n📋 PASO 1: Obtener vuelos monitoreados")
            flights = self.db.get_all_watched_flights()
            
            if not flights:
                logger.warning("⚠️ No hay vuelos monitoreados. Agrega algunos primero.")
                return
            
            logger.info(f"✅ {len(flights)} vuelo(s) a revisar")
            
            # PASO 2: Para cada vuelo, buscar precios actuales
            logger.info("\n🔍 PASO 2: Buscar precios actuales en Amadeus")
            
            for flight in flights:
                flight_id = flight['id']
                origin = flight['origin']
                destination = flight['destination']
                departure_date = flight['departure_date']
                
                try:
                    # Buscar vuelos en Amadeus
                    result = self.api.search_flights(
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date,
                        adults=1
                    )
                    
                    if result and result['flights']:
                        # Guardar el precio más barato encontrado
                        min_price_flight = min(result['flights'], 
                                              key=lambda x: x['price'])
                        
                        # Registrar en BD
                        self.db.add_price_record(
                            flight_id=flight_id,
                            price=min_price_flight['price'],
                            currency=min_price_flight['currency'],
                            airline=min_price_flight['airline'],
                            flight_number=min_price_flight['flight_number']
                        )
                        
                        logger.info(
                            f"✅ {origin}→{destination}: "
                            f"{min_price_flight['price']}€ "
                            f"({min_price_flight['airline']})"
                        )
                    else:
                        logger.warning(f"⚠️ No se encontraron vuelos: {origin}→{destination}")
                
                except Exception as e:
                    logger.error(f"❌ Error buscando {origin}→{destination}: {e}")
                    continue
            
            # PASO 3: Detectar alertas
            logger.info("\n🚨 PASO 3: Detectar alertas")
            alerts = self.detector.check_all_flights()
            
            if alerts:
                logger.info(f"✅ {len(alerts)} alerta(s) detectada(s)")
            else:
                logger.info("✅ No hay alertas en este momento")
            
            # PASO 4: Enviar notificaciones
            logger.info("\n📤 PASO 4: Enviar notificaciones")
            
            if alerts:
                stats = self.notification_manager.process_alerts(alerts)
                logger.info(f"✅ {stats['sent']} alerta(s) enviada(s), {stats['failed']} fallida(s)")
            else:
                logger.info("ℹ️ Sin alertas para enviar")
            
            logger.info("\n✅ Check completado exitosamente\n")
        
        except Exception as e:
            logger.error(f"❌ Error crítico en check: {e}")
    
    def send_daily_report(self):
        """
        JOB: Enviar reporte diario de actividad
        """
        logger.info("\n" + "=" * 70)
        logger.info("📊 REPORTE DIARIO")
        logger.info("=" * 70)
        
        try:
            stats = self.notification_manager.get_stats()
            
            message = (
                f"📊 <b>Reporte Diario</b>\n\n"
                f"🔆 <b>Hoy:</b> {stats.get('alerts_today', 0)} alerta(s)\n"
                f"📈 <b>Últimos 30 días:</b> {stats.get('total_alerts_30days', 0)} alerta(s)\n\n"
                f"⏰ <i>Próximo reporte: Mañana a las 09:00</i>"
            )
            
            self.notifier.send_custom_message(message)
            logger.info("✅ Reporte diario enviado\n")
        
        except Exception as e:
            logger.error(f"❌ Error enviando reporte: {e}")
    
    def cleanup_old_data(self):
        """
        JOB: Limpiar datos antiguos de la BD (más de 30 días)
        
        Mantiene 30 días de historial para análisis de tendencias
        """
        logger.info("\n" + "=" * 70)
        logger.info("🧹 LIMPIEZA DE DATOS ANTIGUOS (>30 días)")
        logger.info("=" * 70)
        
        try:
            deleted = self.db.clear_old_data(days=30)
            logger.info(f"✅ Se eliminaron {deleted} registros antiguos\n")
        
        except Exception as e:
            logger.error(f"❌ Error limpiando datos: {e}")
    
    def log_statistics(self):
        """
        JOB: Registrar estadísticas del sistema
        """
        try:
            stats = self.db.get_statistics()
            logger.debug(
                f"📊 Stats: "
                f"{stats['active_flights']} vuelos activos, "
                f"{stats['price_records']} registros de precio, "
                f"{stats['alerts_sent']} alertas enviadas"
            )
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats: {e}")
    
    def run(self):
        """
        Iniciar el scheduler en modo daemon
        
        CONCEPTO EDUCATIVO - Event Loop:
        Este es el corazón del programa. Un loop infinito que:
        1. Verifica si hay jobs pendientes
        2. Los ejecuta si llega la hora
        3. Duerme un segundo antes de revisar de nuevo
        
        Se ejecuta hasta que el usuario lo detiene (Ctrl+C)
        """
        self.is_running = True
        
        # Programar los trabajos
        self.schedule_jobs()
        
        logger.info("\n" + "=" * 70)
        logger.info("🚀 FLIGHT TRACKER INICIADO")
        logger.info("=" * 70)
        logger.info("Press Ctrl+C to stop\n")
        
        try:
            # Ejecutar un check inicial
            self.check_flights_and_alert()
            
            # Loop principal
            while True:
                # Ejecutar jobs pendientes
                schedule.run_pending()
                
                # Dormir 60 segundos antes de la siguiente revisión
                time.sleep(60)
        
        except KeyboardInterrupt:
            logger.info("\n\n⏹️ Flight Tracker detenido por el usuario")
            self.is_running = False
        
        except Exception as e:
            logger.error(f"\n❌ Error fatal: {e}")
            self.is_running = False
            raise
    
    def run_once(self):
        """
        Ejecutar un único check (útil para testing)
        """
        logger.info("🔄 Ejecutando un check único (sin scheduler)...")
        self.check_flights_and_alert()
    
    def get_status(self) -> Dict:
        """Obtener estado actual del scheduler"""
        return {
            'is_running': self.is_running,
            'execution_count': self.execution_count,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'pending_jobs': len(schedule.jobs)
        }


if __name__ == "__main__":
    # Ejemplo de uso
    try:
        # Crear scheduler
        scheduler = FlightTrackerScheduler()
        
        # Opción 1: Ejecutar un check único (testing)
        if DEBUG:
            logger.info("🧪 Modo DEBUG: ejecutando un check único...\n")
            scheduler.run_once()
        else:
            # Opción 2: Ejecutar en modo daemon (producción)
            logger.info("🔄 Iniciando en modo daemon...\n")
            scheduler.run()
    
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        raise
