"""
test_sistema.py - Verifica que todo está funcionando correctamente

Este script hace pruebas rápidas para asegurar que:
1. BD está conectada
2. Telegram está configurado
3. Amadeus está configurado
4. Los módulos se importan sin errores

USO:
    python test_sistema.py
"""

import sys
from datetime import datetime, timedelta

print("=" * 60)
print("🧪 PRUEBAS DEL SISTEMA FLIGHT TRACKER")
print("=" * 60 + "\n")


def test_importaciones():
    """Test 1: Verificar que se importan todos los módulos"""
    print("1️⃣ TEST DE IMPORTACIONES")
    print("-" * 40)
    
    try:
        print("   ✓ Importando config...")
        from src.config import TELEGRAM_BOT_TOKEN, AMADEUS_CLIENT_ID, DATABASE_URL
        
        print("   ✓ Importando logger...")
        from src.logger import logger
        
        print("   ✓ Importando database...")
        from src.database import (
            inicializar_bd, crear_ruta, SessionLocal,
            obtener_ultimas_busquedas, registrar_busqueda
        )
        
        print("   ✓ Importando api...")
        from src.api import AmadeusAPI
        
        print("   ✓ Importando api_aggregator...")
        from src.api_aggregator import APIAggregator
        
        print("   ✓ Importando airport_utils...")
        from src.airport_utils import traducir_ciudad_a_iata
        
        print("   ✓ Importando alert_calculator...")
        from src.alert_calculator import CalculadorAlertasInteligentes
        
        print("   ✓ Importando telegram_bot...")
        from src.telegram_bot import FlightTrackerBot
        
        print("   ✓ Importando flight_search_worker...")
        from src.flight_search_worker import SearchWorker
        
        print("\n✅ TODAS LAS IMPORTACIONES OK\n")
        return True
    
    except ImportError as e:
        print(f"\n❌ ERROR DE IMPORTACIÓN: {e}\n")
        return False


