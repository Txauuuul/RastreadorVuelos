"""
api.py - Módulo para conectar con Amadeus API y obtener datos de vuelos

CONCEPTO EDUCATIVO:
La API de Amadeus proporciona múltiples servicios:
- Flight Search: Buscar vuelos disponibles
- Flight Offers Search: Obtener ofertas con precios en tiempo real
- Fare Rules: Reglas de cambio/cancelación

Este módulo encapsula toda la lógica de comunicación con Amadeus,
siguiendo el patrón de "separación de responsabilidades" (el API.py solo
habla con Amadeus, otros módulos manejan datos, alertas, etc.)
"""

from amadeus import Client, ResponseError
from datetime import datetime, timedelta
from src.logger import logger
from src.config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET


class AmadeusAPI:
    """
    Clase para manejar todas las operaciones con la API de Amadeus
    
    CONCEPTO EDUCATIVO - Por qué usar una clase:
    - Encapsulación: todo lo de Amadeus está en un lugar
    - Reutilizable: instancia una sola vez y úsala en todo el programa
    - Mantenible: si Amadeus cambia, solo cambias aquí
    """
    
    def __init__(self):
        """Inicializar la conexión con Amadeus"""
        try:
            self.amadeus_client = Client(
                client_id=AMADEUS_CLIENT_ID,
                client_secret=AMADEUS_CLIENT_SECRET
            )
            logger.info("✅ Conexión con Amadeus establecida")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Amadeus: {e}")
            raise
    
    def search_flights(self, 
                      origin: str, 
                      destination: str, 
                      departure_date: str,
                      return_date: str = None,
                      adults: int = 1) -> dict:
        """
        Buscar vuelos en Amadeus
        
        Args:
            origin: Código IATA del aeropuerto origen (ej: "MAD")
            destination: Código IATA del aeropuerto destino (ej: "CDG")
            departure_date: Fecha de salida (formato: "DD-MM-YYYY")
            return_date: Fecha de regreso opcional (formato: "DD-MM-YYYY")
            adults: Número de pasajeros adultos
        
        Returns:
            dict: Información de vuelos con precios
        
        CONCEPTO EDUCATIVO - Validación:
        Siempre validar inputs antes de enviar a la API para:
        - Evitar errores innecesarios
        - Mejorar experiencia del usuario
        - Reducir llamadas a la API (que pueden tener límites)
        """
        
        # Validar que los códigos IATA sean válidos
        if len(origin) != 3 or len(destination) != 3:
            logger.error(f"❌ Códigos IATA inválidos: {origin}, {destination}")
            return None
        
        # Validar formato de fecha y convertir a formato Amadeus (YYYY-MM-DD)
        try:
            departure_dt = datetime.strptime(departure_date, "%d-%m-%Y")
            departure_date_amadeus = departure_dt.strftime("%Y-%m-%d")
            
            if return_date:
                return_dt = datetime.strptime(return_date, "%d-%m-%Y")
                return_date_amadeus = return_dt.strftime("%Y-%m-%d")
            else:
                return_date_amadeus = None
        except ValueError:
            logger.error(f"❌ Formato de fecha incorrecto. Usa DD-MM-YYYY (ej: 20-02-2025)")
            return None
        
        try:
            logger.info(f"🔍 Buscando vuelos: {origin} → {destination} ({departure_date})")
            
            # Construir parámetros de búsqueda
            search_params = {
                'originLocationCode': origin.upper(),
                'destinationLocationCode': destination.upper(),
                'departureDate': departure_date_amadeus,
                'adults': str(adults),
                'max': '10'  # Limitar a 10 resultados para no saturar
            }
            
            # Si es ida y vuelta, agregar fecha de regreso
            if return_date_amadeus:
                search_params['returnDate'] = return_date_amadeus
            
            # Realizar búsqueda
            response = self.amadeus_client.shopping.flight_offers_search.get(**search_params)
            
            logger.info(f"✅ Búsqueda exitosa: {len(response.data) if response.data else 0} ofertas encontradas")
            
            # Retornar los datos en un formato structured
            return self._parse_flight_offers(response.data)
            
        except ResponseError as error:
            logger.error(f"❌ Error en Amadeus API: {error}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return None
    
    def _parse_flight_offers(self, offers: list) -> dict:
        """
        Procesar las ofertas de Amadeus a format más manejable
        
        CONCEPTO EDUCATIVO - Parsing:
        La API devuelve JSON complejo. Aquí extraemos solo lo que necesitamos
        para evitar confusión y errores más adelante
        
        Args:
            offers: Lista de ofertas de Amadeus
        
        Returns:
            dict: Datos procesados y limitados
        """
        
        if not offers:
            return {'flights': [], 'count': 0}
        
        flights = []
        
        for offer in offers:
            try:
                # Extraer información del primer segmento (vuelo)
                itinerary = offer.get('itineraries', [{}])[0]
                first_segment = itinerary.get('segments', [{}])[0]
                
                flight_info = {
                    'id': offer.get('id'),
                    'price': float(offer.get('price', {}).get('total', 0)),
                    'currency': offer.get('price', {}).get('currency', 'EUR'),
                    'departure': first_segment.get('departure', {}).get('at', 'N/A'),
                    'arrival': first_segment.get('arrival', {}).get('at', 'N/A'),
                    'origin': first_segment.get('departure', {}).get('iataCode', 'N/A'),
                    'destination': first_segment.get('arrival', {}).get('iataCode', 'N/A'),
                    'airline': first_segment.get('carrierCode', 'N/A'),
                    'flight_number': first_segment.get('number', 'N/A'),
                    'aircraft': first_segment.get('aircraft', {}).get('code', 'N/A'),
                    'duration': itinerary.get('duration', 'N/A'),
                    'stops': len(itinerary.get('segments', [])) - 1
                }
                
                flights.append(flight_info)
                
            except (KeyError, ValueError) as e:
                logger.warning(f"⚠️ Error procesando una oferta: {e}")
                continue
        
        logger.debug(f"📊 {len(flights)} vuelos procesados correctamente")
        
        return {
            'flights': flights,
            'count': len(flights)
        }
    
    def get_flight_prices_historical(self, 
                                    origin: str, 
                                    destination: str, 
                                    departure_date: str,
                                    days_to_check: int = 7) -> dict:
        """
        Obtener precios históricos para compararlos (búsquedas en días anteriores)
        
        CONCEPTO EDUCATIVO - Rate Limiting:
        Las APIs pueden tener límites de llamadas. Este método es opcional
        y debería usarse con moderación para no gastarse el límite.
        
        Args:
            origin: Código IATA origen
            destination: Código IATA destino
            departure_date: Fecha de referencia (formato DD-MM-YYYY)
            days_to_check: Cuántos días atrás verificar
        
        Returns:
            dict: Precios mínimos de días anteriores
        """
        
        logger.info(f"📈 Obteniendo precios históricos para análisis...")
        
        historical_prices = {}
        
        # Restar días a la fecha de salida (convertir a datetime)
        base_date = datetime.strptime(departure_date, "%d-%m-%Y")
        
        for i in range(1, days_to_check + 1):
            check_date = base_date - timedelta(days=i)
            date_str = check_date.strftime("%d-%m-%Y")
            
            # Buscar vuelo para ese día
            result = self.search_flights(origin, destination, date_str)
            
            if result and result['flights']:
                # Guardar el precio mínimo de ese día
                min_price = min([f['price'] for f in result['flights']])
                historical_prices[date_str] = min_price
                logger.debug(f"  {date_str}: ${min_price}")
        
        return historical_prices
    
    def search_flights_date_range(self,
                                 origin: str,
                                 destination: str,
                                 start_date: str,
                                 end_date: str,
                                 adults: int = 1) -> dict:
        """
        Buscar EL VUELO MÁS BARATO en un rango de fechas
        
        CONCEPTO EDUCATIVO - Búsqueda flexible de fechas:
        En lugar de buscar UN vuelo para UNA fecha específica,
        buscamos TODOS los vuelos en un rango (ej: todo febrero)
        y retornamos el más barato con su fecha.
        
        Args:
            origin: Código IATA origen (ej: "MAD")
            destination: Código IATA destino (ej: "CDG")
            start_date: Fecha inicio del rango (formato: "DD-MM-YYYY")
            end_date: Fecha fin del rango (formato: "DD-MM-YYYY")
            adults: Número de pasajeros
        
        Returns:
            dict con estructura:
            {
                'success': bool,
                'best_price': float,
                'best_date': str (formato: "DD-MM-YYYY"),
                'flight': { 'airline': str, 'duration': str, ... },
                'dates_checked': int,
                'message': str
            }
        
        Ejemplo:
            result = api.search_flights_date_range(
                "MAD", "CDG", "01-02-2025", "28-02-2025"
            )
            # Retorna vuelo más barato encontrado en febrero
        """
        
        try:
            # Validar fechas
            start_dt = datetime.strptime(start_date, "%d-%m-%Y")
            end_dt = datetime.strptime(end_date, "%d-%m-%Y")
            
            if start_dt > end_dt:
                logger.error("❌ Fecha inicio debe ser antes que fecha fin")
                return {
                    'success': False,
                    'message': '❌ Fecha inicio debe ser antes que fecha fin'
                }
            
            if (end_dt - start_dt).days > 90:
                logger.warning("⚠️ Rango > 90 días. Limitando a 90 días")
                end_dt = start_dt + timedelta(days=90)
            
            logger.info(f"🔍 Buscando vuelos más baratos en rango: {start_date} → {end_date}")
            
            best_price = float('inf')
            best_date = None
            best_flight = None
            dates_checked = 0
            dates_with_flights = 0
            
            # Iterar sobre cada día en el rango
            current_date = start_dt
            while current_date <= end_dt:
                date_str = current_date.strftime("%d-%m-%Y")
                dates_checked += 1
                
                try:
                    # Buscar vuelos para este día
                    result = self.search_flights(origin, destination, date_str, adults=adults)
                    
                    if result and result.get('flights'):
                        dates_with_flights += 1
                        
                        # Encontrar el vuelo más barato de este día
                        cheapest_today = min(result['flights'], key=lambda x: x['price'])
                        
                        if cheapest_today['price'] < best_price:
                            best_price = cheapest_today['price']
                            best_date = date_str
                            best_flight = cheapest_today
                            logger.debug(f"  ✅ {date_str}: {best_price}€ ({cheapest_today['airline']})")
                
                except Exception as e:
                    logger.debug(f"  ⚠️ Error en {date_str}: {e}")
                
                # Siguiente día
                current_date += timedelta(days=1)
            
            if best_flight:
                logger.info(
                    f"🏆 Vuelo más barato encontrado:\n"
                    f"   Fecha: {best_date}\n"
                    f"   Precio: {best_price}€\n"
                    f"   Aerolínea: {best_flight['airline']}"
                )
                
                return {
                    'success': True,
                    'best_price': best_price,
                    'best_date': best_date,
                    'flight': best_flight,
                    'dates_checked': dates_checked,
                    'dates_with_flights': dates_with_flights,
                    'message': f"✅ Vuelo más barato: {best_date} por {best_price}€"
                }
            else:
                logger.warning(f"❌ No se encontraron vuelos en el rango {start_date} → {end_date}")
                return {
                    'success': False,
                    'dates_checked': dates_checked,
                    'dates_with_flights': dates_with_flights,
                    'message': f"❌ No se encontraron vuelos. Revisados {dates_checked} días"
                }
        
        except Exception as e:
            logger.error(f"❌ Error buscando rango de fechas: {e}")
            return {
                'success': False,
                'message': f"❌ Error: {str(e)}"
            }


# ==================== FUNCIONES AUXILIARES ====================

def is_valid_iata_code(code: str) -> bool:
    """Validar que un código IATA sea válido (3 letras)"""
    return len(code) == 3 and code.isalpha()


def days_until(departure_date: str) -> int:
    """Calcular días hasta la fecha de salida (formato DD-MM-YYYY)"""
    departure = datetime.strptime(departure_date, "%d-%m-%Y")
    today = datetime.now()
    return (departure - today).days


if __name__ == "__main__":
    # Ejemplo de uso (solo para testing)
    try:
        api = AmadeusAPI()
        
        # Ejemplo: Buscar vuelos Madrid → París para mañana
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
        
        logger.info("🧪 Ejecutando búsqueda de prueba...")
        flights = api.search_flights(
            origin="MAD",
            destination="CDG",
            departure_date=tomorrow,
            adults=1
        )
        
        if flights and flights['count'] > 0:
            logger.info(f"✅ Se encontraron {flights['count']} vuelos")
            # Mostrar el primer vuelo como ejemplo
            first_flight = flights['flights'][0]
            logger.info(f"   Primer vuelo: {first_flight['airline']} - {first_flight['price']} {first_flight['currency']}")
        else:
            logger.info("❌ No se encontraron vuelos")
    
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
