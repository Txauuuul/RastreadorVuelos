"""
database.py - Módulo de gestión de base de datos SQLite

CONCEPTO EDUCATIVO:
Una base de datos es esencial para:
- Persistencia: guardar datos que sobrevivan al cierre del programa
- Análisis: comparar precios históricos
- Deduplicación: no enviar alertas duplicadas

Tablas que crearemos:
1. watched_flights: vuelos que el usuario quiere monitorear
2. price_history: historial de precios para cada vuelo
3. alerts_sent: registro de alertas enviadas (para no repetir)
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from src.logger import logger
from src.config import DB_PATH


class Database:
    """
    Clase para manejar todas las operaciones con la base de datos
    
    CONCEPTO EDUCATIVO - Context Manager:
    Usamos 'with' para asegurar que la conexión se cierre correctamente,
    incluso si hay un error. Es una BEST PRACTICE en Python.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """Inicializar conexión a la base de datos"""
        self.db_path = db_path
        self._ensure_db_exists()
        logger.info(f"✅ Base de datos inicializada: {self.db_path}")
    
    def _ensure_db_exists(self):
        """Crear base de datos y tablas si no existen"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla 1: Vuelos monitoreados por el usuario
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS watched_flights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        origin TEXT NOT NULL,
                        destination TEXT NOT NULL,
                        departure_date TEXT NOT NULL,
                        min_price REAL NOT NULL,
                        price_reduction_percent REAL NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(origin, destination, departure_date)
                    )
                """)
                
                # Tabla 2: Historial de precios
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        flight_id INTEGER NOT NULL,
                        price REAL NOT NULL,
                        currency TEXT DEFAULT 'EUR',
                        airline TEXT,
                        flight_number TEXT,
                        check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (flight_id) REFERENCES watched_flights(id)
                    )
                """)
                
                # Tabla 3: Alertas enviadas (para evitar duplicados)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alerts_sent (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        flight_id INTEGER NOT NULL,
                        alert_type TEXT NOT NULL,
                        price REAL NOT NULL,
                        message TEXT,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (flight_id) REFERENCES watched_flights(id)
                    )
                """)
                
                conn.commit()
                logger.debug("✅ Tablas de base de datos verificadas/creadas")
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error al crear base de datos: {e}")
            raise
    
    # ==================== OPERACIONES VUELOS MONITOREADOS ====================
    
    def add_watched_flight(self, 
                          origin: str, 
                          destination: str, 
                          departure_date: str,
                          min_price: float = 50.0,
                          price_reduction_percent: float = 15.0) -> bool:
        """
        Agregar un vuelo a monitorear
        
        Args:
            origin: Código IATA origen
            destination: Código IATA destino
            departure_date: Fecha de salida (DD-MM-YYYY)
            min_price: Precio mínimo absoluto (€)
            price_reduction_percent: Porcentaje de reducción para alerta (%)
        
        Returns:
            bool: True si se agregó correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO watched_flights 
                    (origin, destination, departure_date, min_price, price_reduction_percent)
                    VALUES (?, ?, ?, ?, ?)
                """, (origin.upper(), destination.upper(), departure_date, min_price, price_reduction_percent))
                
                conn.commit()
                logger.info(f"✅ Vuelo agregado: {origin} → {destination} ({departure_date})")
                return True
        
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ El vuelo {origin}→{destination} ({departure_date}) ya está en monitoreo")
            return False
        except sqlite3.Error as e:
            logger.error(f"❌ Error agregando vuelo: {e}")
            return False
    
    def get_all_watched_flights(self) -> List[Dict]:
        """Obtener todos los vuelos activos monitoreados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, origin, destination, departure_date, min_price, 
                           price_reduction_percent, created_at
                    FROM watched_flights
                    WHERE is_active = 1
                    ORDER BY departure_date ASC
                """)
                
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error obteniendo vuelos: {e}")
            return []
    
    def get_watched_flight(self, flight_id: int) -> Optional[Dict]:
        """Obtener información de un vuelo específico"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, origin, destination, departure_date, min_price, 
                           price_reduction_percent, created_at
                    FROM watched_flights
                    WHERE id = ?
                """, (flight_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error obteniendo vuelo: {e}")
            return None
    
    def deactivate_watched_flight(self, flight_id: int) -> bool:
        """Desactivar el monitoreo de un vuelo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE watched_flights
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (flight_id,))
                
                conn.commit()
                logger.info(f"✅ Vuelo desactivado (ID: {flight_id})")
                return True
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error desactivando vuelo: {e}")
            return False
    
    # ==================== OPERACIONES HISTORIAL DE PRECIOS ====================
    
    def add_price_record(self, 
                        flight_id: int, 
                        price: float, 
                        currency: str = 'EUR',
                        airline: str = None,
                        flight_number: str = None) -> bool:
        """
        Guardar un registro de precio para un vuelo
        
        CONCEPTO EDUCATIVO:
        Cada búsqueda crea un nuevo registro de precio. De esta forma
        tenemos un historial que podemos analizaripara ver tendencias.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO price_history 
                    (flight_id, price, currency, airline, flight_number)
                    VALUES (?, ?, ?, ?, ?)
                """, (flight_id, price, currency, airline, flight_number))
                
                conn.commit()
                return True
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error guardando precio: {e}")
            return False
    
    def get_price_history(self, flight_id: int, days: int = 7) -> List[Dict]:
        """
        Obtener historial de precios de los últimos N días
        
        Args:
            flight_id: ID del vuelo monitoreado
            days: Número de días hacia atrás
        
        Returns:
            Lista de registros de precios
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, price, currency, airline, flight_number, check_date
                    FROM price_history
                    WHERE flight_id = ? AND check_date >= datetime('now', '-' || ? || ' days')
                    ORDER BY check_date DESC
                """, (flight_id, days))
                
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []
    
    def get_average_price(self, flight_id: int, days: int = 7) -> Optional[float]:
        """Calcular precio promedio de los últimos N días"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT AVG(price) as avg_price
                    FROM price_history
                    WHERE flight_id = ? AND check_date >= datetime('now', '-' || ? || ' days')
                """, (flight_id, days))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] else None
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error calculando promedio: {e}")
            return None
    
    def get_min_price(self, flight_id: int, days: int = 7) -> Optional[float]:
        """Obtener precio mínimo de los últimos N días"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MIN(price) as min_price
                    FROM price_history
                    WHERE flight_id = ? AND check_date >= datetime('now', '-' || ? || ' days')
                """, (flight_id, days))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] else None
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error obteniendo mínimo: {e}")
            return None
    
    # ==================== OPERACIONES ALERTAS ====================
    
    def record_alert_sent(self, 
                         flight_id: int, 
                         alert_type: str,
                         price: float,
                         message: str = None) -> bool:
        """
        Registrar que se envió una alerta
        
        CONCEPTO EDUCATIVO - Deduplicación:
        Si guardamos cuando enviamos una alerta, podemos verificar
        si ya enviamos una similar recientemente para no spamear.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alerts_sent 
                    (flight_id, alert_type, price, message)
                    VALUES (?, ?, ?, ?)
                """, (flight_id, alert_type, price, message))
                
                conn.commit()
                logger.debug(f"✅ Alerta registrada (ID: {flight_id}, tipo: {alert_type})")
                return True
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error registrando alerta: {e}")
            return False
    
    def check_recent_alert(self, flight_id: int, alert_type: str, hours: int = 24) -> bool:
        """
        Verificar si ya enviamos una alerta similar en las últimas N horas
        
        CONCEPTO EDUCATIVO - Rate Limiting:
        Evita enviar alertas duplicadas si el precio baja 1€ cada hora.
        Con esto, máximo 1 alerta por tipo de vuelo cada 24 horas.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM alerts_sent
                    WHERE flight_id = ? AND alert_type = ? 
                    AND sent_at >= datetime('now', '-' || ? || ' hours')
                """, (flight_id, alert_type, hours))
                
                result = cursor.fetchone()
                return result[0] > 0 if result else False
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error verificando alerta: {e}")
            return False
    
    def get_alerts_history(self, flight_id: int = None, days: int = 30) -> List[Dict]:
        """Obtener historial de alertas enviadas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if flight_id:
                    cursor.execute("""
                        SELECT id, flight_id, alert_type, price, message, sent_at
                        FROM alerts_sent
                        WHERE flight_id = ? AND sent_at >= datetime('now', '-' || ? || ' days')
                        ORDER BY sent_at DESC
                    """, (flight_id, days))
                else:
                    cursor.execute("""
                        SELECT id, flight_id, alert_type, price, message, sent_at
                        FROM alerts_sent
                        WHERE sent_at >= datetime('now', '-' || ? || ' days')
                        ORDER BY sent_at DESC
                    """, (days,))
                
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error obteniendo alertas: {e}")
            return []
    
    # ==================== UTILIDADES ====================
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas globales de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar vuelos monitoreados
                cursor.execute("SELECT COUNT(*) FROM watched_flights WHERE is_active = 1")
                active_flights = cursor.fetchone()[0]
                
                # Contar registros de precios
                cursor.execute("SELECT COUNT(*) FROM price_history")
                price_records = cursor.fetchone()[0]
                
                # Contar alertas enviadas
                cursor.execute("SELECT COUNT(*) FROM alerts_sent")
                alerts_sent = cursor.fetchone()[0]
                
                return {
                    'active_flights': active_flights,
                    'price_records': price_records,
                    'alerts_sent': alerts_sent
                }
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def clear_old_data(self, days: int = 90) -> int:
        """
        Limpiar datos antiguos (más de N días) para mantener BD limpia
        
        CONCEPTO EDUCATIVO - Mantenimiento:
        Las bases de datos pueden crecer demasiado. Limpiar datos antiguos
        es una buena práctica para mantener rendimiento.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Eliminar registros de precios antiguos
                cursor.execute("""
                    DELETE FROM price_history
                    WHERE check_date < datetime('now', '-' || ? || ' days')
                """, (days,))
                
                deleted_rows = cursor.rowcount
                conn.commit()
                
                logger.info(f"🧹 Se eliminaron {deleted_rows} registros de precios antiguos")
                return deleted_rows
        
        except sqlite3.Error as e:
            logger.error(f"❌ Error limpiando datos: {e}")
            return 0


if __name__ == "__main__":
    # Ejemplo de uso (solo para testing)
    try:
        db = Database()
        
        logger.info("🧪 Ejecutando pruebas de base de datos...")
        
        # 1. Agregar un vuelo monitoreado
        logger.info("\n📝 Test 1: Agregar vuelo monitoreado")
        db.add_watched_flight(
            origin="MAD",
            destination="CDG",
            departure_date="25-02-2025",
            min_price=50.0,
            price_reduction_percent=15.0
        )
        
        # 2. Obtener vuelos monitoreados
        logger.info("\n📋 Test 2: Obtener vuelos monitoreados")
        flights = db.get_all_watched_flights()
        for flight in flights:
            logger.info(f"   {flight['origin']} → {flight['destination']} ({flight['departure_date']})")
        
        # 3. Agregar registros de precio
        logger.info("\n💰 Test 3: Agregar registros de precio")
        if flights:
            flight_id = flights[0]['id']
            db.add_price_record(flight_id, 89.50, airline="IB", flight_number="6845")
            db.add_price_record(flight_id, 87.00, airline="AF", flight_number="1234")
        
        # 4. Obtener historial de precios
        logger.info("\n📊 Test 4: Historial de precios")
        history = db.get_price_history(flight_id)
        logger.info(f"   Registros encontrados: {len(history)}")
        
        # 5. Calcular promedio y mínimo
        logger.info("\n📈 Test 5: Cálculos estadísticos")
        avg = db.get_average_price(flight_id)
        min_price = db.get_min_price(flight_id)
        logger.info(f"   Precio promedio: {avg}€")
        logger.info(f"   Precio mínimo: {min_price}€")
        
        # 6. Registrar alerta
        logger.info("\n🔔 Test 6: Registrar alerta")
        db.record_alert_sent(flight_id, "price_below_threshold", 45.00, "¡Precio muy bajo!")
        
        # 7. Estadísticas
        logger.info("\n📊 Test 7: Estadísticas globales")
        stats = db.get_statistics()
        logger.info(f"   Vuelos activos: {stats['active_flights']}")
        logger.info(f"   Registros de precios: {stats['price_records']}")
        logger.info(f"   Alertas enviadas: {stats['alerts_sent']}")
    
    except Exception as e:
        logger.error(f"❌ Error en pruebas: {e}")
