"""
notifications.py - Módulo de notificaciones por Telegram

CONCEPTO EDUCATIVO:
Las notificaciones son el DESTINO final de las alertas.

Separar notificaciones del resto del código es importante porque:
- Puedes cambiar Telegram → Email → SMS sin tocar el resto
- Testeable: puedes mock el bot para testing
- Profesional: abstracción de responsabilidades

Usamos python-telegram-bot que es asincrónico pero lo envolvemos
en funciones sincrónicas para simplificar.
"""

import asyncio
from typing import List, Dict, Optional
from telegram import Bot
from telegram.error import TelegramError
from src.logger import logger
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.database import Database


class TelegramNotifier:
    """
    Clase para enviar notificaciones por Telegram
    
    CONCEPTO EDUCATIVO - Async/Await:
    Telegram es asincrónico por defecto. Usamos asyncio para
    manejar esto correctamente sin bloquear el programa.
    """
    
    def __init__(self, bot_token: str = TELEGRAM_BOT_TOKEN, chat_id: str = TELEGRAM_CHAT_ID):
        """
        Inicializar el notificador de Telegram
        
        Args:
            bot_token: Token del bot (@BotFather)
            chat_id: ID del chat donde enviar mensajes
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        
        logger.info("✅ Conexión con Telegram Bot establecida")
        logger.debug(f"   Bot Token: {bot_token[:10]}...")
        logger.debug(f"   Chat ID: {chat_id}")
    
    def send_alert(self, alert: Dict) -> bool:
        """
        Enviar una alerta por Telegram
        
        Args:
            alert: Dict con info de la alerta (viene de alerts.py)
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Intentar obtener el event loop actual
            try:
                loop = asyncio.get_running_loop()
                # Si hay un loop corriendo, no podemos usar asyncio.run()
                # Esto ocurre cuando se llama desde dentro de una función async
                logger.warning("⚠️ Detectado event loop en ejecución. send_alert debería llamarse desde contexto async.")
                return False
            except RuntimeError:
                # No hay loop en ejecución, podemos crear uno
                pass
            
            # Crear un nuevo event loop si es necesario
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Ejecutar la función async
            result = loop.run_until_complete(self._send_message_async(alert['message']))
            
            if result:
                logger.info(f"✅ Alerta enviada por Telegram")
                return True
            else:
                logger.error(f"❌ Error enviando alerta por Telegram")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error en Telegram: {e}")
            return False
    
    def send_summary(self, alerts: List[Dict]) -> bool:
        """
        Enviar un resumen de todas las alertas
        
        Args:
            alerts: Lista de alertas detectadas
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Construir mensaje de resumen
            if not alerts:
                message = "✅ No hay nuevas alertas. Los precios están normales."
            else:
                message = f"🔔 RESUMEN DE ALERTAS ({len(alerts)} detectada(s)):\n\n"
                
                for i, alert in enumerate(alerts, 1):
                    message += f"{i}. {alert['origin']} → {alert['destination']}\n"
                    message += f"   📅 {alert['departure_date']}\n"
                    message += f"   💵 {alert['current_price']}€\n"
                    message += f"   🏷️ {alert['alert_type']}\n\n"
            
            # Obtener o crear event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Ejecutar
            result = loop.run_until_complete(self._send_message_async(message))
            
            if result:
                logger.info(f"✅ Resumen enviado por Telegram ({len(alerts)} alertas)")
                return True
            else:
                logger.error(f"❌ Error enviando resumen")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error en resumen: {e}")
            return False
    
    def send_custom_message(self, message: str) -> bool:
        """
        Enviar un mensaje personalizado
        
        Útil para notificaciones de estado o testing
        """
        try:
            # Obtener o crear event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self._send_message_async(message))
            return result
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
    async def _send_message_async(self, message: str) -> bool:
        """
        Función asincrónica para enviar mensaje
        
        CONCEPTO EDUCATIVO - Async/Await:
        Las operaciones I/O (como llamadas a API) son lentas.
        Con async podemos hacer otras cosas mientras esperamos.
        """
        try:
            # Enviar mensaje
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'  # Permite usar etiquetas HTML básicas
            )
            
            logger.debug(f"📤 Mensaje enviado a Telegram ({len(message)} caracteres)")
            return True
        
        except TelegramError as e:
            logger.error(f"❌ Error de Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return False
    
    async def test_connection_async(self) -> bool:
        """
        Probar que la conexión con Telegram funciona (versión async)
        
        CONCEPTO EDUCATIVO - Testing:
        Siempre es buena idea verificar que todo está bien
        antes de empezar a usar el sistema.
        
        Esta versión async evita crear múltiples event loops.
        """
        try:
            message = (
                "🧪 <b>TEST EXITOSO</b>\n\n"
                "Tu bot de Telegram está configurado correctamente.\n"
                "Las alertas de vuelos se enviarán aquí."
            )
            
            result = await self._send_message_async(message)
            
            if result:
                logger.info("✅ Conexión con Telegram verificada")
                return True
            else:
                logger.error("❌ No se pudo enviar mensaje de test")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error en test de conexión: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Versión sincrónica de test_connection para compatibilidad
        """
        try:
            result = asyncio.run(self.test_connection_async())
            return result
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                logger.warning("⚠️ Event loop cerrado detectado. Creando uno nuevo...")
                # Crear un nuevo event loop limpio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.test_connection_async())
                    return result
                finally:
                    loop.close()
            else:
                raise


