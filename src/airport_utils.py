"""
airport_utils.py - Utilidades para traducir ciudades a códigos IATA

CONCEPTO EDUCATIVO - Mapeo de datos:
Un diccionario centralizado permite traducir nombres amigables (ciudades)
a códigos técnicos (IATA). Es mucho más UX-friendly que pedirle al usuario
que sepa de memoria "MAD" en lugar de "Madrid".
"""

from src.logger import logger

# ==================== DICCIONARIO GLOBAL DE AEROPUERTOS ====================
# Formato: "ciudad_minúscula": "IATA"
# Se puede expandir fácilmente agregando más ciudades/aeropuertos

AIRPORTS = {
    # ESPAÑA
    "madrid": "MAD",
    "mda": "MAD",
    "barcelona": "BCN",
    "bcn": "BCN",
    "bilbao": "BIO",
    "bio": "BIO",
    "málaga": "AGP",
    "malaga": "AGP",
    "agp": "AGP",
    "valencia": "VLC",
    "vlc": "VLC",
    "sevilla": "SVQ",
    "svq": "SVQ",
    "alicante": "ALC",
    "alc": "ALC",
    "ibiza": "IBZ",
    "ibz": "IBZ",
    "palma": "PMI",
    "pmi": "PMI",
    "murcia": "MJV",
    "mjv": "MJV",
    "vigo": "VGO",
    "vgo": "VGO",
    
    # EUROPA - PRINCIPALES
    "parís": "CDG",
    "paris": "CDG",
    "cdg": "CDG",
    "orly": "ORY",
    "londres": "LHR",
    "london": "LHR",
    "lhr": "LHR",
    "berlín": "BER",
    "berlin": "BER",
    "ber": "BER",
    "ámsterdam": "AMS",
    "amsterdam": "AMS",
    "ams": "AMS",
    "róterdam": "RTM",
    "rotterdam": "RTM",
    "rtm": "RTM",
    "fráncfort": "FRA",
    "frankfurt": "FRA",
    "fra": "FRA",
    "múnich": "MUC",
    "munich": "MUC",
    "muc": "MUC",
    "milán": "MXP",
    "milan": "MXP",
    "mxp": "MXP",
    "roma": "FCO",
    "fco": "FCO",
    "venecia": "VCE",
    "venice": "VCE",
    "vce": "VCE",
    "viena": "VIE",
    "vienna": "VIE",
    "vie": "VIE",
    "praga": "PRG",
    "prague": "PRG",
    "prg": "PRG",
    "varsovia": "WAW",
    "warsaw": "WAW",
    "waw": "WAW",
    "dublín": "DUB",
    "dublin": "DUB",
    "dub": "DUB",
    "lisboa": "LIS",
    "lisbon": "LIS",
    "lis": "LIS",
    "zurich": "ZRH",
    "zurych": "ZRH",
    "zrh": "ZRH",
    "ginebra": "GVA",
    "geneva": "GVA",
    "gva": "GVA",
    "estocolmo": "ARN",
    "stockholm": "ARN",
    "arn": "ARN",
    "copenhague": "CPH",
    "copenhagen": "CPH",
    "cph": "CPH",
    "oslo": "OSL",
    "osl": "OSL",
    "helsinki": "HEL",
    "hel": "HEL",
    "bucarest": "OTP",
    "bucharest": "OTP",
    "otp": "OTP",
    "budapest": "BUD",
    "bud": "BUD",
    "belgrado": "BEG",
    "belgrade": "BEG",
    "beg": "BEG",
    "sofía": "SOF",
    "sofia": "SOF",
    "sof": "SOF",
    "estambul": "IST",
    "istanbul": "IST",
    "ist": "IST",
    "atenas": "ATH",
    "athens": "ATH",
    "ath": "ATH",
    
    # AMÉRICA - USA
    "nueva york": "NYC",
    "new york": "NYC",
    "ny": "NYC",
    "nyc": "NYC",
    "jfk": "JFK",
    "lga": "LGA",
    "newark": "EWR",
    "ewr": "EWR",
    "los ángeles": "LAX",
    "los angeles": "LAX",
    "la": "LAX",
    "lax": "LAX",
    "san francisco": "SFO",
    "sf": "SFO",
    "sfo": "SFO",
    "chicago": "ORD",
    "ord": "ORD",
    "midfway": "MDW",
    "mdw": "MDW",
    "miami": "MIA",
    "mia": "MIA",
    "boston": "BOS",
    "bos": "BOS",
    "las vegas": "LAS",
    "las": "LAS",
    "las vegas": "LAS",
    "seattle": "SEA",
    "sea": "SEA",
    "denver": "DEN",
    "den": "DEN",
    "atlanta": "ATL",
    "atl": "ATL",
    "dallas": "DFW",
    "dfw": "DFW",
    "houston": "IAH",
    "iah": "IAH",
    "filadelfia": "PHL",
    "philadelphia": "PHL",
    "phl": "PHL",
    "washington": "DCA",
    "dc": "DCA",
    "dca": "DCA",
    "phoenix": "PHX",
    "phx": "PHX",
    "orlando": "MCO",
    "mco": "MCO",
    "detroit": "DTW",
    "dtw": "DTW",
    "minneapolis": "MSP",
    "msp": "MSP",
    
    # AMÉRICA - CANADA
    "toronto": "YYZ",
    "yyz": "YYZ",
    "vancouver": "YVR",
    "yvr": "YVR",
    "montreal": "YUL",
    "yul": "YUL",
    "calgary": "YYC",
    "yyc": "YYC",
    
    # AMÉRICA - MÉXICO Y CARIBE
    "méxico": "MEX",
    "mexico": "MEX",
    "mex": "MEX",
    "cancún": "CUN",
    "cancun": "CUN",
    "cun": "CUN",
    "san juan": "SJU",
    "sju": "SJU",
    "la habana": "HAV",
    "havana": "HAV",
    "hav": "HAV",
    
    # AMÉRICA - SUDAMÉRICA
    "buenos aires": "AEP",
    "aep": "AEP",
    "bogotá": "BOG",
    "bogota": "BOG",
    "bog": "BOG",
    "lima": "LIM",
    "lim": "LIM",
    "santiago": "SCL",
    "scl": "SCL",
    "são paulo": "GIG",
    "sao paulo": "GIG",
    "gig": "GIG",
    "cartagena": "CTG",
    "ctg": "CTG",
    
    # ASIA
    "tokio": "NRT",
    "tokyo": "NRT",
    "nrt": "NRT",
    "haneda": "HND",
    "hnd": "HND",
    "singapur": "SIN",
    "singapore": "SIN",
    "sin": "SIN",
    "bangkok": "BKK",
    "bkk": "BKK",
    "hong kong": "HKG",
    "hkg": "HKG",
    "seúl": "ICN",
    "seoul": "ICN",
    "icn": "ICN",
    "pekín": "PEI",
    "beijing": "PEI",
    "pei": "PEI",
    "shangái": "SHA",
    "shanghai": "SHA",
    "sha": "SHA",
    "delhi": "DEL",
    "del": "DEL",
    "bombay": "BOM",
    "mumbai": "BOM",
    "bom": "BOM",
    "bangkok": "BKK",
    "bkk": "BKK",
    "kuala lumpur": "KUL",
    "kul": "KUL",
    "bangkok": "BKK",
    
    # ORIENTE PRÓXIMO
    "dubai": "DXB",
    "dxb": "DXB",
    "catar": "DOH",
    "qatar": "DOH",
    "doh": "DOH",
    "abu dabi": "AUH",
    "abu dhabi": "AUH",
    "auh": "AUH",
    "teherán": "IKA",
    "tehran": "IKA",
    "ika": "IKA",
    "estambul": "IST",
    
    # OCEANÍA
    "sídney": "SYD",
    "sydney": "SYD",
    "syd": "SYD",
    "melbourne": "MEL",
    "mel": "MEL",
    "auckland": "AKL",
    "akl": "AKL",
    
    # ÁFRICA
    "el cairo": "CAI",
    "cairo": "CAI",
    "cai": "CAI",
    "johannesburgo": "JNB",
    "johannesburg": "JNB",
    "jnb": "JNB",
    "casablanca": "CMN",
    "cmn": "CMN",
}


