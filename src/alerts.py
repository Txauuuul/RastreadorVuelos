"""
alerts.py - Módulo de lógica de alertas

CONCEPTO EDUCATIVO:
Una alerta se dispara cuando ocurre una de estas situaciones:

1. PRICE_BELOW_THRESHOLD: El precio actual < umbral mínimo
2. PRICE_BELOW_AVERAGE: El precio actual es X% más bajo que la media histórica

Este módulo encapsula la LÓGICA de decisión:
- ¿Hay una buena oportunidad?
- ¿Ya enviamos una alerta similar recientemente?
- ¿Qué mensaje mostrar?

Separar lógica de notificaciones es una BEST PRACTICE porque:
- Las alertas pueden cambiar (email → SMS → Telegram)
- La lógica de detección es independiente del medio
"""

from typing import List, Dict, Optional, Tuple
from src.logger import logger
from src.database import Database
from src.config import MIN_PRICE_THRESHOLD, PRICE_REDUCTION_PERCENTAGE


class AlertDetector:
    """
    Clase para detectar oportunidades de compra y generar alertas
    
    CONCEPTO EDUCATIVO - Responsabilidad única:
    Esta clase SOLO detecta si hay que enviar alerta.
    Otra clase (notifications.py) decidirá CÓMO enviarla.
    """
    
    def __init__(self, db: Database = None):
        """
        Inicializar el detector de alertas
        
        Args:
            db: Instancia de Database. Si no se proporciona, crea una nueva.
        """
        self.db = db or Database()
        logger.info("✅ Detector de alertas inicializado")
    
    def check_all_flights(self) -> List[Dict]:
        """
        Revisar TODOS los vuelos monitoreados y detectar alertas
        
        CONCEPTO EDUCATIVO - Orquestación:
        Este es el método "principal" que:
        1. Obtiene todos los vuelos activos
        2. Para cada uno, busca oportunidades
        3. Retorna las alertas a enviar
        
        Returns:
            Lista de alertas detectadas
        """
        alerts = []
        
        # Obtener todos los vuelos monitoreados
        flights = self.db.get_all_watched_flights()
        
        if not flights:
            logger.info("ℹ️ No hay vuelos monitoreados. Agrega algunos con add_watched_flight()")
            return alerts
        
        logger.info(f"🔍 Revisando {len(flights)} vuelos monitoreados...")
        
        for flight in flights:
            # Buscar alertas para este vuelo
            # NOTA: Aquí iría el código para obtener precio actual de Amadeus
            # De momento usamos datos de la BD para demostración
            flight_alerts = self._check_flight(flight)
            alerts.extend(flight_alerts)
        
        logger.info(f"📊 Detectadas {len(alerts)} alerta(s) potencial(es)")
        return alerts
    
    def _check_flight(self, flight: Dict) -> List[Dict]:
        """
        Revisar un vuelo específico y detectar alertas
        
        Args:
            flight: Dict con info del vuelo monitoreado
        
        Returns:
            Lista de alertas para este vuelo
        """
        alerts = []
        flight_id = flight['id']
        
        # Obtener historial de precios
        history = self.db.get_price_history(flight_id, days=7)
        
        if not history:
            logger.debug(f"⚠️ No hay historial para vuelo {flight['origin']}→{flight['destination']}")
            return alerts
        
        # Precio actual (el más reciente)
        current_price = history[0]['price']
        
        # ==================== ALERTA 1: PRECIO MÁS BAJO QUE EL UMBRAL ====================
        if current_price < flight['min_price']:
            alert = self._create_alert(
                flight=flight,
                alert_type="PRICE_BELOW_THRESHOLD",
                current_price=current_price,
                history=history
            )
            if alert:
                alerts.append(alert)
        
        # ==================== ALERTA 2: PRECIO SIGNIFICATIVAMENTE MÁS BAJO QUE MEDIA ====================
        avg_price = self.db.get_average_price(flight_id, days=7)
        
        if avg_price and current_price < avg_price:
            # Calcular porcentaje de reducción respecto a la media
            reduction_percent = ((avg_price - current_price) / avg_price) * 100
            
            if reduction_percent >= flight['price_reduction_percent']:
                alert = self._create_alert(
                    flight=flight,
                    alert_type="PRICE_BELOW_AVERAGE",
                    current_price=current_price,
                    history=history,
                    average_price=avg_price,
                    reduction_percent=reduction_percent
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def _create_alert(self,
                     flight: Dict,
                     alert_type: str,
                     current_price: float,
                     history: List[Dict],
                     average_price: float = None,
                     reduction_percent: float = None) -> Optional[Dict]:
        """
        Crear un objeto de alerta con validaciones
        
        CONCEPTO EDUCATIVO - Deduplicación:
        Aquí verificamos si ya enviamos una alerta similar
        para no spamear al usuario.
        """
        flight_id = flight['id']
        
        # ==================== VERIFICAR DEDUPLICACIÓN ====================
        # ¿Ya enviamos una alerta de este tipo en las últimas 24 horas?
        if self.db.check_recent_alert(flight_id, alert_type, hours=24):
            logger.debug(f"⏭️ Alerta duplicada evitada: {flight['origin']}→{flight['destination']} ({alert_type})")
            return None
        
        # ==================== CONSTRUIR MENSAJE ====================
        message = self._build_message(
            flight=flight,
            alert_type=alert_type,
            current_price=current_price,
            average_price=average_price,
            reduction_percent=reduction_percent,
            history=history
        )
        
        alert = {
            'flight_id': flight_id,
            'alert_type': alert_type,
            'origin': flight['origin'],
            'destination': flight['destination'],
            'departure_date': flight['departure_date'],
            'current_price': current_price,
            'average_price': average_price,
            'reduction_percent': reduction_percent,
            'message': message,
            'price_history': history[:5]  # Últimos 5 precios para contexto
        }
        
        logger.info(f"🚨 ALERTA DETECTADA: {alert_type} - {flight['origin']}→{flight['destination']}")
        logger.info(f"   Precio actual: {current_price}€ | Mensaje: {message[:60]}...")
        
        return alert
    
    def _build_message(self,
                      flight: Dict,
                      alert_type: str,
                      current_price: float,
                      average_price: float = None,
                      reduction_percent: float = None,
                      history: List[Dict] = None) -> str:
        """
        Construir mensaje de alerta personalizado
        
        CONCEPTO EDUCATIVO - Mensajes dinámicos:
        El mensaje cambia según el tipo de alerta para que sea
        más informativo y útil al usuario.
        """
        origin = flight['origin']
        destination = flight['destination']
        date = flight['departure_date']
        
        if alert_type == "PRICE_BELOW_THRESHOLD":
            min_price = flight['min_price']
            savings = min_price - current_price
            return (
                f"💰 ¡GANGA ENCONTRADA! {origin}→{destination}\n"
                f"📅 {date}\n"
                f"💵 Precio: {current_price}€ (estabas buscando por {min_price}€)\n"
                f"💸 Ahorras: {savings:.2f}€"
            )
        
        elif alert_type == "PRICE_BELOW_AVERAGE":
            savings = average_price - current_price
            return (
                f"📉 ¡PRECIO BAJÓ! {origin}→{destination}\n"
                f"📅 {date}\n"
                f"💵 Precio actual: {current_price}€\n"
                f"📊 Promedio (últimos 7 días): {average_price:.2f}€\n"
                f"📉 Reducción: {reduction_percent:.1f}%\n"
                f"💸 Ahorras: {savings:.2f}€"
            )
        
        return "🔔 Alerta de precio para tu vuelo"
    
    def get_alert_summary(self, alerts: List[Dict]) -> str:
        """
        Crear un resumen de todas las alertas detectadas
        para mostrar en un solo lugar
        """
        if not alerts:
            return "✅ No hay alertas. Los precios están normales."
        
        summary = f"🔔 RESUMEN DE ALERTAS ({len(alerts)} detectada(s)):\n\n"
        
        for i, alert in enumerate(alerts, 1):
            summary += f"{i}. {alert['origin']} → {alert['destination']} ({alert['departure_date']})\n"
            summary += f"   Tipo: {alert['alert_type']}\n"
            summary += f"   Precio: {alert['current_price']}€\n"
            summary += f"   {alert['message'][:80]}...\n\n"
        
        return summary


class AlertAnalyzer:
    """
    Clase adicional para análisis más profundos de tendencias de precios
    
    CONCEPTO EDUCATIVO - Extensibilidad:
    Si en el futuro quieres análisis más complejos (ML, predicciones),
    lo pones aquí sin afectar el resto del código.
    """
    
    def __init__(self, db: Database = None):
        """Inicializar el analizador"""
        self.db = db or Database()
    
    def get_price_trend(self, flight_id: int, days: int = 7) -> Dict:
        """
        Analizar la tendencia de precios
        
        Returns:
            Dict con estadísticas de la tendencia
        """
        history = self.db.get_price_history(flight_id, days=days)
        
        if len(history) < 2:
            return {'status': 'insufficient_data', 'history_size': len(history)}
        
        # Invertir para ordenar cronológicamente (más antiguo primero)
        history_sorted = sorted(history, key=lambda x: x['check_date'], reverse=True)
        
        prices = [h['price'] for h in history_sorted]
        
        # Calcular tendencia simple
        first_price = prices[0]
        last_price = prices[-1]
        
        change = last_price - first_price
        change_percent = (change / last_price) * 100 if last_price > 0 else 0
        
        return {
            'status': 'ok',
            'days': days,
            'data_points': len(prices),
            'oldest_price': first_price,
            'newest_price': last_price,
            'change': change,
            'change_percent': change_percent,
            'trend': 'SUBIENDO ⬆️' if change > 0 else 'BAJANDO ⬇️' if change < 0 else 'ESTABLE →',
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices)
        }
    
    def compare_flights(self, flight_ids: List[int]) -> List[Dict]:
        """
        Comparar el precio de varios vuelos
        
        Útil si tienes varias opciones y quieres ver cuál es más barato
        """
        comparison = []
        
        for flight_id in flight_ids:
            flight = self.db.get_watched_flight(flight_id)
            if not flight:
                continue
            
            avg_price = self.db.get_average_price(flight_id)
            min_price = self.db.get_min_price(flight_id)
            
            comparison.append({
                'flight_id': flight_id,
                'origin': flight['origin'],
                'destination': flight['destination'],
                'departure_date': flight['departure_date'],
                'average_price': avg_price,
                'min_price': min_price
            })
        
        # Ordenar por precio mínimo
        return sorted(comparison, key=lambda x: x['min_price'] if x['min_price'] else float('inf'))


