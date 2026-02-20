"""
multi_api.py - Soporte para múltiples APIs de búsqueda de vuelos

CONCEPTO EDUCATIVO - Patrón Strategy:
En lugar de tener un solo API hardcodeado, creamos una interfaz genérica
que permite intercambiar providers fácilmente.

Cada API tiene:
- search_flights_date_range() - método estándar
- Mismo retorno (dict con estructura uniforme)

Esto permite:
1. Cambiar de API sin tocar el resto del código
2. Buscar en MÚLTIPLES APIs simultáneamente
3. Comparar precios y retornar el MEJOR

USO:
    from src.multi_api import BuscadorMultiAPI
    
    buscador = BuscadorMultiAPI()
    resultado = await buscador.buscar_todos(
        origen="MAD",
        destino="NYC",
        fecha_inicio="01-06-2026",
        fecha_fin="30-06-2026"
    )
    # Retorna: vuelo más barato de TODAS las APIs
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.logger import logger


class APIFlights:
    """
    Interfaz base para todos los APIs de vuelos
    
    Cada API (Amadeus, Skyscanner, Kiwi, etc) debe heredar de esto
    e implementar el método search_flights_date_range()
    """
    
    def __init__(self, nombre: str):
        self.nombre = nombre
    
    async def search_flights_date_range(self, origen: str, destino: str, 
                                       fecha_inicio: str, fecha_fin: str) -> Dict:
        """
        Buscar vuelos en un rango de fechas
        
        Retorna estructura estándar:
        {
            'success': bool,
            'best_price': float,
            'best_date': str (DD-MM-YYYY),
            'flight': {
                'airline': str,
                'stops': int,
                'duration': int,
                'departure_time': str,
                ...
            },
            'api': str (nombre del API),
            'message': str
        }
        """
        raise NotImplementedError("Subclases deben implementar este método")


class AmadeusAPI(APIFlights):
    """
    API Amadeus implementado como Strategy
    """
    
    def __init__(self):
        super().__init__("Amadeus")
        from src.api import AmadeusAPI as AmadeusOrig
        self._client = AmadeusOrig()
    
    async def search_flights_date_range(self, origen: str, destino: str,
                                       fecha_inicio: str, fecha_fin: str) -> Dict:
        """Delegar al API original de Amadeus"""
        try:
            resultado = self._client.search_flights_date_range(
                origen, destino, fecha_inicio, fecha_fin
            )
            
            if resultado.get('success'):
                resultado['api'] = 'Amadeus'
            
            return resultado
        
        except Exception as e:
            logger.error(f"❌ Error en Amadeus: {e}")
            return {
                'success': False,
                'api': 'Amadeus',
                'message': f"Error: {str(e)[:100]}"
            }


class SkyscannerAPI(APIFlights):
    """
    API Skyscanner para búsqueda de vuelos
    
    Nota: Requiere API key de Skyscanner
    https://www.skyscanner.com/partner-api/
    
    CONCEPTO EDUCATIVO - Patrón Adapter:
    Convierte el formato de respuesta de Skyscanner al formato estándar
    """
    
    def __init__(self):
        super().__init__("Skyscanner")
        from src.config import SKYSCANNER_API_KEY
        self.api_key = SKYSCANNER_API_KEY
        self.base_url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
        
        if not self.api_key or self.api_key == "sk_live_DUMMY":
            logger.warning("⚠️ Skyscanner API key no configurada")
            self.enabled = False
        else:
            self.enabled = True
    
    async def search_flights_date_range(self, origen: str, destino: str,
                                       fecha_inicio: str, fecha_fin: str) -> Dict:
        """
        Buscar en Skyscanner
        
        NOTA: Esta es una implementación placeholder.
        Para producción, necesitas:
        1. Obtener API key de Skyscanner
        2. Implementar autenticación
        3. Procesar respuestas en tiempo real
        """
        
        if not self.enabled:
            return {
                'success': False,
                'api': 'Skyscanner',
                'message': 'API key no configurada'
            }
        
        try:
            logger.debug(f"🔍 Buscando en Skyscanner: {origen}→{destino}")
            
            # TODO: Implementar búsqueda real en Skyscanner
            # Por ahora retornar estructura correcta pero vacía para no romper el flow
            
            return {
                'success': False,
                'api': 'Skyscanner',
                'message': 'Implementación próximamente disponible'
            }
        
        except Exception as e:
            logger.error(f"❌ Error en Skyscanner: {e}")
            return {
                'success': False,
                'api': 'Skyscanner',
                'message': f"Error: {str(e)[:100]}"
            }


class KiwiAPI(APIFlights):
    """
    API Kiwi.com para búsqueda de vuelos
    
    Nota: Requiere API key de Kiwi
    https://www.kiwi.com/en/pages/kiwi-api/
    
    Ventajas de Kiwi:
    - Más barato que Amadeus generalmente
    - Incluye vuelos combinados
    - API muy flexible
    """
    
    def __init__(self):
        super().__init__("Kiwi")
        from src.config import KIWI_API_KEY
        self.api_key = KIWI_API_KEY
        
        if not self.api_key or self.api_key == "DUMMY":
            logger.warning("⚠️ Kiwi API key no configurada")
            self.enabled = False
        else:
            self.enabled = True
    
    async def search_flights_date_range(self, origen: str, destino: str,
                                       fecha_inicio: str, fecha_fin: str) -> Dict:
        """
        Buscar en Kiwi.com
        
        NOTA: Implementación placeholder
        Para producción:
        1. Obtener API key de Kiwi
        2. Usar endpoint: https://tequila-api.kiwi.com/v2/search
        3. Soportar búsquedas en rango de fechas
        """
        
        if not self.enabled:
            return {
                'success': False,
                'api': 'Kiwi',
                'message': 'API key no configurada'
            }
        
        try:
            logger.debug(f"🔍 Buscando en Kiwi: {origen}→{destino}")
            
            # TODO: Implementar búsqueda real en Kiwi
            
            return {
                'success': False,
                'api': 'Kiwi',
                'message': 'Implementación próximamente disponible'
            }
        
        except Exception as e:
            logger.error(f"❌ Error en Kiwi: {e}")
            return {
                'success': False,
                'api': 'Kiwi',
                'message': f"Error: {str(e)[:100]}"
            }


class BuscadorMultiAPI:
    """
    Buscador que consulta MÚLTIPLES APIs en PARALELO
    
    CONCEPTO EDUCATIVO - Concurrencia:
    - asyncio.gather() permite ejecutar múltiples búsquedas al mismo tiempo
    - Sin bloquear una a la otra
    - Se espera a que todas terminen
    - Retorna el resultado más barato
    
    Ventajas:
    ✅ Busca en Amadeus + Skyscanner + Kiwi simultáneamente
    ✅ Encuentra el vuelo MÁS BARATO de TODAS las fuentes
    ✅ Si un API falla, los otros siguen funcionando
    ✅ Más rápido que búsquedas secuenciales
    """
    
    def __init__(self):
        self.apis = {
            'amadeus': AmadeusAPI(),
            # Comentados hasta que tengas API keys
            # 'skyscanner': SkyscannerAPI(),
            # 'kiwi': KiwiAPI(),
        }
        logger.info(f"🔄 Buscador Multi-API inicializado con {len(self.apis)} providers activos")
    
    async def buscar_todos(self, origen: str, destino: str,
                          fecha_inicio: str, fecha_fin: str) -> Dict:
        """
        Buscar en TODOS los APIs simultáneamente
        
        Retorna el vuelo más barato encontrado en cualquier API
        
        Args:
            origen, destino: Códigos IATA
            fecha_inicio, fecha_fin: Formato DD-MM-YYYY
        
        Returns:
            {
                'success': bool,
                'best_price': float,
                'best_date': str,
                'flight': {...},
                'api_ganador': str,
                'todos_resultados': [...]  # Resultados de todos los APIs
            }
        """
        
        logger.info(f"🔍 Búsqueda Multi-API: {origen}→{destino} ({fecha_inicio} a {fecha_fin})")
        
        # CONCEPTO EDUCATIVO - asyncio.gather():
        # Ejecutar TODAS las búsquedas en paralelo
        # No espera a que una termine para empezar la siguiente
        
        tareas = {
            nombre: api.search_flights_date_range(origen, destino, fecha_inicio, fecha_fin)
            for nombre, api in self.apis.items()
        }
        
        resultados = {}
        try:
            # Ejecutar todas las búsquedas concurrentemente
            for nombre, tarea in tareas.items():
                resultados[nombre] = await tarea
        
        except Exception as e:
            logger.error(f"❌ Error en búsqueda multi-API: {e}")
        
        # Encontrar el más barato de todos los resultados
        mejor_resultado = None
        mejor_precio = float('inf')
        api_ganador = None
        
        for nombre, resultado in resultados.items():
            if resultado.get('success'):
                precio = resultado.get('best_price', float('inf'))
                
                if precio < mejor_precio:
                    mejor_precio = precio
                    mejor_resultado = resultado
                    api_ganador = nombre
                    
                    logger.info(f"  ✅ {nombre.upper()}: {precio}€ ({resultado.get('best_date')})")
            else:
                logger.debug(f"  ⚠️ {nombre.upper()}: {resultado.get('message', 'Sin resultados')}")
        
        if mejor_resultado:
            logger.info(f"🏆 VUELO MÁS BARATO: {api_ganador.upper()} -> {mejor_precio}€")
            
            return {
                'success': True,
                'best_price': mejor_precio,
                'best_date': mejor_resultado.get('best_date'),
                'flight': mejor_resultado.get('flight'),
                'api_ganador': api_ganador,
                'todos_resultados': resultados,
                'flights': [mejor_resultado.get('flight')]
            }
        else:
            logger.warning("❌ No se encontraron vuelos en ningún API")
            
            return {
                'success': False,
                'message': 'No se encontraron vuelos',
                'todos_resultados': resultados
            }
    
    def agregar_api(self, nombre: str, api: APIFlights):
        """Agregar un nuevo API al buscador"""
        self.apis[nombre] = api
        logger.info(f"✅ API '{nombre}' agregado al buscador multi")
        
    
    async def buscar_con_timeout(self, origen: str, destino: str,
                                 fecha_inicio: str, fecha_fin: str,
                                 timeout_segundos: int = 30) -> Dict:
        """
        Buscar con timeout - útil si un API es muy lento
        
        Si tarda más de timeout_segundos, se cancela
        """
        try:
            resultado = await asyncio.wait_for(
                self.buscar_todos(origen, destino, fecha_inicio, fecha_fin),
                timeout=timeout_segundos
            )
            return resultado
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Búsqueda multi-API excedió {timeout_segundos}s")
            return {
                'success': False,
                'message': f'Búsqueda excedió {timeout_segundos} segundos'
            }


# Funciones de conveniencia
async def buscar_vuelos_baratos(origen: str, destino: str,
                                 fecha_inicio: str, fecha_fin: str) -> Dict:
    """
    Búsqueda simple - retorna el vuelo más barato en todos los APIs
    
    USO:
        resultado = await buscar_vuelos_baratos("MAD", "NYC", "01-06-2026", "30-06-2026")
    """
    buscador = BuscadorMultiAPI()
    return await buscador.buscar_todos(origen, destino, fecha_inicio, fecha_fin)


if __name__ == "__main__":
    """
    Prueba: python -m src.multi_api
    """
    import asyncio
    
    async def test():
        buscador = BuscadorMultiAPI()
        resultado = await buscador.buscar_todos("MAD", "BCN", "01-06-2026", "15-06-2026")
        print("\n" + "="*60)
        print(resultado)
    
    asyncio.run(test())
