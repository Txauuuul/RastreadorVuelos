#!/usr/bin/env python3
"""
Script para agregar rutas de seguimiento a la base de datos
"""

from datetime import datetime
from src.database import inicializar_bd, SessionLocal, Ruta
from src.logger import logger

def agregar_ruta(origen, destino, fecha_inicio, fecha_fin, dias_regreso_min=None, 
                 dias_regreso_max=None, porcentaje_rebaja=15.0, precio_minimo=50.0):
    """Agrega una nueva ruta a la base de datos"""
    session = SessionLocal()
    try:
        # Verificar si ya existe
        existe = session.query(Ruta).filter_by(
            origen=origen,
            destino=destino,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        ).first()
        
        if existe and existe.activo:
            logger.warning(f"⚠️  Ruta {origen}→{destino} ya existe y está activa")
            return False
        
        ruta = Ruta(
            origen=origen,
            destino=destino,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            es_ida_vuelta=dias_regreso_min is not None,
            dias_regreso_min=dias_regreso_min,
            dias_regreso_max=dias_regreso_max,
            porcentaje_rebaja_alerta=porcentaje_rebaja,
            precio_minimo_alerta=precio_minimo,
            activo=True
        )
        
        session.add(ruta)
        session.commit()
        logger.info(f"✅ Ruta agregada: {origen}→{destino}")
        logger.info(f"   📅 Período: {fecha_inicio.date()} a {fecha_fin.date()}")
        if dias_regreso_min:
            logger.info(f"   🔄 Retorno: {dias_regreso_min}-{dias_regreso_max} días")
        logger.info(f"   🚨 Alerta: {porcentaje_rebaja}% rebaja o menos de €{precio_minimo}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al agregar ruta: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def main():
    """Agregar las rutas de prueba"""
    logger.info("=" * 60)
    logger.info("🛫 AGREGANDO RUTAS DE MONITOREO   ")
    logger.info("=" * 60)
    
    # Inicializar BD
    inicializar_bd()
    
    # RUTA 1: Madrid → Bangkok, Abril 2026, ida+vuelta 10-30 días
    agregar_ruta(
        origen="MAD",
        destino="BKK",
        fecha_inicio=datetime(2026, 4, 1),
        fecha_fin=datetime(2026, 4, 30),
        dias_regreso_min=10,
        dias_regreso_max=30,
        porcentaje_rebaja=15.0,
        precio_minimo=500.0
    )
    
    # RUTA 2: Madrid → Nueva York, Diciembre 2026, ida+vuelta 8-15 días
    agregar_ruta(
        origen="MAD",
        destino="JFK",
        fecha_inicio=datetime(2026, 12, 1),
        fecha_fin=datetime(2026, 12, 31),
        dias_regreso_min=8,
        dias_regreso_max=15,
        porcentaje_rebaja=15.0,
        precio_minimo=400.0
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ RUTAS AGREGADAS EXITOSAMENTE")
    logger.info("=" * 60)
    logger.info("\n🚀 El sistema ahora buscará automáticamente cada 5 horas")
    logger.info("   en Amadeus, FlyScraper2 y FlightsScraperData\n")

if __name__ == "__main__":
    main()