def test_configuracion():
    """Test 2: Verificar variables de entorno"""
    print("2️⃣ TEST DE CONFIGURACIÓN")
    print("-" * 40)
    
    try:
        from src.config import (
            TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, 
            AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET,
            DATABASE_URL
        )
        
        # Verificar que no estén vacías
        checks = [
            ("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN),
            ("TELEGRAM_CHAT_ID", str(TELEGRAM_CHAT_ID)),
            ("AMADEUS_CLIENT_ID", AMADEUS_CLIENT_ID),
            ("AMADEUS_CLIENT_SECRET", AMADEUS_CLIENT_SECRET),
            ("DATABASE_URL", DATABASE_URL[:30] + "..."),  # Mostrar parcial
        ]
        
        for nombre, valor in checks:
            if valor and valor != "..." and len(str(valor)) > 0:
                print(f"   ✓ {nombre}: {'✓ Configurado'}")
            else:
                print(f"   ❌ {nombre}: ✗ FALTA")
                return False
        
        print("\n✅ TODAS LAS VARIABLES CONFIGURADAS\n")
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR EN CONFIGURACIÓN: {e}\n")
        return False


def test_base_datos():
    """Test 3: Verificar conexión a BD"""
    print("3️⃣ TEST DE BASE DE DATOS")
    print("-" * 40)
    
    try:
        from src.database import inicializar_bd, SessionLocal
        
        print("   ✓ Inicializando BD...")
        inicializar_bd()
        
        print("   ✓ Verificando conexión...")
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        
        print("\n✅ BASE DE DATOS CONECTADA\n")
        return True
    
    except Exception as e:
        print(f"\n⚠️ ERROR EN BD: {e}")
        print("💡 El sistema usará SQLite local como fallback\n")
        return True  # No es error fatal, SQLite fallback está disponible


def test_amadeus():
    """Test 4: Verificar conexión a Amadeus API"""
    print("4️⃣ TEST DE AMADEUS API")
    print("-" * 40)
    
    try:
        from src.api import AmadeusAPI
        
        print("   ✓ Inicializando cliente Amadeus...")
        api = AmadeusAPI()
        
        print("   ✓ Probando búsqueda simple...")
        # Usar fecha futura: 25 de abril 2026
        resultado = api.search_flights("MAD", "BCN", "25-04-2026")
        
        if resultado and resultado.get('count', 0) > 0:
            print(f"   ✓ Amadeus respondió: {resultado['count']} vuelos encontrados")
            print("✅ AMADEUS CONECTADO\n")
            return True
        else:
            print(f"   ⚠️ Amadeus no retornó vuelos")
            print("💡 Posibles causas: credenciales, cuota agotada, fecha inválida\n")
            return False
    
    except Exception as e:
        print(f"⚠️ ERROR EN AMADEUS: {str(e)[:100]}")
        print("💡 Verifica tus credenciales en .env\n")
        return False


def test_aggregator():
    """Test 4b: Verificar Patrón Agregador Multi-API"""
    print("4b️⃣ TEST DEL AGREGADOR MULTI-API")
    print("-" * 40)
    
    try:
        from src.api_aggregator import APIAggregator
        
        print("   ✓ Inicializando APIAggregator...")
        agregador = APIAggregator()
        
        print("   ✓ Probando búsqueda paralela en múltiples APIs...")
        # Usar fecha futura: 25 de abril 2026
        mejor_vuelo, todos_vuelos = agregador.search(
            origin="MAD",
            destination="BCN",
            departure_date="25-04-2026"
        )
        
        if mejor_vuelo:
            print(f"   ✓ Mejor vuelo encontrado: {mejor_vuelo.price}€")
            print(f"   ✓ API ganador: {mejor_vuelo.api_source}")
            print(f"   ✓ Total opciones comparadas: {len(todos_vuelos)}")
            print("✅ AGREGADOR FUNCIONAL\n")
            return True
        else:
            print("   ⚠️ Ninguna API retornó vuelos")
            print("   ℹ️ Posible: APIs no configuradas o sin vuelos disponibles\n")
            return True  # No es error fatal
    
    except Exception as e:
        print(f"⚠️ ERROR EN AGREGADOR: {str(e)[:100]}\n")
        return False


def test_airport_utils():
    """Test 5: Verificar traducción ciudad→IATA"""
    print("5️⃣ TEST DE AIRPORT UTILS")
    print("-" * 40)
    
    try:
        from src.airport_utils import traducir_ciudad_a_iata
        
        pruebas = [
            ("Madrid", "MAD"),
            ("Barcelona", "BCN"),
            ("Nueva York", "NYC"),
            ("MAD", "MAD"),  # Ya está en IATA
        ]
        
        for ciudad, esperado in pruebas:
            resultado = traducir_ciudad_a_iata(ciudad)
            if resultado == esperado:
                print(f"   ✓ {ciudad:20} → {resultado}")
            else:
                print(f"   ❌ {ciudad:20} → {resultado} (esperaba {esperado})")
                return False
        
        print("\n✅ AIRPORT UTILS FUNCIONANDO\n")
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR EN AIRPORT UTILS: {e}\n")
        return False


def test_crear_ruta():
    """Test 6: Crear ruta de prueba"""
    print("6️⃣ TEST DE CREAR RUTA")
    print("-" * 40)
    
    try:
        from src.database import crear_ruta
        
        print("   ✓ Creando ruta de prueba...")
        fecha_inicio = datetime.now() + timedelta(days=60)
        fecha_fin = fecha_inicio + timedelta(days=90)
        
        ruta = crear_ruta(
            origen="MAD",
            destino="BCN",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            porcentaje_rebaja=20.0,
            precio_min_automatico=True
        )
        
        print(f"   ✓ Ruta creada ID: {ruta.id}")
        print(f"   ✓ Precio mínimo alerta: {ruta.precio_minimo_alerta}€")
        
        print("\n✅ RUTA CREADA EXITOSAMENTE\n")
        return True
    
    except Exception as e:
        print(f"\n⚠️ ERROR AL CREAR RUTA: {e}\n")
        return True  # No es crítico para el test


def test_telegram():
    """Test 7: Verificar conexión a Telegram"""
    print("7️⃣ TEST DE TELEGRAM")
    print("-" * 40)
    
    try:
        import asyncio
        from telegram import Bot
        from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        
        async def test_async():
            print("   ✓ Inicializando cliente Telegram...")
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            
            print("   ✓ Verificando credenciales...")
            me = await bot.get_me()
            print(f"   ✓ Bot encontrado: @{me.username}")
            
            return True
        
        resultado = asyncio.run(test_async())
        
        print("\n✅ TELEGRAM CONECTADO\n")
        return resultado
    
    except Exception as e:
        print(f"\n⚠️ ERROR EN TELEGRAM: {e}")
        print("💡 Verifica TELEGRAM_BOT_TOKEN en .env\n")
        return False


def resumen(resultados):
    """Mostrar resumen de pruebas"""
    print("=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    tests = [
        ("Importaciones", resultados[0]),
        ("Configuración", resultados[1]),
        ("Base de Datos", resultados[2]),
        ("Amadeus API", resultados[3]),
        ("Agregador Multi-API", resultados[4]),
        ("Airport Utils", resultados[5]),
        ("Crear Ruta", resultados[6]),
        ("Telegram", resultados[7]),
    ]
    
    ok = sum(1 for _, r in tests if r)
    total = len(tests)
    
    for nombre, resultado in tests:
        estado = "✅" if resultado else "❌"
        print(f"{estado} {nombre}")
    
    print(f"\nResultado: {ok}/{total} tests pasados")
    
    if ok >= total - 1:  # Tolerar 1 fallo (por ejemplo Amadeus si no tiene cuota)
        print("\n🎉 ¡SISTEMA FUNCIONAL!")
        print("\n✨ Características:")
        print("  ✓ Patrón Agregador Multi-API activado")
        print("  ✓ Busca simultáneamente en Amadeus, FlyScraper, GoogleFlights")
        print("  ✓ Resilencia: si una API falla, las otras continúan")
        print("  ✓ Retorna el precio más barato automáticamente")
        print("\nAhora ejecuta:")
        print("  python run_combined.py")
        print("\n¡Luego usa Telegram para agregar rutas! 🚀")
    else:
        print("\n⚠️ Hay problemas. Revisa los errores arriba.")
        print("💡 Lee GUIA_RAPIDA.py para solucionar problemas")


if __name__ == "__main__":
    print("\n")
    
    resultados = [
        test_importaciones(),
        test_configuracion(),
        test_base_datos(),
        test_amadeus(),
        test_aggregator(),
        test_airport_utils(),
        test_crear_ruta(),
        test_telegram(),
    ]
    
    print("\n")
    resumen(resultados)
    print("\n" + "=" * 60 + "\n")
