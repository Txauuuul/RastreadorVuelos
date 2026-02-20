"""
alert_calculator.py - Cálculo inteligente de precios mínimos

CONCEPTO EDUCATIVO - Alertas Dinámicas:
En lugar de usar un precio mínimo fijo (ej: 50€), queremos que sea
DINÁMICO basado en el historial de precios reales.

Ventajas:
- Se adapta a rutas caras y baratas automáticamente
- No envía alertas absurdas
- Más inteligente que un threshold fijo
"""

from datetime import datetime, timedelta
from src.logger import logger
from src.database import SessionLocal, PrecioHistorico, Ruta
from sqlalchemy import func


class CalculadorAlertasInteligentes:
    """
    Calcula automáticamente precios mínimos de alerta basados en historial
    
    CONCEPTO EDUCATIVO - Estadística simple:
    Usamos conceptos como MEDIA, DESVIACIÓN ESTÁNDAR, PERCENTILES
    para tomar decisiones inteligentes sobre precios.
    """
    
    @staticmethod
    def calcular_precio_minimo_automatico(ruta_id: int, 
                                         porcentaje_rebaja: float = 15.0,
                                         dias_historial: int = 60) -> float:
        """
        Calcular automáticamente el precio MÍNIMO de alerta basado en:
        1. Precio MEDIO histórico
        2. Porcentaje de rebaja deseado
        
        Fórmula: precio_minimo = media * (1 - porcentaje_rebaja / 100)
        
        Args:
            ruta_id: ID de la ruta
            porcentaje_rebaja: Qué % de descuento queremos detectar
            dias_historial: Cuántos días atrás mirar (default: 60 días)
        
        Returns:
            float: Precio mínimo calculado automáticamente
        
        Ejemplo:
            Si media es 500€ y queremos -20% rebaja
            Retorna: 500 * (1 - 0.20) = 400€
        """
        db = SessionLocal()
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=dias_historial)
            
            # Obtener media histórica de precios
            resultado = db.query(func.avg(PrecioHistorico.precio)).filter(
                PrecioHistorico.ruta_id == ruta_id,
                PrecioHistorico.fecha_busqueda >= fecha_limite,
                PrecioHistorico.tipo_vuelo == 'ida'  # Solo vuelos ida
            ).scalar()
            
            media_historica = float(resultado) if resultado else None
            
            if not media_historica or media_historica <= 0:
                logger.warning(f"⚠️  No hay historial de precios para ruta {ruta_id}")
                # Si no hay historial, usar un valor por defecto
                return 50.0
            
            # Calcular precio mínimo de alerta
            # Ej: media 500€, rebaja 20% → 500 * 0.80 = 400€
            precio_minimo = media_historica * (1 - porcentaje_rebaja / 100)
            
            logger.info(f"📊 Ruta {ruta_id}:")
            logger.info(f"   Media histórica (últimos {dias_historial}d): {media_historica:.2f}€")
            logger.info(f"   Rebaja deseada: {porcentaje_rebaja}%")
            logger.info(f"   → Precio mínimo de alerta: {precio_minimo:.2f}€")
            
            return round(precio_minimo, 2)
        
        except Exception as e:
            logger.error(f"❌ Error calculando precio mínimo: {e}")
            return 50.0
        finally:
            db.close()
    
    @staticmethod
    def obtener_estadisticas_ruta(ruta_id: int, dias_historial: int = 60) -> dict:
        """
        Obtener estadísticas completas de precios de una ruta
        
        CONCEPTO EDUCATIVO - Análisis de datos:
        Retorna múltiples métricas para análisis exhaustivo
        """
        db = SessionLocal()
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=dias_historial)
            
            # Obtener todos los precios
            precios_query = db.query(PrecioHistorico.precio).filter(
                PrecioHistorico.ruta_id == ruta_id,
                PrecioHistorico.fecha_busqueda >= fecha_limite,
                PrecioHistorico.tipo_vuelo == 'ida'
            )
            
            precios = [p[0] for p in precios_query.all()]
            
            if not precios:
                return {
                    'precios_encontrados': 0,
                    'media': 0,
                    'minimo': 0,
                    'maximo': 0,
                    'mediana': 0
                }
            
            # Calcular estadísticas
            precios_ordenados = sorted(precios)
            
            return {
                'precios_encontrados': len(precios),
                'media': sum(precios) / len(precios),
                'minimo': min(precios),
                'maximo': max(precios),
                'mediana': precios_ordenados[len(precios)//2],
                'desviacion_std': CalculadorAlertasInteligentes._calcular_desviacion_standar(precios)
            }
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
        finally:
            db.close()
    
    @staticmethod
    def _calcular_desviacion_standar(valores: list) -> float:
        """Calcular desviación estándar (variabilidad de precios)"""
        if not valores or len(valores) < 2:
            return 0.0
        
        media = sum(valores) / len(valores)
        varianza = sum((x - media) ** 2 for x in valores) / len(valores)
        return varianza ** 0.5
    
    @staticmethod
    def precio_es_buena_oferta(ruta_id: int, precio_actual: float, 
                               porcentaje_rebaja_alerta: float = 15.0,
                               dias_historial: int = 60) -> tuple:
        """
        Evaluar si un precio actual es una BUENA OFERTA
        
        Retorna: (es_buena_oferta: bool, motivo: str, precio_minimo: float)
        
        Ejemplo:
            (True, "Precio 20% bajo vs media", 400.0)
        """
        db = SessionLocal()
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=dias_historial)
            
            # Obtener media
            media = db.query(func.avg(PrecioHistorico.precio)).filter(
                PrecioHistorico.ruta_id == ruta_id,
                PrecioHistorico.fecha_busqueda >= fecha_limite,
                PrecioHistorico.tipo_vuelo == 'ida'
            ).scalar()
            
            if not media:
                return False, "Sin historial suficiente", 50.0
            
            media = float(media)
            
            # Calcular descuento real vs media
            if media > 0:
                descuento_real = ((media - precio_actual) / media) * 100
            else:
                return False, "Error en cálculo", 50.0
            
            # Umbral de alerta
            precio_minimo = media * (1 - porcentaje_rebaja_alerta / 100)
            
            # ¿Es buena oferta?
            if precio_actual <= precio_minimo:
                motivo = f"Precio {descuento_real:.1f}% bajo vs media ({media:.2f}€)"
                return True, motivo, precio_minimo
            else:
                motivo = f"Precio normal (necesita {porcentaje_rebaja_alerta}% rebaja)"
                return False, motivo, precio_minimo
        
        except Exception as e:
            logger.error(f"❌ Error evaluando oferta: {e}")
            return False, "Error en cálculo", 50.0
        finally:
            db.close()


if __name__ == "__main__":
    """Test de las funciones de alerta"""
    logger.info("🧪 Test: Cálculo de alertas inteligentes\n")
    
    # Ejemplo: Calcular precio mínimo para ruta 1
    print("=" * 60)
    precio_minimo = CalculadorAlertasInteligentes.calcular_precio_minimo_automatico(
        ruta_id=1,
        porcentaje_rebaja=20.0,  # Queremos 20% de rebaja
        dias_historial=60
    )
    print(f"\n✅ Precio mínimo calculado: {precio_minimo}€\n")
    
    # Ejemplo: Obtener estadísticas
    print("=" * 60)
    stats = CalculadorAlertasInteligentes.obtener_estadisticas_ruta(ruta_id=1)
    if stats and stats['precios_encontrados'] > 0:
        logger.info("📊 Estadísticas de la ruta:")
        logger.info(f"   Precios registrados: {stats['precios_encontrados']}")
        logger.info(f"   Media: {stats['media']:.2f}€")
        logger.info(f"   Mínimo: {stats['minimo']:.2f}€")
        logger.info(f"   Máximo: {stats['maximo']:.2f}€")
        logger.info(f"   Desviación estándar: {stats['desviacion_std']:.2f}€")
