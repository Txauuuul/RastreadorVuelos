"""
manage_flights.py - Herramienta interactiva para gestionar vuelos monitoreados

CONCEPTO EDUCATIVO - Interfaz de Usuario (CLI):
Una interfaz de línea de comandos permite al usuario interactuar
con el sistema sin necesidad de saber programación.

Esto es especialmente importante para operaciones de mantenimiento
como agregar/eliminar/modificar vuelos.
"""

import sys
from pathlib import Path
from src.logger import logger
from src.database import Database


def clear_screen():
    """Limpiar la pantalla (compatible con Windows y Linux)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Imprimir un encabezado bonito"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_menu():
    """Mostrar el menú principal"""
    print("\n📋 GESTOR DE VUELOS MONITOREADOS\n")
    print("1️⃣  Ver vuelos monitoreados")
    print("2️⃣  Agregar nuevo vuelo")
    print("3️⃣  Modificar parámetros de un vuelo")
    print("4️⃣  Eliminar vuelo de monitoreo")
    print("5️⃣  Ver historial de precios de un vuelo")
    print("6️⃣  Ver estadísticas")
    print("0️⃣  Salir")
    print()


def list_flights(db: Database):
    """Mostrar todos los vuelos monitoreados"""
    print_header("📋 VUELOS MONITOREADOS")
    
    flights = db.get_all_watched_flights()
    
    if not flights:
        print("\n❌ No hay vuelos monitoreados.\n")
        return
    
    for flight in flights:
        print(f"\n{'─' * 70}")
        print(f"  ID: {flight['id']}")
        print(f"  Ruta: {flight['origin']} → {flight['destination']}")
        print(f"  Fecha salida: {flight['departure_date']}")
        print(f"  Precio mínimo deseado: {flight['min_price']}€")
        print(f"  Alerta reducción: {flight['price_reduction_percent']}%")
        print(f"  Creado: {flight['created_at']}")
    
    print(f"\n{'─' * 70}")
    print(f"\n✅ Total: {len(flights)} vuelo(s) monitoreado(s)\n")


def add_flight(db: Database):
    """Agregar un nuevo vuelo a monitorear"""
    print_header("➕ AGREGAR NUEVO VUELO")
    
    try:
        origin = input("📍 Código IATA origen (ej: MAD): ").strip().upper()
        if len(origin) != 3:
            print("❌ Código IATA debe tener 3 letras\n")
            return False
        
        destination = input("📍 Código IATA destino (ej: CDG): ").strip().upper()
        if len(destination) != 3:
            print("❌ Código IATA debe tener 3 letras\n")
            return False
        
        departure_date = input("📅 Fecha de salida (DD-MM-YYYY, ej: 25-02-2025): ").strip()
        if len(departure_date) != 10 or departure_date[2] != '-' or departure_date[5] != '-':
            print("❌ Formato de fecha incorrecto. Usa DD-MM-YYYY\n")
            return False
        
        while True:
            try:
                min_price = float(input("💰 Precio mínimo deseado (€, ej: 50): ").strip())
                if min_price < 0:
                    print("❌ El precio no puede ser negativo\n")
                    continue
                break
            except ValueError:
                print("❌ Introduce un número válido\n")
        
        while True:
            try:
                reduction_percent = float(input("📉 Alerta reducción respecto a media histórica (%, ej: 15): ").strip())
                if reduction_percent < 0 or reduction_percent > 100:
                    print("❌ El porcentaje debe estar entre 0 y 100\n")
                    continue
                break
            except ValueError:
                print("❌ Introduce un número válido\n")
        
        # Agregar a la BD
        success = db.add_watched_flight(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            min_price=min_price,
            price_reduction_percent=reduction_percent
        )
        
        if success:
            print(f"\n✅ Vuelo agregado correctamente:")
            print(f"   {origin} → {destination} ({departure_date})")
            print(f"   Precio mínimo: {min_price}€")
            print(f"   Alerta reducción: {reduction_percent}%\n")
            return True
        else:
            print("\n⚠️ Este vuelo ya estaba en monitoreo\n")
            return False
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada\n")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False


def modify_flight(db: Database):
    """Modificar parámetros de un vuelo"""
    print_header("✏️ MODIFICAR PARÁMETROS DE UN VUELO")
    
    try:
        flights = db.get_all_watched_flights()
        
        if not flights:
            print("\n❌ No hay vuelos para modificar\n")
            return False
        
        # Mostrar vuelos disponibles
        print("\n📋 Vuelos disponibles:\n")
        for flight in flights:
            print(f"  ID {flight['id']}: {flight['origin']}→{flight['destination']} ({flight['departure_date']})")
        
        while True:
            try:
                flight_id = int(input("\n🔍 Introduce el ID del vuelo a modificar: ").strip())
                flight = db.get_watched_flight(flight_id)
                if flight:
                    break
                print("❌ ID no encontrado")
            except ValueError:
                print("❌ Introduce un número válido")
        
        print(f"\n✏️ Modificando: {flight['origin']}→{flight['destination']}")
        print(f"   Valores actuales:")
        print(f"   - Precio mínimo: {flight['min_price']}€")
        print(f"   - Alerta reducción: {flight['price_reduction_percent']}%\n")
        
        while True:
            try:
                new_min_price = float(input("💰 Nuevo precio mínimo (€, Enter para mantener): ") or flight['min_price'])
                if new_min_price < 0:
                    print("❌ El precio no puede ser negativo\n")
                    continue
                break
            except ValueError:
                print("❌ Introduce un número válido\n")
        
        while True:
            try:
                new_reduction = float(input("📉 Nuevo porcentaje reducción (%, Enter para mantener): ") or flight['price_reduction_percent'])
                if new_reduction < 0 or new_reduction > 100:
                    print("❌ El porcentaje debe estar entre 0 y 100\n")
                    continue
                break
            except ValueError:
                print("❌ Introduce un número válido\n")
        
        # Actualizar en BD
        import sqlite3
        db_path = db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE watched_flights
                SET min_price = ?, price_reduction_percent = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_min_price, new_reduction, flight_id))
            conn.commit()
        
        print(f"\n✅ Vuelo modificado correctamente:")
        print(f"   Precio mínimo: {new_min_price}€")
        print(f"   Alerta reducción: {new_reduction}%\n")
        return True
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada\n")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False


def delete_flight(db: Database):
    """Eliminar un vuelo de monitoreo"""
    print_header("🗑️ ELIMINAR VUELO DE MONITOREO")
    
    try:
        flights = db.get_all_watched_flights()
        
        if not flights:
            print("\n❌ No hay vuelos para eliminar\n")
            return False
        
        # Mostrar vuelos disponibles
        print("\n📋 Vuelos disponibles:\n")
        for flight in flights:
            print(f"  ID {flight['id']}: {flight['origin']}→{flight['destination']} ({flight['departure_date']})")
        
        while True:
            try:
                flight_id = int(input("\n🔍 Introduce el ID del vuelo a eliminar: ").strip())
                flight = db.get_watched_flight(flight_id)
                if flight:
                    break
                print("❌ ID no encontrado")
            except ValueError:
                print("❌ Introduce un número válido")
        
        confirm = input(f"\n⚠️  ¿Deseas eliminar {flight['origin']}→{flight['destination']}? (s/n): ").strip().lower()
        
        if confirm == 's':
            db.deactivate_watched_flight(flight_id)
            print(f"\n✅ Vuelo eliminado correctamente\n")
            return True
        else:
            print("\n❌ Operación cancelada\n")
            return False
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada\n")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False


def view_price_history(db: Database):
    """Ver historial de precios de un vuelo"""
    print_header("📊 HISTORIAL DE PRECIOS")
    
    try:
        flights = db.get_all_watched_flights()
        
        if not flights:
            print("\n❌ No hay vuelos disponibles\n")
            return
        
        # Mostrar vuelos disponibles
        print("\n📋 Vuelos disponibles:\n")
        for flight in flights:
            print(f"  ID {flight['id']}: {flight['origin']}→{flight['destination']} ({flight['departure_date']})")
        
        while True:
            try:
                flight_id = int(input("\n🔍 Introduce el ID del vuelo: ").strip())
                flight = db.get_watched_flight(flight_id)
                if flight:
                    break
                print("❌ ID no encontrado")
            except ValueError:
                print("❌ Introduce un número válido")
        
        history = db.get_price_history(flight_id, days=30)
        
        if not history:
            print(f"\n❌ Sin historial de precios para {flight['origin']}→{flight['destination']}\n")
            return
        
        print(f"\n📊 Historial de {flight['origin']}→{flight['destination']} (últimos 30 días):\n")
        
        for i, record in enumerate(history, 1):
            print(f"{i}. {record['check_date']}: {record['price']}€ ({record['airline']} {record['flight_number']})")
        
        # Estadísticas
        avg = db.get_average_price(flight_id, days=30)
        min_price = db.get_min_price(flight_id, days=30)
        
        print(f"\n📈 Estadísticas (últimos 30 días):")
        print(f"   Precio promedio: {avg:.2f}€")
        print(f"   Precio mínimo: {min_price:.2f}€")
        print()
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def view_statistics(db: Database):
    """Ver estadísticas globales"""
    print_header("📊 ESTADÍSTICAS GLOBALES")
    
    try:
        stats = db.get_statistics()
        alerts = db.get_alerts_history(days=30)
        
        print(f"\n✈️ Vuelos activos: {stats['active_flights']}")
        print(f"📈 Registros de precio: {stats['price_records']}")
        print(f"🔔 Alertas enviadas (últimos 30 días): {stats['alerts_sent']}")
        
        if alerts:
            by_type = {}
            for alert in alerts:
                alert_type = alert['alert_type']
                by_type[alert_type] = by_type.get(alert_type, 0) + 1
            
            print(f"\n📊 Alertas por tipo:")
            for alert_type, count in by_type.items():
                print(f"   • {alert_type}: {count}")
        
        print()
    
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def main():
    """Función principal"""
    print("\n🛫 BIENVENIDO AL GESTOR DE VUELOS\n")
    
    try:
        db = Database()
    except Exception as e:
        print(f"❌ Error conectando a la BD: {e}")
        sys.exit(1)
    
    while True:
        print_menu()
        choice = input("🔹 Elige una opción (0-6): ").strip()
        
        if choice == '0':
            print("\n👋 ¡Hasta luego!\n")
            break
        elif choice == '1':
            list_flights(db)
        elif choice == '2':
            add_flight(db)
        elif choice == '3':
            modify_flight(db)
        elif choice == '4':
            delete_flight(db)
        elif choice == '5':
            view_price_history(db)
        elif choice == '6':
            view_statistics(db)
        else:
            print("❌ Opción no válida. Intenta de nuevo.\n")
        
        if choice in ['1', '2', '3', '4', '5', '6']:
            input("Presiona Enter para continuar...")


if __name__ == "__main__":
    main()
