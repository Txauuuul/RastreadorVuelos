"""
api_aggregator.py - Patrón Agregador para múltiples APIs de vuelos

CONCEPTO EDUCATIVO - AGREGADOR (Aggregator Pattern):
Un agregador es un patrón de diseño que combina múltiples fuentes de datos
en una sola interfaz. Utilidades:

1. FLEXIBILIDAD: Agregar/remover APIs sin cambiar el código cliente
2. RESILIENCIA: Si una API falla, las otras siguen funcionando
3. COMPARACIÓN: Encontrar el mejor precio entre múltiples proveedores
4. ESCALABILIDAD: Soporta N APIs de forma genérica

ARQUITECTURA:
                    APIAggregator (orquestador)
                          |
                 ---------|----------
                |          |         |
          AmadeusProvider  |   GoogleFlightsProvider
                        FlysScraperProvider

Cada provider implementa la interfaz APIProvider:
  - search_flights(origin, dest, dates) -> dict

El agregador ejecuta todas EN PARALELO y retorna el mejor resultado.
"""

import requests
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from src.logger import logger
from src.config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, RAPIDAPI_KEY
from src.airport_utils import traducir_ciudad_a_iata


@dataclass
class FlightOffer:
    """Estructura unificada para una oferta de vuelo"""
    price: float
    currency: str = "EUR"
    departure: str = ""
    arrival: str = ""
    airline: str = ""
    stops: int = 0
    api_source: str = ""  # Quién encontró este vuelo (Amadeus, FlyScraper, etc)
    raw_data: dict = None


class APIProvider(ABC):
    """
    Interfaz base para todos los proveedores de APIs de vuelos
    
    CONCEPTO EDUCATIVO - Por qué ABC (Abstract Base Class):
    - Define un contrato que todos los providers deben cumplir
    - Obliga a implementar search_flights() en cada subclase
    - Permite polimorfismo: trata todos los providers igual
    """
    
    def __init__(self, name: str):
        """Inicializar el provider con su nombre"""
        self.name = name
        self.is_configured = True
    
    @abstractmethod
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None) -> Optional[List[FlightOffer]]:
        """
        Buscar vuelos en esta API
        
        Args:
            origin: Código IATA (ej: MAD)
            destination: Código IATA (ej: BCN)
            departure_date: Formato DD-MM-YYYY
            return_date: Formato DD-MM-YYYY (opcional)
        
        Returns:
            Lista de FlightOffer o None si error
        """
        pass


class AmadeusProvider(APIProvider):
    """Provider para la API de Amadeus (oficial, paga pero confiable)"""
    
    def __init__(self):
        super().__init__("Amadeus")
        try:
            from amadeus import Client
            self.client = Client(
                client_id=AMADEUS_CLIENT_ID,
                client_secret=AMADEUS_CLIENT_SECRET
            )
            logger.info("✅ AmadeusProvider inicializado")
        except Exception as e:
            logger.error(f"❌ AmadeusProvider no se pudo inicializar: {e}")
            self.is_configured = False
    
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None) -> Optional[List[FlightOffer]]:
        """
        Buscar en Amadeus
        
        NOTA: Usa la lógica existente de src.api.AmadeusAPI
        """
        if not self.is_configured:
            logger.warning(f"⚠️ {self.name} no está configurado")
            return None
        
        try:
            from src.api import AmadeusAPI
            amadeus_api = AmadeusAPI()
            
            # AmadeusAPI espera DD-MM-YYYY, no ISO format
            # Pasar directamente sin convertir
            results = amadeus_api.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date
            )
            
            if not results or not results.get('flights'):
                return []
            
            # Convertir a FlightOffer
            offers = []
            for flight in results.get('flights', []):
                offer = FlightOffer(
                    price=flight.get('price', 9999),
                    currency=flight.get('currency', 'EUR'),
                    departure=flight.get('departure', ''),
                    arrival=flight.get('arrival', ''),
                    airline=flight.get('airline', ''),
                    stops=flight.get('stops', 0),
                    api_source="Amadeus",
                    raw_data=flight
                )
                offers.append(offer)
            
            logger.info(f"✅ {self.name}: {len(offers)} vuelos encontrados")
            return offers
            
        except Exception as e:
            logger.error(f"❌ Error en {self.name}: {str(e)}")
            return None


