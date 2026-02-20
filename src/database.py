"""
database.py - Gestión de Base de Datos (PostgreSQL + SQLite local)

CONCEPTO EDUCATIVO:
- SQLAlchemy: ORM (Object-Relational Mapping)
  Permite trabajar con BD usando clases Python en lugar de SQL puro
  Beneficio: Código más limpio, portable (funciona con PostgreSQL, SQLite, MySQL)
  
- Modelos: Clases que representan tablas
  Ej: class Ruta() = tabla 'rutas' en la BD
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from src.config import DATABASE_URL
from src.logger import logger

# Base para todas las clases de modelos
Base = declarative_base()



# ==================== MODELOS (TABLAS) ====================

class Ruta(Base):
    """
    Tabla: rutas
    
    Almacena los vuelos que el usuario quiere monitorear
    Ejemplo:
        Madrid (MAD) → Nueva York (JFK)
        Desde: 2025-06-01
        Hasta: 2025-12-31
    """
    __tablename__ = 'rutas'
    
    id = Column(Integer, primary_key=True)
    origen = Column(String(3), nullable=False)  # Código IATA (MAD, BCN, etc)
    destino = Column(String(3), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)  # Desde qué fecha buscar
    fecha_fin = Column(DateTime, nullable=False)  # Hasta cuándo buscar
    
    # Vuelo de regreso
    es_ida_vuelta = Column(Boolean, default=False)
    dias_regreso_min = Column(Integer, nullable=True)  # Ej: 10 días mínimo
    dias_regreso_max = Column(Integer, nullable=True)  # Ej: 20 días máximo
    
    # Alertas
    precio_minimo_alerta = Column(Float, default=50.0)  # Alerta si baja de esto
    porcentaje_rebaja_alerta = Column(Float, default=15.0)  # Alerta si baja 15% vs media
    
    # Metadatos
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultima_busqueda = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Ruta {self.origen}→{self.destino} ({self.fecha_inicio.strftime('%Y-%m-%d')})"


class PrecioHistorico(Base):
    """
    Tabla: precios_historicos
    
    Registro de TODOS los precios encontrados en cada búsqueda
    Esto permite calcular la media histórica y detectar bajadas
    """
    __tablename__ = 'precios_historicos'
    
    id = Column(Integer, primary_key=True)
    ruta_id = Column(Integer, nullable=False)  # Foreign key a tabla 'rutas'
    
    # Vuelo
    origen = Column(String(3), nullable=False)
    destino = Column(String(3), nullable=False)
    fecha_vuelo = Column(DateTime, nullable=False)  # Fecha del vuelo (ida o vuelta)
    tipo_vuelo = Column(String(10), default='ida')  # 'ida' o 'vuelta'
    
    # Precio encontrado
    precio = Column(Float, nullable=False)
    moneda = Column(String(3), default='EUR')
    
    # Aerolínea
    aerolinea = Column(String(100), nullable=True)
    escalas = Column(Integer, nullable=True)  # 0=directo, 1=1 escala, etc
    duracion = Column(Integer, nullable=True)  # Minutos de vuelo
    
    # API que lo encontró
    fuente = Column(String(50))  # 'amadeus', 'kiwi', etc
    
    # Timestamp
    fecha_busqueda = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Precio {self.origen}→{self.destino} {self.fecha_vuelo.date()}: {self.precio}€>"


class Alerta(Base):
    """
    Tabla: alertas
    
    Registro de alertas GENERADAS (para no enviar la misma alerta 2 veces)
    Y para análisis histórico
    """
    __tablename__ = 'alertas'
    
    id = Column(Integer, primary_key=True)
    ruta_id = Column(Integer, nullable=False)
    
    # Tipo de alerta
    tipo = Column(String(50))  # 'precio_bajo', 'rebaja_vs_media', 'mejor_precio'
    
    # Detalles
    mensaje = Column(Text)  # Mensaje a enviar por Telegram
    precio_actual = Column(Float)
    precio_anterior = Column(Float, nullable=True)
    media_historica = Column(Float, nullable=True)
    
    # Estado
    enviado = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_envio = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Alerta {self.tipo}: {self.mensaje}>"


# ==================== DATABASE ENGINE ====================

def crear_engine():
    """
    Crea la conexión a PostgreSQL en Render
    Si falla (ej: no hay conexión a internet), usa SQLite local como fallback
    """
    try:
        logger.info(f"📡 Intentando conectar a PostgreSQL remoto...")
        engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
        
        # Test de conexión
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            logger.info("✅ PostgreSQL remoto CONECTADO")
        
        return engine
    
    except Exception as e:
        logger.warning(f"⚠️  No se pudo conectar a PostgreSQL: {e}")
        logger.warning("📦 Usando SQLite local como fallback...")
        
        # Fallback a SQLite
        sqlite_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vuelos.db')
        engine = create_engine(f'sqlite:///{sqlite_path}', echo=False)
        logger.info(f"✅ SQLite iniciado: {sqlite_path}")
        
        return engine


# Crear engine
engine = crear_engine()

# Session factory para ejecutar queries
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


# ==================== MIGRACIONES ====================

def aplicar_migraciones():
    """
    Aplica todas las migraciones de BD pendientes
    (Agregar nuevas columnas a tablas existentes, etc)
    """
    db = SessionLocal()
    try:
        from sqlalchemy import text, inspect
        
        # Inspeccionar estructura actual
        inspector = inspect(engine)
        
        # Migración 1: Agregar columna 'duracion' a precios_historicos
        tabla_columns = [col['name'] for col in inspector.get_columns('precios_historicos')]
        
        if 'duracion' not in tabla_columns:
            logger.info("🔧 Migrando: Agregando columna 'duracion' a precios_historicos...")
            try:
                if 'postgresql' in str(engine.url):
                    db.execute(text("ALTER TABLE precios_historicos ADD COLUMN duracion INTEGER"))
                else:  # SQLite
                    db.execute(text("ALTER TABLE precios_historicos ADD COLUMN duracion INTEGER"))
                db.commit()
                logger.info("✅ Migración completada: Columna 'duracion' agregada")
            except Exception as e:
                logger.warning(f"⚠️ Migración no necesaria: {str(e)[:60]}")
                db.rollback()
    except Exception as e:
        logger.warning(f"⚠️ Error al aplicar migraciones: {str(e)[:60]}")
    finally:
        db.close()


def inicializar_bd():
    """
    Crea todas las tablas en la BD si no existen
    Ejecutar al inicio del programa
    """
    logger.info("🔧 Inicializando base de datos...")
    Base.metadata.create_all(engine)
    logger.info("✅ Tablas creadas/verificadas")
    
    # Aplicar migraciones
    aplicar_migraciones()


def obtener_sesion() -> Session:
    """
    Context manager para obtener una sesión de BD
    
    USO:
    with obtener_sesion() as db:
        rutas = db.query(Ruta).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== FUNCIONES BÁSICAS DE BD ====================