def traducir_ciudad_a_iata(entrada: str) -> str:
    """
    Traduce un nombre de ciudad (o IATA) a código IATA
    
    CONCEPTO EDUCATIVO - Fuzzy matching:
    - Si es exactamente 3 letras, asume que es IATA
    - Si es un nombre de ciudad, busca en el diccionario
    - Case-insensitive
    - Retorna la entrada en mayúsculas si es IATA válido
    
    Args:
        entrada: "Madrid", "MAD", "paris", "CDG", etc
    
    Returns:
        str: Código IATA en mayúsculas (ej: "MAD", "CDG")
    
    Raises:
        ValueError: Si no puede traducir la entrada
    
    Ejemplo:
        >>> traducir_ciudad_a_iata("madrid")
        'MAD'
        >>> traducir_ciudad_a_iata("MAD")
        'MAD'
        >>> traducir_ciudad_a_iata("invento")
        ValueError: Aeropuerto no encontrado: invento
    """
    entrada_limpia = entrada.strip().lower()
    
    # Si tiene exactamente 3 caracteres, asumir que es IATA
    if len(entrada_limpia) == 3 and entrada_limpia.isalpha():
        # Verificar que sea válido (búsqueda inversa en diccionario)
        iata_mayúscula = entrada_limpia.upper()
        
        # Buscar si existe este IATA en los valores del diccionario
        if iata_mayúscula in AIRPORTS.values():
            return iata_mayúscula
        else:
            # Si no está en nuestro diccionario, igual lo retornamos
            # (podría ser un aeropuerto válido pero no catalogado)
            logger.warning(f"⚠️  IATA '{iata_mayúscula}' no está en nuestro diccionario, pero lo aceptamos")
            return iata_mayúscula
    
    # Si no, buscar en el diccionario de ciudades
    if entrada_limpia in AIRPORTS:
        return AIRPORTS[entrada_limpia]
    
    # Si no encontramos exacto, buscar coincidencia parcial
    for ciudad, iata in AIRPORTS.items():
        if entrada_limpia in ciudad or ciudad in entrada_limpia:
            logger.info(f"   ℹ️  Coincidencia encontrada: '{entrada}' → {iata}")
            return iata
    
    # No encontramos nada
    raise ValueError(f"❌ Aeropuerto no encontrado: '{entrada}'")