class FlysScraperProvider(APIProvider):
    """
    Provider para FlyScraper (API no oficial en RapidAPI)
    
    ⚠️ DESACTIVADA: El endpoint está discontinuado en RapidAPI
    Error: "API doesn't exists"
    
    Solución: Buscar alternativas en RapidAPI o usar solo Amadeus
    """
    
    BASE_URL = "https://flyscraper-api.p.rapidapi.com"
    
    def __init__(self, api_key: str = None):
        super().__init__("FlyScraper")
        self.api_key = api_key or RAPIDAPI_KEY
        
        # TEMPORALMENTE DESACTIVADO - Endpoint no existe
        logger.warning(f"⚠️ {self.name}: Desactivado (endpoint no válido en RapidAPI)")
        self.is_configured = False
    
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None) -> Optional[List[FlightOffer]]:
        """Buscar vuelos en FlyScraper"""
        
        if not self.is_configured:
            logger.warning(f"⚠️ {self.name} no está configurado, saltando...")
            return None
        
        try:
            # Convertir formato de fecha a ISO (YYYY-MM-DD)
            departure_dt = datetime.strptime(departure_date, "%d-%m-%Y")
            departure_iso = departure_dt.strftime("%Y-%m-%d")
            
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "flyscraper-api.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            params = {
                "originCode": origin.upper(),
                "destinationCode": destination.upper(),
                "departureDate": departure_iso,
                "returnDate": datetime.strptime(return_date, "%d-%m-%Y").strftime("%Y-%m-%d") if return_date else None,
                "passengers": 1,
                "cabinClass": "ECONOMY"
            }
            
            # Remover None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.info(f"🔍 Buscando en {self.name}...")
            response = requests.get(
                f"{self.BASE_URL}/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ {self.name} retornó código {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('flights'):
                logger.info(f"ℹ️ {self.name}: Sin vuelos encontrados")
                return []
            
            # Convertir a FlightOffer
            offers = []
            for flight in data.get('flights', []):
                try:
                    offer = FlightOffer(
                        price=float(flight.get('price', {}).get('total', 9999)),
                        currency=flight.get('price', {}).get('currency', 'EUR'),
                        departure=flight.get('departure', {}).get('dateTime', ''),
                        arrival=flight.get('arrival', {}).get('dateTime', ''),
                        airline=flight.get('airline', {}).get('name', 'Unknown'),
                        stops=flight.get('segments', [{}])[0].get('stops', 0) if flight.get('segments') else 0,
                        api_source="FlyScraper",
                        raw_data=flight
                    )
                    offers.append(offer)
                except Exception as parse_error:
                    logger.warning(f"⚠️ Error parseando vuelo en {self.name}: {parse_error}")
                    continue
            
            logger.info(f"✅ {self.name}: {len(offers)} vuelos encontrados")
            return offers
            
        except requests.Timeout:
            logger.error(f"❌ {self.name}: Timeout (excedió 10 segundos)")
            return None
        except requests.ConnectionError as e:
            logger.error(f"❌ {self.name}: Error de conexión: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error en {self.name}: {str(e)}")
            return None


class GoogleFlightsScraperProvider(APIProvider):
    """
    Provider para Flights Scraper Data (API no oficial en RapidAPI)
    
    ⚠️ DESACTIVADA: Usuario no tiene suscripción a esta API
    Error: "You are not subscribed to this API"
    
    Solución: 
    1. Ir a https://rapidapi.com/am89tn/api/google-flights1
    2. Click en "Subscribe" (gratis o de pago)
    3. Reactivar provider
    """
    
    BASE_URL = "https://flights-scraper-data1.p.rapidapi.com"
    
    def __init__(self, api_key: str = None):
        super().__init__("GoogleFlights")
        self.api_key = api_key or RAPIDAPI_KEY
        
        # TEMPORALMENTE DESACTIVADO - Sin suscripción
        logger.warning(f"⚠️ {self.name}: Desactivado (sin suscripción en RapidAPI)")
        self.is_configured = False
    
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None) -> Optional[List[FlightOffer]]:
        """Buscar vuelos en Google Flights Scraper"""
        
        if not self.is_configured:
            logger.warning(f"⚠️ {self.name} no está configurado, saltando...")
            return None
        
        try:
            # Convertir formato de fecha a ISO (YYYY-MM-DD)
            departure_dt = datetime.strptime(departure_date, "%d-%m-%Y")
            departure_iso = departure_dt.strftime("%Y-%m-%d")
            
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "flights-scraper-data1.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            params = {
                "fromEntityId": origin.upper(),
                "toEntityId": destination.upper(),
                "departDate": departure_iso,
                "returnDate": datetime.strptime(return_date, "%d-%m-%Y").strftime("%Y-%m-%d") if return_date else None,
                "adults": 1,
                "cabinClass": "ECONOMY"
            }
            
            # Remover None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.info(f"🔍 Buscando en {self.name}...")
            response = requests.get(
                f"{self.BASE_URL}/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ {self.name} retornó código {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('data', {}).get('flights'):
                logger.info(f"ℹ️ {self.name}: Sin vuelos encontrados")
                return []
            
            # Convertir a FlightOffer
            offers = []
            for flight in data.get('data', {}).get('flights', []):
                try:
                    offer = FlightOffer(
                        price=float(flight.get('price', {}).get('total', 9999)),
                        currency=flight.get('price', {}).get('currency', 'EUR'),
                        departure=flight.get('legs', [{}])[0].get('departure', {}).get('time', ''),
                        arrival=flight.get('legs', [{}])[0].get('arrival', {}).get('time', ''),
                        airline=flight.get('airlines', ['Unknown'])[0] if flight.get('airlines') else 'Unknown',
                        stops=flight.get('legs', [{}])[0].get('stops', 0) if flight.get('legs') else 0,
                        api_source="GoogleFlights",
                        raw_data=flight
                    )
                    offers.append(offer)
                except Exception as parse_error:
                    logger.warning(f"⚠️ Error parseando vuelo en {self.name}: {parse_error}")
                    continue
            
            logger.info(f"✅ {self.name}: {len(offers)} vuelos encontrados")
            return offers
            
        except requests.Timeout:
            logger.error(f"❌ {self.name}: Timeout (excedió 10 segundos)")
            return None
        except requests.ConnectionError as e:
            logger.error(f"❌ {self.name}: Error de conexión: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error en {self.name}: {str(e)}")
            return None


class FlyScraper2Provider(APIProvider):
    """
    Provider para Fly Scraper API v2 (RapidAPI)
    
    ✅ ACTIVADO: Suscripción gratuita disponible
    Endpoint: https://fly-scraper.p.rapidapi.com/v2/flights/search-roundtrip
    """
    
    BASE_URL = "https://fly-scraper.p.rapidapi.com/v2/flights"
    
    def __init__(self, api_key: str = None):
        super().__init__("FlyScraper2")
        self.api_key = api_key or RAPIDAPI_KEY
        
        if not self.api_key or self.api_key == "dummy":
            logger.warning(f"⚠️ {self.name} no tiene API key configurada")
            self.is_configured = False
        else:
            logger.info(f"✅ {self.name}Provider inicializado")
    
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None) -> Optional[List[FlightOffer]]:
        """Buscar vuelos en Fly Scraper v2"""
        
        if not self.is_configured:
            logger.warning(f"⚠️ {self.name} no está configurado, saltando...")
            return None
        
        try:
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "fly-scraper.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            # Fly Scraper usa formato SkyId (PARI para París, MSYA para Kuala Lumpur)
            # Mapeamos códigos IATA a SkyId aproximados
            sky_id_map = {
                'MAD': 'MADM', 'BCN': 'BARCM', 'BKK': 'BKKM',
                'CDG': 'PARI', 'LHR': 'LOND', 'ORY': 'PARI',
                'JFK': 'NYCM', 'LAX': 'LAXM', 'MIA': 'MIAM'
            }
            
            origin_sky = sky_id_map.get(origin.upper(), origin.upper())
            dest_sky = sky_id_map.get(destination.upper(), destination.upper())
            
            params = {
                "originSkyId": origin_sky,
                "destinationSkyId": dest_sky
            }
            
            logger.info(f"🔍 Buscando en {self.name}...")
            response = requests.get(
                f"{self.BASE_URL}/search-roundtrip",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ {self.name} retornó código {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('data', {}).get('flights'):
                logger.info(f"ℹ️ {self.name}: Sin vuelos encontrados")
                return []
            
            # Convertir a FlightOffer
            offers = []
            for flight in data.get('data', {}).get('flights', []):
                try:
                    price = flight.get('minPrice', 9999)
                    offer = FlightOffer(
                        price=price,
                        currency=flight.get('currency', 'EUR'),
                        departure=flight.get('departure', ''),
                        arrival=flight.get('arrival', ''),
                        airline=flight.get('airline', 'Unknown'),
                        stops=flight.get('stops', 0),
                        api_source="FlyScraper2",
                        raw_data=flight
                    )
                    offers.append(offer)
                except Exception as parse_error:
                    logger.warning(f"⚠️ Error parseando vuelo en {self.name}: {parse_error}")
                    continue
            
            logger.info(f"✅ {self.name}: {len(offers)} vuelos encontrados")
            return offers
            
        except requests.Timeout:
            logger.error(f"❌ {self.name}: Timeout (excedió 10 segundos)")
            return None
        except requests.ConnectionError as e:
            logger.error(f"❌ {self.name}: Error de conexión: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error en {self.name}: {str(e)}")
            return None


class FlightsScraperDataProvider(APIProvider):
    """
    Provider para Flights Scraper Data API (RapidAPI)
    
    ✅ ACTIVADO: Suscripción gratuita disponible
    Endpoint: https://flights-scraper-data.p.rapidapi.com/flights/search-roundtrip
    """
    
    BASE_URL = "https://flights-scraper-data.p.rapidapi.com/flights"
    
    def __init__(self, api_key: str = None):
        super().__init__("FlightsScraperData")
        self.api_key = api_key or RAPIDAPI_KEY
        
        if not self.api_key or self.api_key == "dummy":
            logger.warning(f"⚠️ {self.name} no tiene API key configurada")
            self.is_configured = False
        else:
            logger.info(f"✅ {self.name}Provider inicializado")
    
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None) -> Optional[List[FlightOffer]]:
        """Buscar vuelos en Flights Scraper Data"""
        
        if not self.is_configured:
            logger.warning(f"⚠️ {self.name} no está configurado, saltando...")
            return None
        
        try:
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": "flights-scraper-data.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            params = {
                "departureId": origin.upper(),
                "arrivalId": destination.upper()
            }
            
            logger.info(f"🔍 Buscando en {self.name}...")
            response = requests.get(
                f"{self.BASE_URL}/search-roundtrip",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ {self.name} retornó código {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('flights'):
                logger.info(f"ℹ️ {self.name}: Sin vuelos encontrados")
                return []
            
            # Convertir a FlightOffer
            offers = []
            for flight in data.get('flights', []):
                try:
                    price = flight.get('price', 9999)
                    if isinstance(price, dict):
                        price = price.get('amount', 9999)
                    
                    offer = FlightOffer(
                        price=price,
                        currency=flight.get('currency', 'EUR'),
                        departure=flight.get('departure', ''),
                        arrival=flight.get('arrival', ''),
                        airline=flight.get('airline', 'Unknown'),
                        stops=flight.get('stops', 0),
                        api_source="FlightsScraperData",
                        raw_data=flight
                    )
                    offers.append(offer)
                except Exception as parse_error:
                    logger.warning(f"⚠️ Error parseando vuelo en {self.name}: {parse_error}")
                    continue
            
            logger.info(f"✅ {self.name}: {len(offers)} vuelos encontrados")
            return offers
            
        except requests.Timeout:
            logger.error(f"❌ {self.name}: Timeout (excedió 10 segundos)")
            return None
        except requests.ConnectionError as e:
            logger.error(f"❌ {self.name}: Error de conexión: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error en {self.name}: {str(e)}")
            return None


class APIAggregator:
    """
    Orquestador que ejecuta búsquedas en MÚLTIPLES APIs en paralelo
    
    CONCEPTO EDUCATIVO - Aggregator Patrón:
    
    1. Crea N threads, uno por cada API
    2. Cada thread busca en su API simultáneamente
    3. Si una API falla, su thread captura la excepción y continúa
    4. Al final, consolida resultados y devuelve el vuelo más barato
    5. Todo está logeado para debugging
    
    VENTAJAS:
    ✅ Si GoogleFlights crashes, Amadeus y FlyScraper siguen funcionando
    ✅ Paralelismo: en lugar de esperar 30 segundos secuencial (3 APIs × 10s c/u)
       esperas 10 segundos en paralelo
    ✅ Escalable: agregar una 4ª API es tan simple como instanciar otro provider
    """
    
    def __init__(self):
        """Inicializar el agregador con todos los providers disponibles"""
        logger.info("🚀 Inicializando APIAggregator...")
        
        self.providers = {
            "Amadeus": AmadeusProvider(),
            "FlyScraper2": FlyScraper2Provider(),
            "FlightsScraperData": FlightsScraperDataProvider()
        }
        
        # Contar cuántos providers están configurados
        configured = sum(1 for p in self.providers.values() if p.is_configured)
        logger.info(f"✅ {configured}/{len(self.providers)} APIs disponibles")
    
    def search(self, 
               origin: str, 
               destination: str, 
               departure_date: str,
               return_date: str = None) -> Tuple[Optional[FlightOffer], List[FlightOffer]]:
        """
        Buscar vuelos en TODAS las APIs en paralelo
        
        CONCEPTO EDUCATIVO - Threading:
        Usamos threading para paralelizar. La alternativa es asyncio,
        pero requests no es async-friendly sin librerias especiales.
        
        Args:
            origin: Código IATA (MAD)
            destination: Código IATA (BCN)  
            departure_date: Formato DD-MM-YYYY
            return_date: Formato DD-MM-YYYY (opcional)
        
        Returns:
            Tuple:
                - FlightOffer: El vuelo más barato (o None si todos fallaron)
                - List[FlightOffer]: Todos los vuelos encontrados (combinados)
        
        EJEMPLO RETORNO:
            cheapest = FlightOffer(price=120, api_source="FlyScraper", ...)
            all_flights = [
                FlightOffer(price=120, api_source="FlyScraper", ...),
                FlightOffer(price=150, api_source="Amadeus", ...),
                FlightOffer(price=140, api_source="GoogleFlights", ...),
            ]
        """
        
        logger.info(f"🔍 BÚSQUEDA AGREGADA: {origin} → {destination} ({departure_date})")
        logger.info(f"📡 Consultando {len(self.providers)} APIs simultáneamente...")
        
        # Diccionario para almacenar resultados de cada thread
        results = {}
        errors = {}
        
        def search_in_provider(provider_name: str, provider: APIProvider):
            """Función que ejecuta cada thread para buscar en una API"""
            try:
                logger.info(f"  ↳ {provider_name}: iniciando búsqueda...")
                offers = provider.search_flights(origin, destination, departure_date, return_date)
                results[provider_name] = offers or []
                logger.info(f"  ↳ {provider_name}: ✅ completado")
            except Exception as e:
                logger.error(f"  ↳ {provider_name}: ❌ error fatal: {e}")
                results[provider_name] = []
                errors[provider_name] = str(e)
        
        # Crear y ejecutar threads en paralelo
        threads = []
        for provider_name, provider in self.providers.items():
            thread = threading.Thread(
                target=search_in_provider,
                args=(provider_name, provider),
                daemon=False
            )
            threads.append(thread)
            thread.start()
        
        # Esperar a que todos los threads terminen (máximo 15 segundos)
        for thread in threads:
            thread.join(timeout=15)
        
        # Consolidar todos los resultados
        all_flights = []
        for provider_name, offers in results.items():
            if offers:
                all_flights.extend(offers)
                logger.info(f"✅ {provider_name}: {len(offers)} vuelos agregados")
        
        # Reportar errores
        if errors:
            logger.warning(f"⚠️ {len(errors)} APIs tuvieron problemas:")
            for provider_name, error in errors.items():
                logger.warning(f"   - {provider_name}: {error}")
        
        # Encontrar el vuelo más barato
        cheapest = None
        if all_flights:
            cheapest = min(all_flights, key=lambda x: x.price)
            logger.info(
                f"🏆 GANADOR: {cheapest.api_source} con {cheapest.price}€ "
                f"(de {len(all_flights)} vuelos comparados)"
            )
        else:
            logger.warning("❌ Ninguna API retornó resultados válidos")
        
        return cheapest, all_flights
    
    def add_provider(self, name: str, provider: APIProvider):
        """Agregar un nuevo provider (para extensibilidad futura)"""
        logger.info(f"➕ Agregando provider: {name}")
        self.providers[name] = provider
    
    def disable_provider(self, name: str):
        """Deshabilitar un provider temporalmente"""
        if name in self.providers:
            logger.info(f"🔇 Deshabilitando provider: {name}")
            self.providers[name].is_configured = False


# Para tests
if __name__ == "__main__":
    from src.logger import logger as test_logger
    
    print("🧪 Test del APIAggregator\n")
    
    aggregator = APIAggregator()
    
    # Prueba simple
    cheapest, all_offers = aggregator.search("MAD", "BCN", "25-04-2026")
    
    if cheapest:
        print(f"\n✅ Vuelo más barato encontrado:")
        print(f"   API: {cheapest.api_source}")
        print(f"   Precio: {cheapest.price}€")
        print(f"   Salida: {cheapest.departure}")
        print(f"   Llegada: {cheapest.arrival}")
    else:
        print("\n❌ No se encontraron vuelos")
    
    print(f"\n📊 Total de vuelos encontrados: {len(all_offers)}")
    for i, offer in enumerate(all_offers, 1):
        print(f"   {i}. {offer.api_source}: {offer.price}€")
