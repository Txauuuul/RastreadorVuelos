#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_rapidapi.py - Verificar conexión a RapidAPI

Prueba los nuevos endpoints:
1. fly-scraper.p.rapidapi.com/v2/flights/search-roundtrip
2. flights-scraper-data.p.rapidapi.com/flights/search-roundtrip
"""

import requests
from datetime import datetime, timedelta
from src.config import RAPIDAPI_KEY
from src.logger import logger

# Dates de prueba
departure = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
print(f"Fecha de prueba: {departure}\n")

# ==================== TEST 1: Fly Scraper v2 ====================
print("="*60)
print("TEST 1: Fly Scraper v2 (NUEVO)")
print("="*60)

url_flyscraper = "https://fly-scraper.p.rapidapi.com/v2/flights/search-roundtrip"
headers_flyscraper = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "fly-scraper.p.rapidapi.com",
    "Content-Type": "application/json"
}
params_flyscraper = {
    "originSkyId": "MADM",
    "destinationSkyId": "BARCM"
}

print(f"\n📍 URL: {url_flyscraper}")
print(f"📋 Parámetros: {params_flyscraper}")
print(f"\nIntentando conexión...")

try:
    response = requests.get(url_flyscraper, headers=headers_flyscraper, params=params_flyscraper, timeout=10)
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Response Time: {response.elapsed.total_seconds():.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ ÉXITO: Respuesta recibida")
        if isinstance(data, dict) and 'data' in data:
            flights = data.get('data', {}).get('flights', [])
            print(f"   Vuelos encontrados: {len(flights)}")
        else:
            print(f"   Estructura: {type(data)}")
    else:
        print(f"❌ ERROR {response.status_code}: {response.reason}")
        print(f"   Respuesta: {response.text[:200]}")
except requests.Timeout:
    print(f"❌ TIMEOUT: La API no responde dentro de 10 segundos")
except Exception as e:
    print(f"❌ EXCEPCIÓN: {str(e)}")

# ==================== TEST 2: Flights Scraper Data ====================
print("\n" + "="*60)
print("TEST 2: Flights Scraper Data (NUEVO)")
print("="*60)

url_flights = "https://flights-scraper-data.p.rapidapi.com/flights/search-roundtrip"
headers_flights = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "flights-scraper-data.p.rapidapi.com",
    "Content-Type": "application/json"
}
params_flights = {
    "departureId": "MAD",
    "arrivalId": "BCN"
}

print(f"\n📍 URL: {url_flights}")
print(f"📋 Parámetros: {params_flights}")
print(f"\nIntentando conexión...")

try:
    response = requests.get(url_flights, headers=headers_flights, params=params_flights, timeout=10)
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Response Time: {response.elapsed.total_seconds():.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ ÉXITO: Respuesta recibida")
        if isinstance(data, dict) and 'flights' in data:
            flights = data.get('flights', [])
            print(f"   Vuelos encontrados: {len(flights)}")
        else:
            print(f"   Estructura: {type(data)}")
    else:
        print(f"❌ ERROR {response.status_code}: {response.reason}")
        print(f"   Respuesta: {response.text[:200]}")
except requests.Timeout:
    print(f"❌ TIMEOUT: La API no responde dentro de 10 segundos")
except Exception as e:
    print(f"❌ EXCEPCIÓN: {str(e)}")

# ==================== RESUMEN ====================
print("\n" + "="*60)
print("📋 RESULTADO")
print("="*60)

print(f"""
PRÓXIMOS PASOS:
1. Si ambas retornan 200 ✅: Excelente, APIs funcionando
2. Si retornan 401/403: Verificar suscripción en https://rapidapi.com
3. Si retornan 404: Verificar endpoint correcto en documentación
""")

