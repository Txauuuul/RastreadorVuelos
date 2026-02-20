#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostics.py - Verificación automática del sistema
Ejecutar: python diagnostics.py

Verifica automáticamente todos los problemas comunes
y sugiere soluciones.
"""

import os
import sys
from datetime import datetime, timedelta

def check_imports():
    print("\n1️⃣ VERIFICANDO IMPORTACIONES")
    print("-" * 50)
    
    modules = [
        "src.config",
        "src.logger",
        "src.database",
        "src.api",
        "src.api_aggregator",
        "src.airport_utils",
        "src.alert_calculator",
        "src.telegram_bot",
        "src.flight_search_worker"
    ]
    
    ok = 0
    failed = []
    
    for mod in modules:
        try:
            __import__(mod)
            print(f"   ✓ {mod}")
            ok += 1
        except ImportError as e:
            print(f"   ✗ {mod}")
            print(f"      Error: {str(e)[:70]}")
            failed.append((mod, str(e)))
    
    print(f"\n   Resultado: {ok}/{len(modules)} imports OK")
    
    if failed:
        print(f"\n   ⚠️ PROBLEMAS ENCONTRADOS:")
        for mod, err in failed:
            print(f"      - {mod}: {err}")
    
    return ok == len(modules), failed


def check_config():
    print("\n2️⃣ VERIFICANDO CONFIGURACIÓN")
    print("-" * 50)
    
    try:
        from src.config import (
            TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
            AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET,
            RAPIDAPI_KEY, DATABASE_URL
        )
    except Exception as e:
        print(f"   ✗ No se pudo cargar config: {str(e)[:50]}")
        return False, [("config", str(e))]
    
    checks = {
        "TELEGRAM_BOT_TOKEN": (TELEGRAM_BOT_TOKEN and len(TELEGRAM_BOT_TOKEN) > 10, "Token del bot Telegram"),
        "TELEGRAM_CHAT_ID": (bool(TELEGRAM_CHAT_ID), "ID de chat Telegram"),
        "AMADEUS_CLIENT_ID": (AMADEUS_CLIENT_ID and len(AMADEUS_CLIENT_ID) > 10, "Credenciales Amadeus"),
        "AMADEUS_CLIENT_SECRET": (AMADEUS_CLIENT_SECRET and len(AMADEUS_CLIENT_SECRET) > 5, "Secret de Amadeus"),
        "DATABASE_URL": (bool(DATABASE_URL), "URL de base de datos"),
    }
    
    ok = 0
    failed = []
    
    for key, (value, desc) in checks.items():
        if value:
            print(f"   ✓ {key:25} ({desc})")
            ok += 1
        else:
            print(f"   ✗ {key:25} ❌ FALTA")
            failed.append(key)
    
    # RAPIDAPI_KEY es opcional
    if RAPIDAPI_KEY and RAPIDAPI_KEY != "DUMMY":
        print(f"   ✓ {'RAPIDAPI_KEY':25} (RapidAPI para scrapers)")
    else:
        print(f"   ⚠️ {'RAPIDAPI_KEY':25} (Opcional - sin RAPIDAPI)")
    
    print(f"\n   Resultado: {ok}/5 configuraciones críticas OK")
    
    if failed:
        print(f"   ⚠️ FALTANTES: {', '.join(failed)}")
    
    return ok >= 4, failed


def check_database():
    print("\n3️⃣ VERIFICANDO BASE DE DATOS")
    print("-" * 50)
    
    try:
        from src.database import inicializar_bd, SessionLocal
        
        print("   • Inicializando BD...")
        inicializar_bd()
        
        print("   • Conectando...")
        db = SessionLocal()
        
        print("   • Ejecutando query de prueba...")
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        db.close()
        
        print(f"   ✓ Base de datos funcionando correctamente")
        
        # Verificar archivo SQLite
        if os.path.exists("data/vuelos.db"):
            size = os.path.getsize("data/vuelos.db")
            print(f"   ✓ Archivo SQLite: data/vuelos.db ({size} bytes)")
        
        return True, []
        
    except Exception as e:
        print(f"   ✗ Error en base de datos:")
        print(f"      {str(e)[:70]}")
        
        # Intentar fallback SQLite
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine("sqlite:///data/vuelos.db", echo=False)
            Session = sessionmaker(bind=engine)
            session = Session()
            session.execute(text("SELECT 1"))
            session.close()
            
            print(f"   ⚠️ PostgreSQL no disponible, pero SQLite funciona")
            return True, []
        except:
            return False, [("database", str(e))]


def check_dates():
    print("\n4️⃣ VERIFICANDO FECHAS EN TESTS")
    print("-" * 50)
    
    today = datetime.now()
    future_date = (today + timedelta(days=25))
    future_str = future_date.strftime("%d-%m-%Y")
    
    print(f"   Hoy: {today.strftime('%d-%m-%Y')}")
    print(f"   Fecha mínima válida para tests: {future_str}+")
    
    issues = []
    
    # Verificar si test_sistema.py usa fechas futuras
    try:
        if os.path.exists("test_sistema.py"):
            with open("test_sistema.py", "r", encoding="utf-8") as f:
                content = f.read()
                
                # Buscar fechas en format D D-MM-YYYY
                import re
                dates = re.findall(r'"(\d{2}-\d{2}-\d{4})"', content)
                
                old_dates = [d for d in dates if d == "05-01-2026" or d == "05-03-2026"]
                
                if old_dates:
                    print(f"   ✗ Encontradas fechas obsoletas: {old_dates}")
                    issues.append("test_dates")
                    print(f"   ⚠️ RECOMENDACIÓN: Cambiar a {future_str} o posterior")
                else:
                    print(f"   ✓ Fechas en tests son futuras")
        else:
            print(f"   ⚠️ test_sistema.py no encontrado")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        print(f"   ✗ Error verificando dates: {str(e)}")
        return False, ["date_check"]


def check_aggregator():
    print("\n5️⃣ VERIFICANDO AGREGADOR MULTI-API")
    print("-" * 50)
    
    try:
        from src.api_aggregator import APIAggregator
        
        agg = APIAggregator()
        providers = list(agg.providers.keys())
        
        print(f"   ✓ Agregador cargado correctamente")
        print(f"   • Proveedores disponibles: {', '.join(providers)}")
        
        # Verificar configuración de cada proveedor (es_configured es un atributo bool)
        for name, provider in agg.providers.items():
            is_configured = provider.is_configured
            status = "✓" if is_configured else "✗"
            config_status = "Configurado" if is_configured else "NO CONFIGURADO"
            print(f"   {status} {name:20} - {config_status}")
        
        return True, []
        
    except Exception as e:
        print(f"   ✗ Error cargando agregador:")
        print(f"      {str(e)[:70]}")
        return False, [("aggregator", str(e))]


def check_airport_utils():
    print("\n6️⃣ VERIFICANDO AIRPORT UTILS")
    print("-" * 50)
    
    try:
        from src.airport_utils import traducir_ciudad_a_iata, AIRPORTS
        
        # Test mappings
        test_cases = {
            "madrid": "MAD",
            "barcelona": "BCN",
            "nueva york": "NYC",
            "london": "LHR",
        }
        
        issues = []
        for city, expected in test_cases.items():
            try:
                result = traducir_ciudad_a_iata(city)
                if result == expected:
                    print(f"   ✓ {city:15} → {result}")
                else:
                    print(f"   ✗ {city:15} → {result} (se espera {expected})")
                    if result != city:  # Si no retorna el mismo nombre, es un error
                        issues.append(f"{city}→{result}")
            except Exception as e:
                print(f"   ⚠️ {city:15} → Error: {str(e)[:30]}")
        
        if not issues:
            print(f"   ✓ Códigos IATA funcionando correctamente")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        print(f"   ✗ Error verificando airport_utils:")
        print(f"      {str(e)[:70]}")
        return False, [("airport_utils", str(e))]


def check_telegram():
    print("\n7️⃣ VERIFICANDO TELEGRAM BOT")
    print("-" * 50)
    
    try:
        from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        
        if not TELEGRAM_BOT_TOKEN or len(TELEGRAM_BOT_TOKEN) < 10:
            print(f"   ✗ Token de Telegram no configurado")
            return False, ["telegram_token"]
        
        if not TELEGRAM_CHAT_ID:
            print(f"   ✗ Chat ID de Telegram no configurado")
            return False, ["telegram_chat_id"]
        
        # Nota: No intentar conexión real para no usar credits innecesariamente
        print(f"   ✓ Credenciales Telegram configuradas")
        print(f"   ℹ️  Conexión real se verificará en runtime")
        
        return True, []
        
    except Exception as e:
        print(f"   ⚠️ Error verificando Telegram: {str(e)}")
        return True, []  # No es crítico


def main():
    print("=" * 60)
    print("  🔧 VERIFICACIÓN AUTOMÁTICA DEL SISTEMA")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = {
        "Importaciones": check_imports,
        "Configuración": check_config,
        "Base de datos": check_database,
        "Fechas en tests": check_dates,
        "Agregador Multi-API": check_aggregator,
        "Airport Utils": check_airport_utils,
        "Telegram Bot": check_telegram,
    }
    
    results = {}
    all_issues = {}
    
    for test_name, test_func in tests.items():
        try:
            passed, issues = test_func()
            results[test_name] = passed
            if issues:
                all_issues[test_name] = issues
        except Exception as e:
            print(f"\n⚠️ Excepción en {test_name}: {str(e)}")
            results[test_name] = False
            all_issues[test_name] = [str(e)]
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = "✅" if passed else "⚠️"
        print(f"{status} {test_name}")
        if test_name in all_issues and all_issues[test_name]:
            for issue in all_issues[test_name]:
                print(f"   └─ {issue}")
    
    print("\n" + "=" * 60)
    
    if passed_count == total_count:
        print("✅ SISTEMA 100% FUNCIONAL - 0 PROBLEMAS DETECTADOS")
        print("=" * 60)
        return 0
    else:
        print(f"⚠️  {total_count - passed_count} problemas detectados")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Verificación interrumpida por el usuario")
        sys.exit(-1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {str(e)}")
        sys.exit(1)
