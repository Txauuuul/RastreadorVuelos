"""
city_mapper.py - Mapeo de ciudades a códigos IATA

CONCEPTO EDUCATIVO:
En lugar de obligar al usuario a saber códigos IATA (MAD, BCN, etc.),
permitimos que escriba el nombre de la ciudad. Este módulo:

1. Mapea nombre de ciudad → lista de códigos IATA posibles
2. Cuando hay múltiples aeropuertos, busca el más barato
3. Valida que la ciudad exista

Ejemplos:
- "Madrid" → "MAD" (un único aeropuerto)
- "Londres" → busca LHR, LGW, STN, LCM, LTN → elige el más barato
- "Nueva York" → busca JFK, LGA, EWR → elige el más barato
"""

from typing import List, Tuple, Optional
from src.logger import logger
from src.api import AmadeusAPI

# Mapeo de ciudades a códigos IATA
# Formato: "ciudad_normalizada": ["IATA1", "IATA2", ...]
CITY_TO_IATA = {
    # España
    "madrid": ["MAD"],
    "barcelona": ["BCN"],
    "sevilla": ["SVQ"],
    "bilbao": ["BIO"],
    "málaga": ["AGP"],
    "alicante": ["ALC"],
    "valencia": ["VLC"],
    "ibiza": ["IBZ"],
    "palma": ["PMI"],
    "santiago": ["SCQ"],
    "vigo": ["VGO"],
    "asturias": ["OVD"],
    "zaragoza": ["ZAZ"],
    
    # Europa cercana
    "lisboa": ["LIS", "TPS"],
    "oporto": ["OPO"],
    "parís": ["CDG", "ORY", "EGC"],
    "amsterdam": ["AMS"],
    "bruselas": ["BRU", "CRL"],
    "berlín": ["BER", "TXL"],
    "múnich": ["MUC"],
    "fráncfort": ["FRA"],
    "zurich": ["ZRH"],
    "viena": ["VIE"],
    "praga": ["PRG"],
    "budapest": ["BUD"],
    "budapest": ["BUD"],
    "estocolmo": ["ARN"],
    "copenhague": ["CPH"],
    "oslo": ["OSL"],
    "varsovia": ["WAW"],
    "roma": ["FCO", "CIA"],
    "milán": ["MXP", "LIN"],
    "venecia": ["VCE"],
    "florencia": ["FLR"],
    "génova": ["GOA"],
    "atenas": ["ATH"],
    "estambul": ["IST"],
    "dublín": ["DUB"],
    "londres": ["LHR", "LGW", "STN", "LCM", "LTN"],
    "manchester": ["MAN"],
    "birmingham": ["BHX"],
    "edimburgo": ["EDI"],
    
    # América del Norte
    "nueva york": ["JFK", "LGA", "EWR"],
    "los ángeles": ["LAX"],
    "chicago": ["ORD", "MDW"],
    "miami": ["MIA"],
    "toronto": ["YYZ"],
    "méxico": ["MEX"],
    "ciudad de méxico": ["MEX"],
    "san francisco": ["SFO"],
    "boston": ["BOS"],
    "filadelfia": ["PHL"],
    
    # América del Sur
    "buenos aires": ["AEP", "EZE"],
    "sao paulo": ["GIG", "CGH"],
    "río de janeiro": ["GIG"],
    "santiago de chile": ["SCL"],
    "lima": ["LIM"],
    "bogotá": ["BOG"],
    
    # Asia
    "bangkok": ["BKK"],
    "singapur": ["SIN"],
    "seúl": ["ICN", "GMP"],
    "tokio": ["NRT", "HND"],
    "singapur": ["SIN"],
    "hong kong": ["HKG"],
    "dubai": ["DXB"],
    "doha": ["DOH"],
    "abudhabi": ["AUH"],
    "estambul": ["IST"],
    "bangladesh": ["DAC"],
    "delhi": ["DEL"],
    "mumbai": ["BOM"],
    "bengaluru": ["BLR"],
    
    # Oceanía
    "sídney": ["SYD"],
    "melbourne": ["MEL"],
    "auckland": ["AKL"],
}