class NotificationManager:
    """
    Clase para orquestar notificaciones
    
    CONCEPTO EDUCATIVO - Patrón Manager:
    Centraliza la lógica de:
    - Decidir qué alertas enviar
    - Registrarlo en la BD
    - Manejar errores
    """
    
    def __init__(self, 
                 telegram_notifier: TelegramNotifier = None,
                 db: Database = None):
        """
        Inicializar el gestor de notificaciones
        
        Args:
            telegram_notifier: Instancia de TelegramNotifier
            db: Instancia de Database para registro
        """
        self.telegram = telegram_notifier or TelegramNotifier()
        self.db = db or Database()
        logger.info("✅ Gestor de notificaciones inicializado")
    
    def process_alerts(self, alerts: List[Dict]) -> Dict:
        """
        Procesar y enviar alertas
        
        CONCEPTO EDUCATIVO - Transacción lógica:
        Para cada alerta, hacemos:
        1. Intentar enviar por Telegram
        2. Registrar en BD que se envió (o no)
        3. Retornar estadísticas
        
        Returns:
            Dict con estadísticas de envío
        """
        stats = {
            'total': len(alerts),
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        if not alerts:
            logger.info("ℹ️ No hay alertas para procesar")
            return stats
        
        logger.info(f"📤 Procesando {len(alerts)} alerta(s)...")
        
        for alert in alerts:
            flight_id = alert['flight_id']
            alert_type = alert['alert_type']
            price = alert['current_price']
            message = alert['message']
            
            # Intentar enviar
            success = self.telegram.send_alert(alert)
            
            if success:
                # Registrar en BD
                self.db.record_alert_sent(
                    flight_id=flight_id,
                    alert_type=alert_type,
                    price=price,
                    message=message[:100]  # Guardar primeros 100 caracteres
                )
                
                stats['sent'] += 1
                stats['details'].append({
                    'status': 'sent',
                    'alert_type': alert_type,
                    'origin': alert['origin'],
                    'destination': alert['destination']
                })
            else:
                stats['failed'] += 1
                stats['details'].append({
                    'status': 'failed',
                    'alert_type': alert_type,
                    'origin': alert['origin'],
                    'destination': alert['destination']
                })
        
        # Log resumen
        logger.info(f"✅ Procesamiento completado: {stats['sent']} enviadas, {stats['failed']} fallidas")
        
        return stats
    
    def send_daily_report(self) -> bool:
        """
        Enviar reporte diario de alertas enviadas
        
        Útil para saber qué está pasando sin tener que revisar logs
        """
        try:
            db = Database()
            alerts = db.get_alerts_history(days=1)
            
            if not alerts:
                message = "📊 <b>Reporte Diario</b>\n\nNo se detectaron alertas hoy."
            else:
                message = f"📊 <b>Reporte Diario ({len(alerts)} alertas)</b>\n\n"
                
                # Agrupar por tipo
                by_type = {}
                for alert in alerts:
                    alert_type = alert['alert_type']
                    if alert_type not in by_type:
                        by_type[alert_type] = 0
                    by_type[alert_type] += 1
                
                for alert_type, count in by_type.items():
                    message += f"• {alert_type}: {count}\n"
            
            return self.telegram.send_custom_message(message)
        
        except Exception as e:
            logger.error(f"❌ Error en reporte: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de notificaciones"""
        try:
            alerts = self.db.get_alerts_history(days=30)
            
            stats = {
                'total_alerts_30days': len(alerts),
                'alerts_by_type': {},
                'alerts_today': 0
            }
            
            for alert in alerts:
                # Contar por tipo
                alert_type = alert['alert_type']
                stats['alerts_by_type'][alert_type] = stats['alerts_by_type'].get(alert_type, 0) + 1
                
                # Contar de hoy
                if alert['sent_at'].startswith(str(__import__('datetime').datetime.now().date())):
                    stats['alerts_today'] += 1
            
            return stats
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats: {e}")
            return {}


if __name__ == "__main__":
    # Ejemplo de uso (solo para testing)
    # IMPORTANTE: Usamos una única función async para evitar múltiples event loops
    
    async def run_tests():
        """Ejecutar todas las pruebas bajo un mismo event loop"""
        try:
            logger.info("🧪 Ejecutando pruebas de notificaciones...\n")
            
            # 1. Crear notificador
            logger.info("📱 Test 1: Inicializar Telegram Notifier")
            notifier = TelegramNotifier()
            
            # 2. Test de conexión
            logger.info("\n🔗 Test 2: Verificar conexión")
            try:
                success = await notifier.test_connection_async()
                
                if success:
                    logger.info("✅ Conexión exitosa")
                else:
                    logger.error("❌ No se pudo conectar a Telegram")
            except Exception as e:
                logger.error(f"❌ Error en test de conexión: {e}")
            
            # 3. Crear gestor
            logger.info("\n⚙️ Test 3: Inicializar NotificationManager")
            manager = NotificationManager(telegram_notifier=notifier)
            
            # 4. Ejemplo de alerta
            logger.info("\n🚨 Test 4: Enviar alerta de ejemplo")
            example_alert = {
                'flight_id': 1,
                'alert_type': 'PRICE_BELOW_THRESHOLD',
                'origin': 'MAD',
                'destination': 'CDG',
                'departure_date': '25-02-2025',
                'current_price': 45.50,
                'message': (
                    "💰 ¡GANGA ENCONTRADA! MAD→CDG\n"
                    "📅 25-02-2025\n"
                    "💵 Precio: 45.50€ (estabas buscando por 50.00€)\n"
                    "💸 Ahorras: 4.50€"
                )
            }
            
            # Enviar usando la función async directamente
            try:
                result = await notifier._send_message_async(example_alert['message'])
                if result:
                    logger.info("✅ Alerta de ejemplo enviada exitosamente")
                else:
                    logger.error("❌ Fallo al enviar alerta de ejemplo")
            except Exception as e:
                logger.error(f"❌ Error enviando alerta: {e}")
            
            # 5. Estadísticas
            logger.info("\n📊 Test 5: Ver estadísticas")
            stats = manager.get_stats()
            logger.info(f"   Alertas últimos 30 días: {stats.get('total_alerts_30days', 0)}")
            logger.info(f"   Alertas hoy: {stats.get('alerts_today', 0)}")
            
            logger.info("\n✅ Pruebas completadas")
        
        except Exception as e:
            logger.error(f"❌ Error en pruebas: {e}")
    
    # Ejecutar todas las pruebas bajo un único event loop
    try:
        asyncio.run(run_tests())
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