def crear_ruta(origen: str, destino: str, fecha_inicio, fecha_fin, 
               es_ida_vuelta=False, dias_regreso_min=None, dias_regreso_max=None,
               porcentaje_rebaja=15.0, precio_min_automatico: bool = True) -> Ruta:
    """
    Crear una nueva ruta a monitorear
    
    CONCEPTO EDUCATIVO - Cálculo Automático:
    Si precio_min_automatico=True, el precio mínimo se calcula basado en:
    - Media histórica de precios para esa ruta
    - Porcentaje de rebaja deseado
    
    Ej: Si media es 500€ y rebaja es 20%, alerta cuando baje de 400€
    
    Args:
        origen, destino: Códigos IATA (MAD, NYC, etc)
        fecha_inicio, fecha_fin: Rango de búsqueda
        es_ida_vuelta: ¿Incluir vuelo de regreso?
        dias_regreso_min/max: Rango de días para el regreso
        porcentaje_rebaja: Porcentaje de descuento para alerta (%)
        precio_min_automatico: Si True, calcula automáticamente el precio mínimo
    
    Ejemplo:
    >>> crear_ruta('MAD', 'NYC', datetime(2025,6,1), datetime(2025,12,31), 
    ...           es_ida_vuelta=True, dias_regreso_min=10, dias_regreso_max=20,
    ...           porcentaje_rebaja=20.0)
    """
    db = SessionLocal()
    try:
        # Crear la ruta primero (sin precio mínimo)
        ruta = Ruta(
            origen=origen.upper(),
            destino=destino.upper(),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            es_ida_vuelta=es_ida_vuelta,
            dias_regreso_min=dias_regreso_min,
            dias_regreso_max=dias_regreso_max,
            porcentaje_rebaja_alerta=porcentaje_rebaja,
            precio_minimo_alerta=50.0  # Valor temporal
        )
        
        db.add(ruta)
        db.commit()  # Necesario para obtener el ID
        
        ruta_id = ruta.id
        
        # Ahora calcular el precio mínimo automáticamente
        if precio_min_automatico:
            from src.alert_calculator import CalculadorAlertasInteligentes
            
            precio_calculado = CalculadorAlertasInteligentes.calcular_precio_minimo_automatico(
                ruta_id=ruta_id,
                porcentaje_rebaja=porcentaje_rebaja,
                dias_historial=60
            )
            
            ruta.precio_minimo_alerta = precio_calculado
            db.commit()
            
            logger.info(f"✅ Ruta creada: {origen}→{destino}")
            logger.info(f"   Precio mínimo (calculado automáticamente): {precio_calculado}€")
        else:
            logger.info(f"✅ Ruta creada: {origen}→{destino}")
            logger.info(f"   Precio mínimo (fijo): {ruta.precio_minimo_alerta}€")
        
        return ruta
    
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error al crear ruta: {e}")
        raise
    finally:
        db.close()