# Descripción de ciudades en español (para respuestas amigables)
CITY_LABELS = {
    "madrid": "📍 Madrid",
    "barcelona": "📍 Barcelona",
    "sevilla": "📍 Sevilla",
    "bilbao": "📍 Bilbao",
    "málaga": "📍 Málaga",
    "alicante": "📍 Alicante",
    "valencia": "📍 Valencia",
    "ibiza": "📍 Ibiza",
    "palma": "📍 Palma de Mallorca",
    "new york": "📍 Nueva York",
    "los angeles": "📍 Los Ángeles",
    "london": "📍 Londres",
    "paris": "📍 París",
    "tokyo": "📍 Tokio",
    "bangkok": "📍 Bangkok",
    "singapur": "📍 Singapur",
    "sydney": "📍 Sídney",
}


def normalize_city_name(city: str) -> str:
    """
    Normalizar nombre de ciudad
    
    Ejemplos:
    - "MADRID" → "madrid"
    - "Nueva York" → "nueva york"
    - "  barcelona  " → "barcelona"
    """
    return city.strip().lower()


def get_iata_codes_for_city(city: str) -> Optional[List[str]]:
    """
    Obtener códigos IATA para una ciudad
    
    Args:
        city: Nombre de la ciudad (ej: "Madrid", "Londres")
    
    Returns:
        Lista de códigos IATA, o None si no existe
    
    Ejemplos:
        "Madrid" → ["MAD"]
        "Londres" → ["LHR", "LGW", "STN", "LCM", "LTN"]
        "Xyz" → None
    """
    normalized = normalize_city_name(city)
    return CITY_TO_IATA.get(normalized)


async def find_cheapest_airport(
    origin_city: str,
    destination_city: str,
    departure_date: str,
    api: AmadeusAPI
) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Encontrar el aeropuerto más barato para una ruta
    
    ALGORITMO:
    1. Obtener todos los aeropuertos de origen
    2. Obtener todos los aeropuertos de destino
    3. Buscar vuelos para cada combinación
    4. Retornar la combinación más barata
    
    Args:
        origin_city: Nombre de ciudad origen (ej: "Madrid")
        destination_city: Nombre de ciudad destino (ej: "Londres")
        departure_date: Fecha de salida (formato: DD-MM-YYYY)
        api: Instancia de AmadeusAPI
    
    Returns:
        Tupla: (iata_origin, iata_destination, min_price)
        Si no encuentra, retorna (None, None, None)
    
    Ejemplo:
        origin, dest, price = await find_cheapest_airport(
            "Nueva York", "Londres", "25-02-2025", api
        )
        # Retorna: ("JFK", "LHR", 285.50)
    """
    
    origin_codes = get_iata_codes_for_city(origin_city)
    destination_codes = get_iata_codes_for_city(destination_city)
    
    if not origin_codes or not destination_codes:
        logger.warning(f"❌ Ciudad no reconocida: {origin_city} o {destination_city}")
        return None, None, None
    
    min_price = float('inf')
    best_origin = None
    best_destination = None
    
    # Buscar todas las combinaciones
    for origin in origin_codes:
        for destination in destination_codes:
            try:
                result = await api.search_flights_async(
                    origin=origin,
                    destination=destination,
                    departure_date=departure_date,
                    adults=1
                )
                
                if result and result.get('flights'):
                    flight_price = min(f['price'] for f in result['flights'])
                    
                    if flight_price < min_price:
                        min_price = flight_price
                        best_origin = origin
                        best_destination = destination
                        
                        logger.debug(f"✅ {origin}→{destination}: {flight_price}€")
            
            except Exception as e:
                logger.debug(f"⚠️ Error buscando {origin}→{destination}: {e}")
                continue
    
    if best_origin and best_destination:
        logger.info(f"🏆 Mejor ruta encontrada: {best_origin}→{best_destination} ({min_price}€)")
        return best_origin, best_destination, min_price
    
    logger.warning(f"❌ No se encontraron vuelos para {origin_city}→{destination_city}")
    return None, None, None


def format_city_name(city: str) -> str:
    """Formatear nombre de ciudad para respuestas (sin emojis para evitar encoding issues)"""
    normalized = normalize_city_name(city)
    # Simplemente retornar el nombre con primera letra mayúscula
    # Sin usar emojis para evitar problemas de encoding
    return city.title() if city else "Desconocida"


def get_all_cities() -> List[str]:
    """Retornar lista de todas las ciudades disponibles"""
    return [city.title() for city in CITY_TO_IATA.keys()]
