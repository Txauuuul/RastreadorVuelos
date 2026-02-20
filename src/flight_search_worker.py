"""
flight_search_worker.py - Motor de búsqueda automática de vuelos

CONCEPTO EDUCATIVO - Background Worker:
Un "worker" es un proceso que corre en background ejecutando tareas.
En nuestro caso:
- Cada 5 horas busca todos los vuelos configurados
- Guarda precios en la BD
- Detecta si hay ofertas
- Envía alertas a Telegram

AGREGADOR MULTI-API (Patrón Agregador):
- Busca simultáneamente en Amadeus, FlyScraper, GoogleFlights
- Encuentra el vuelo más barato entre TODAS las fuentes
- Si un API falla, los otros siguen funcionando (RESILIENCIA)
- Compara precios automáticamente

USO:
    from src.flight_search_worker import iniciar_buscador_automatico
    asyncio.run(iniciar_buscador_automatico())
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.logger import logger
from src.database import (
    obtener_rutas_activas, guardar_precio, SessionLocal, Ruta,
    obtener_ultimas_busquedas, registrar_busqueda
)
from src.api_aggregator import APIAggregator
from src.alert_calculator import CalculadorAlertasInteligentes
from telegram import Bot
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class SearchWorker:
    """
    Worker que busca vuelos automáticamente
    
    CONCEPTO EDUCATIVO - Scheduler:
    Un scheduler ejecuta tareas en intervalos regulares (ej: cada 5 horas).
    En realidad, los schedulers usan loops asyncrónicos que evalúan
    si pasó suficiente tiempo desde la última ejecución.
    
    Patrón:
    1. Esperar X segundos
    2. Si es hora, ejecutar tarea
    3. Registrar último timestamp
    4. Volver a (1)
    """
    
    INTERVALO_BUSQUEDA = 5 * 3600  # 5 horas en segundos
    
    def __init__(self):
        self.agregador = APIAggregator()  # Busca en múltiples APIs automáticamente
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.calculador = CalculadorAlertasInteligentes()
        self.chat_id = TELEGRAM_CHAT_ID
        self.ultima_busqueda = None
        logger.info(f"🔄 SearchWorker inicializado con PATRÓN AGREGADOR (intervalo: {self.INTERVALO_BUSQUEDA}s)")
    
    async def buscar_todos_los_vuelos(self) -> Dict:
        """
        Busca todos los vuelos de todas las rutas configuradas
        USANDO PATRÓN AGREGADOR: Múltiples APIs en paralelo
        
        Retorna:
            {
                'total_rutas': int,
                'total_vuelos': int,
                'ofertas': [(...), ...],
                'errores': [(...), ...]
            }
        """
        logger.info("🚀 Iniciando búsqueda de todos los vuelos (Patrón Agregador)...")
        
        rutas = obtener_rutas_activas()
        resultados = {
            'total_rutas': len(rutas),
            'total_vuelos': 0,
            'ofertas_detectadas': [],
            'errores': [],
            'timestamp': datetime.now()
        }
        
        if not rutas:
            logger.warning("⚠️ No hay rutas activas para buscar")
            return resultados
        
        # Buscar cada ruta usando el AGREGADOR (múltiples APIs en paralelo)
        for ruta in rutas:
            try:
                logger.info(f"🔍 Buscando: {ruta.origen} → {ruta.destino} (Agregador paralelo)")
                
                # Buscar en MÚLTIPLES APIs SIMULTÁNEAMENTE
                mejor_vuelo, todos_los_vuelos = self.agregador.search(
                    origin=ruta.origen,
                    destination=ruta.destino,
                    departure_date=ruta.fecha_inicio.strftime("%d-%m-%Y"),
                    return_date=ruta.fecha_fin.strftime("%d-%m-%Y")
                )
                
                if not mejor_vuelo:
                    resultados['errores'].append({
                        'ruta': f"{ruta.origen}→{ruta.destino}",
                        'error': 'Ninguna API retornó resultados'
                    })
                    continue
                
                if mejor_vuelo.price > 0:
                    resultados['total_vuelos'] += 1
                    
                    # Guardar vuelo encontrado
                    try:
                        registrar_busqueda(
                            ruta_id=ruta.id,
                            origen=ruta.origen,
                            destino=ruta.destino,
                            fecha_vuelo=datetime.now(),
                            precio=float(mejor_vuelo.price),
                            aerolinea=mejor_vuelo.airline or f'API:{mejor_vuelo.api_source}',
                            escalas=mejor_vuelo.stops,
                            fuente=mejor_vuelo.api_source,  # Guardar cuál API lo encontró
                            duracion=None
                        )
                        logger.info(f"💾 Vuelo guardado: {mejor_vuelo.price}€ de {mejor_vuelo.api_source}")
                    except Exception as e:
                        logger.error(f"❌ Error guardando vuelo: {e}")
                    
                    # Verificar si es buena oferta
                    es_oferta = self.calculador.precio_es_buena_oferta(
                        ruta_id=ruta.id,
                        precio_actual=mejor_vuelo.price,
                        porcentaje_rebaja_alerta=ruta.porcentaje_rebaja_alerta
                    )
                    
                    if es_oferta:
                        oferta = {
                            'origen': ruta.origen,
                            'destino': ruta.destino,
                            'precio': mejor_vuelo.price,
                            'fecha': mejor_vuelo.departure,
                            'aerolinea': mejor_vuelo.airline or 'Unknown',
                            'umbral_minimo': ruta.precio_minimo_alerta,
                            'porcentaje_rebaja': ruta.porcentaje_rebaja_alerta,
                            'api_ganador': mejor_vuelo.api_source,  # Mostrar qué API lo encontró
                            'total_opciones': len(todos_los_vuelos)  # Para estadísticas
                        }
                        resultados['ofertas_detectadas'].append(oferta)
                        logger.info(
                            f"💰 OFERTA DETECTADA ({mejor_vuelo.api_source}): "
                            f"{ruta.origen}→{ruta.destino} por {mejor_vuelo.price}€ "
                            f"(de {len(todos_los_vuelos)} opciones comparadas)"
                        )
            
            except Exception as e:
                logger.error(f"❌ Error buscando {ruta.origen}→{ruta.destino}: {e}")
                resultados['errores'].append({
                    'ruta': f"{ruta.origen}→{ruta.destino}",
                    'error': str(e)[:100]
                })
        
        logger.info(
            f"✅ Búsqueda completada: "
            f"{resultados['total_vuelos']} vuelos, "
            f"{len(resultados['ofertas_detectadas'])} ofertas"
        )
        
        return resultados
    
    async def enviar_alertas(self, resultados: Dict):
        """Enviar alertas a Telegram con detalles del Agregador"""
        try:
            if resultados['ofertas_detectadas']:
                # Encabezado
                mensaje = "🎉 *¡OFERTAS DETECTADAS!*\n\n"
                
                for oferta in resultados['ofertas_detectadas']:
                    mensaje += (
                        f"✈️ *{oferta['origen']} → {oferta['destino']}*\n"
                        f"💰 *{oferta['precio']}€* "
                        f"(umbral: {oferta['umbral_minimo']}€)\n"
                        f"📅 {oferta['fecha']}\n"
                        f"🔖 {oferta['aerolinea']}\n"
                        f"🏆 Encontrado en: *{oferta['api_ganador'].upper()}*\n"
                        f"📊 Opciones comparadas: {oferta.get('total_opciones', '?')}\n"
                        f"📉 Rebaja: {oferta['porcentaje_rebaja']}%\n\n"
                    )
                
                mensaje += f"⏰ Búsqueda: {resultados['timestamp'].strftime('%H:%M:%S')}"
                
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=mensaje,
                    parse_mode='Markdown'
                )
                logger.info("✅ Alertas enviadas a Telegram")
        
        except Exception as e:
            logger.error(f"❌ Error enviando alertas: {e}")
    
    async def enviar_resumen(self, resultados: Dict):
        """Enviar resumen de búsqueda (no solo ofertas)"""
        try:
            mensaje = (
                f"📊 *Búsqueda completada*\n"
                f"⏰ {resultados['timestamp'].strftime('%d-%m-%Y %H:%M')}\n\n"
                f"📍 Rutas monitoreadas: {resultados['total_rutas']}\n"
                f"✈️ Vuelos encontrados: {resultados['total_vuelos']}\n"
                f"💰 Ofertas: {len(resultados['ofertas_detectadas'])}\n"
                f"❌ Errores: {len(resultados['errores'])}\n"
            )
            
            if resultados['errores']:
                mensaje += "\n*Errores:*\n"
                for error in resultados['errores'][:3]:
                    mensaje += f"• {error['ruta']}: {error['error'][:30]}\n"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=mensaje,
                parse_mode='Markdown'
            )
        
        except Exception as e:
            logger.error(f"❌ Error enviando resumen: {e}")
    
    async def ejecutar_ciclo_busqueda(self):
        """
        Ejecuta un ciclo completo de búsqueda y alertas
        
        Pasos:
        1. Buscar todos los vuelos
        2. Guardar en BD
        3. Detectar ofertas
        4. Enviar alertas
        5. Registrar búsqueda
        """
        try:
            # 1. Buscar
            resultados = await self.buscar_todos_los_vuelos()
            
            # 2. Enviar alertas si hay ofertas
            await self.enviar_alertas(resultados)
            
            # 3. Enviar resumen
            await self.enviar_resumen(resultados)
            
            # 4. Registrar búsqueda (opcional, no hay tabla para esto)
            # Descomentar si se implementa tabla de estadísticas de búsquedas
            # try:
            #     registrar_busqueda(
            #         rutas_buscadas=resultados['total_rutas'],
            #         vuelos_encontrados=resultados['total_vuelos'],
            #         ofertas_detectadas=len(resultados['ofertas_detectadas'])
            #     )
            # except:
            #     pass
            
            self.ultima_busqueda = datetime.now()
        
        except Exception as e:
            logger.error(f"❌ Error en ciclo de búsqueda: {e}")


async def iniciar_buscador_automatico(intervalo_segundos: int = 5*3600):
    """
    Inicia el loop de búsqueda automática
    
    Args:
        intervalo_segundos: Cada cuántos segundos buscar (default: 5 horas = 18000s)
    
    CONCEPTO EDUCATIVO - Event Loop:
    asyncio.run() crea un event loop que ejecuta código asincrónico.
    async/await permiten que operaciones de red no bloqueen el programa.
    Mientras espera respuesta del API, puede hacer otra cosa.
    
    USO EN main.py O scheduler.py:
        import asyncio
        from src.flight_search_worker import iniciar_buscador_automatico
        
        asyncio.run(iniciar_buscador_automatico())
    """
    worker = SearchWorker()
    
    logger.info(f"🔄 Buscador automático iniciado (intervalo: {intervalo_segundos}s = {intervalo_segundos/3600:.1f}h)")
    
    while True:
        try:
            logger.info("⏳ Ejecutando búsqueda...")
            await worker.ejecutar_ciclo_busqueda()
            
            logger.info(f"⏰ Próxima búsqueda en {intervalo_segundos/3600:.1f} horas...")
            await asyncio.sleep(intervalo_segundos)
        
        except KeyboardInterrupt:
            logger.info("⛔ Buscador automático detenido por usuario")
            break
        except Exception as e:
            logger.error(f"❌ Error en buscador: {e}")
            # Esperar aunque haya error, para no saturar logs
            await asyncio.sleep(60)


if __name__ == "__main__":
    """Ejecutar directamente con: python -m src.flight_search_worker"""
    asyncio.run(iniciar_buscador_automatico())