def obtener_lista_ciudades_disponibles() -> list:
    """Retorna lista de ciudades/IATA disponibles para consulta"""
    ciudades = []
    for ciudad, iata in sorted(AIRPORTS.items()):
        if ciudad in AIRPORTS and AIRPORTS[ciudad] != iata:
            # Evitar duplicados
            continue
        # Formato: "Madrid (MAD)"
        ciudades.append(f"{ciudad.title()} ({iata})")
    
    # Eliminar duplicados
    return sorted(list(set(ciudades)))


def mostrar_ciudades_disponibles():
    """Muestra todas las ciudades disponibles al usuario"""
    ciudades = obtener_lista_ciudades_disponibles()
    
    print("\n" + "=" * 70)
    print("✈️  CIUDADES Y AEROPUERTOS DISPONIBLES")
    print("=" * 70)
    print()
    
    # Agrupar por continentes (aproximado)
    españas = [c for c in ciudades if "(" in c][:15]
    europa = [c for c in ciudades if any(x in c.lower() for x in ["par", "lon", "ber", "ams", "fra", "mun", "mil", "rom"])][:10]
    usa = [c for c in ciudades if any(x in c.lower() for x in ["york", "angeles", "chicago", "miami", "boston"])][:10]
    
    if españas:
        print("🇪🇸 ESPAÑA:")
        for ciudad in españas:
            print(f"   • {ciudad}")
    
    if europa:
        print("\n🇪🇺 EUROPA:")
        for ciudad in europa:
            print(f"   • {ciudad}")
    
    if usa:
        print("\n🇺🇸 AMÉRICA:")
        for ciudad in usa:
            print(f"   • {ciudad}")
    
    print("\n   (Hay más aeropuertos disponibles, prueba escribiendo una ciudad)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Test de traducción
    print("🧪 Test: Traducción de ciudades a IATA\n")
    
    pruebas = ["Madrid", "MAD", "Barcelona", "BCN", "Paris", "CDG", "Nueva York", "JFK"]
    
    for entrada in pruebas:
        try:
            resultado = traducir_ciudad_a_iata(entrada)
            print(f"✅ '{entrada}' → {resultado}")
        except ValueError as e:
            print(f"❌ {e}")