if __name__ == "__main__":
    # Ejemplo de uso (solo para testing)
    try:
        db = Database()
        detector = AlertDetector(db)
        analyzer = AlertAnalyzer(db)
        
        logger.info("🧪 Ejecutando pruebas de alertas...\n")
        
        # 1. Obtener vuelos
        logger.info("📋 Test 1: Obtener vuelos monitoreados")
        flights = db.get_all_watched_flights()
        
        if flights:
            for flight in flights:
                logger.info(f"   {flight['origin']} → {flight['destination']} ({flight['departure_date']})")
        else:
            logger.warning("   ℹ️ No hay vuelos monitoreados. Ejecuta primero database.py para agregar vuelos.")
        
        # 2. Revisar alertas
        logger.info("\n🚨 Test 2: Revisar alertas")
        alerts = detector.check_all_flights()
        
        if alerts:
            logger.info(f"✅ Se detectaron {len(alerts)} alerta(s):")
            for alert in alerts:
                logger.info(f"\n{alert['message']}")
        else:
            logger.info("   No hay alertas actualmente")
        
        # 3. Analizar tendencias
        logger.info("\n📈 Test 3: Analizar tendencias de precios")
        if flights:
            flight_id = flights[0]['id']
            trend = analyzer.get_price_trend(flight_id)
            logger.info(f"   Vuelo ID {flight_id}:")
            logger.info(f"   - Tendencia: {trend.get('trend', 'Sin data')}")
            logger.info(f"   - Cambio: {trend.get('change_percent', 0):.2f}%")
            logger.info(f"   - Precio promedio: {trend.get('avg_price', 'N/A')}€")
        
        # 4. Resumen de alertas
        logger.info("\n📊 Test 4: Resumen de alertas")
        summary = detector.get_alert_summary(alerts)
        logger.info(summary)
    
    except Exception as e:
        logger.error(f"❌ Error en pruebas: {e}")