def guardar_precio(ruta_id: int, origen: str, destino: str, fecha_vuelo,
                   precio: float, aerolinea: str, escalas: int, fuente: str,
                   tipo_vuelo: str = 'ida', duracion: int = None):
    """Guardar un precio en el historial"""
    db = SessionLocal()
    try:
        registro = PrecioHistorico(
            ruta_id=ruta_id,
            origen=origen.upper(),
            destino=destino.upper(),
            fecha_vuelo=fecha_vuelo,
            tipo_vuelo=tipo_vuelo,
            precio=precio,
            aerolinea=aerolinea,
            escalas=escalas,
            duracion=duracion,
            fuente=fuente
        )
        db.add(registro)
        db.commit()
        logger.debug(f"💾 Precio guardado: {precio}€")
        return registro
    
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error al guardar precio: {e}")
        raise
    finally:
        db.close()


def obtener_rutas_activas():
    """Obtener todas las rutas que están siendo monitoreadas"""
    db = SessionLocal()
    try:
        rutas = db.query(Ruta).filter(Ruta.activo == True).all()
        return rutas
    finally:
        db.close()


def obtener_media_precio(ruta_id: int, dias_historial: int = 30) -> float:
    """
    Calcular el precio MEDIO de los últimos N días
    Se usa para detectar bajadas vs "normal"
    """
    db = SessionLocal()
    try:
        from datetime import timedelta
        
        fecha_limite = datetime.utcnow() - timedelta(days=dias_historial)
        
        media = db.query(func.avg(PrecioHistorico.precio)).filter(
            PrecioHistorico.ruta_id == ruta_id,
            PrecioHistorico.fecha_busqueda >= fecha_limite
        ).scalar()
        
        return float(media) if media else 0.0
    finally:
        db.close()


def obtener_ultimas_busquedas(ruta_id: int, limite: int = 10):
    """
    Obtener los últimos N registros de búsqueda (precios encontrados)
    
    Args:
        ruta_id: ID de la ruta
        limite: Cuántos resultados retornar (default: 10)
    
    Returns:
        Lista de PrecioHistorico ordenados por fecha descendente
    """
    db = SessionLocal()
    try:
        registros = db.query(PrecioHistorico).filter(
            PrecioHistorico.ruta_id == ruta_id
        ).order_by(
            PrecioHistorico.fecha_busqueda.desc()
        ).limit(limite).all()
        
        return registros
    finally:
        db.close()


def registrar_busqueda(ruta_id: int, origen: str, destino: str, fecha_vuelo,
                       precio: float, aerolinea: str = None, escalas: int = 0,
                       fuente: str = "manual", tipo_vuelo: str = 'ida',
                       duracion: int = None) -> PrecioHistorico:
    """
    Registrar una búsqueda/vuelo encontrado en el histórico de precios
    ALIAS para guardar_precio() con un nombre más descriptivo
    
    Args:
        ruta_id: ID de la ruta
        origen: Código IATA
        destino: Código IATA
        fecha_vuelo: Fecha del vuelo
        precio: Precio en EUR
        aerolinea: Nombre de aerolínea (opcional)
        escalas: Número de escalas
        fuente: Origen del dato (ej: "Amadeus", "FlyScraper", "GoogleFlights")
        tipo_vuelo: 'ida' o 'vuelta'
        duracion: Duración en minutos
    
    Returns:
        PrecioHistorico: El registro creado
    """
    return guardar_precio(
        ruta_id=ruta_id,
        origen=origen,
        destino=destino,
        fecha_vuelo=fecha_vuelo,
        precio=precio,
        aerolinea=aerolinea or "Unknown",
        escalas=escalas,
        fuente=fuente,
        tipo_vuelo=tipo_vuelo,
        duracion=duracion
    )


if __name__ == "__main__":
    # Ejecutar este archivo para inicializar la BD
    inicializar_bd()
    print("✅ Base de datos inicializada")
