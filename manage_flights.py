"""
manage_flights.py - Interfaz interactiva para gestionar rutas de vuelos

CONCEPTO EDUCATIVO - CLI (Command Line Interface):
Un CLI permite que el usuario interactúe con el programa a través de
preguntas en la terminal. Es simple pero poderoso.

USO:
    python manage_flights.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.logger import logger
from src.database import crear_ruta, obtener_rutas_activas, SessionLocal, Ruta
from src.alert_calculator import CalculadorAlertasInteligentes
from src.airport_utils import traducir_ciudad_a_iata, mostrar_ciudades_disponibles


def validar_codigo_iata(codigo: str) -> bool:
    """Validar que sea un código IATA válido (3 letras mayúsculas)"""
    return len(codigo) == 3 and codigo.isupper() and codigo.isalpha()


def solicitar_codigo_aeropuerto(tipo: str = "origen") -> str:
    """
    Pedir un código IATA válido al usuario
    
    CONCEPTO EDUCATIVO - Inteligencia:
    Ahora acepta TANTO códigos IATA ("MAD") COMO nombres de ciudades ("Madrid")
    El sistema automáticamente traduce ciudades a IATA
    """
    while True:
        print(f"\n  📍 Código IATA de {tipo}")
        print(f"     (Puedes escribir ciudad: 'Madrid' o IATA: 'MAD')")
        print(f"     (Escribe '?' para ver lista de aeropuertos)")
        
        entrada = input(f"  > ").strip()
        
        # Si pide ayuda, mostrar lista
        if entrada == "?":
            mostrar_ciudades_disponibles()
            continue
        
        if not entrada:
            print(f"  ❌ Por favor, introduce algo")
            continue
        
        try:
            # Intentar traducir (acepta ciudad O IATA)
            iata = traducir_ciudad_a_iata(entrada)
            print(f"  ✅ Aceptado: {iata}")
            return iata
        
        except ValueError as e:
            print(f"  ❌ {e}")
            print(f"  💡 Intenta con: 'Madrid', 'MAD', 'Barcelona', 'Paris', etc.")
            print(f"  💡 O escribe '?' para ver la lista completa\n")


def solicitar_fecha(mensaje: str, fecha_minima: datetime = None) -> datetime:
    """Pedir una fecha al usuario (formato: DD-MM-YYYY)"""
    while True:
        fecha_str = input(f"  📅 {mensaje} (DD-MM-YYYY): ").strip()
        try:
            fecha = datetime.strptime(fecha_str, "%d-%m-%Y")
            
            if fecha_minima and fecha < fecha_minima:
                print(f"  ❌ La fecha debe ser posterior a {fecha_minima.strftime('%d-%m-%Y')}")
                continue
            
            return fecha
        except ValueError:
            print(f"  ❌ Formato inválido. Usa DD-MM-YYYY")


def solicitar_rango_dias(mensaje: str) -> tuple:
    """Pedir un rango de días (ej: 10-20)"""
    while True:
        rango_str = input(f"  ⏱️  {mensaje} (ej: 10-20): ").strip()
        try:
            partes = rango_str.split("-")
            if len(partes) != 2:
                raise ValueError("Debe ser un rango con - entre los números")
            
            min_dias = int(partes[0].strip())
            max_dias = int(partes[1].strip())
            
            if min_dias < 1 or max_dias < 1:
                raise ValueError("Los días deben ser mayores a 0")
            
            if min_dias > max_dias:
                raise ValueError("El mínimo no puede ser mayor que el máximo")
            
            return min_dias, max_dias
        except (ValueError, IndexError) as e:
            print(f"  ❌ Inválido: {e}")


def solicitar_si_no(pregunta: str) -> bool:
    """Pedir S/N al usuario"""
    while True:
        respuesta = input(f"  ❓ {pregunta} (S/N): ").strip().upper()
        if respuesta in ("S", "SI"):
            return True
        elif respuesta in ("N", "NO"):
            return False
        else:
            print(f"  ❌ Responde S o N")


def solicitar_porcentaje(mensaje: str, default: float = 15.0) -> float:
    """Pedir un porcentaje al usuario"""
    while True:
        respuesta = input(f"  % {mensaje} (default {default}%): ").strip()
        
        if not respuesta:
            return default
        
        try:
            porcentaje = float(respuesta)
            if 0 < porcentaje <= 100:
                return porcentaje
            else:
                print("  ❌ El porcentaje debe estar entre 1 y 100")
        except ValueError:
            print("  ❌ Introduce un número válido")


def agregar_nueva_ruta():
    """
    Interfaz interactiva para agregar una nueva ruta
    
    Pregunta al usuario:
    1. De dónde a dónde
    2. Fechas de búsqueda
    3. ¿Vuelo de regreso?
    4. Rango de días para regreso
    5. Porcentaje de rebaja deseado
    """
    logger.info("\n" + "=" * 70)
    logger.info("✏️  AGREGAR NUEVA RUTA DE VUELO")
    logger.info("=" * 70)
    
    print("\n🛫 Información del viaje:")
    
    # 1. Origen y destino
    origen = solicitar_codigo_aeropuerto("origen")
    destino = solicitar_codigo_aeropuerto("destino")
    
    if origen == destino:
        print("  ❌ Error: El origen y destino no pueden ser iguales")
        return False
    
    # 2. Rango de fechas
    print(f"\n🗓️  Rango de fechas para buscar vuelos de {origen}→{destino}:")
    fecha_inicio = solicitar_fecha("Fecha de inicio (hoy o posterior)")
    fecha_fin = solicitar_fecha("Fecha de fin (posterior a inicio)", fecha_inicio)
    
    dias_totales = (fecha_fin - fecha_inicio).days
    print(f"  ℹ️  Rango: {dias_totales} días")
    
    # 3. ¿Ida y vuelta?
    es_ida_vuelta = solicitar_si_no("¿Buscas vuelo de regreso?")
    dias_regreso_min = None
    dias_regreso_max = None
    
    if es_ida_vuelta:
        print(f"\n✈️  Información del vuelo de regreso ({destino}→{origen}):")
        dias_regreso_min, dias_regreso_max = solicitar_rango_dias(
            "¿Cuántos días después de la llegada? (ej: 5-10)"
        )
        print(f"  ℹ️  Regreso: entre {dias_regreso_min} y {dias_regreso_max} días después")
    
    # 4. Porcentaje de rebaja
    print(f"\n💰 Configuración de alertas:")
    porcentaje_rebaja = solicitar_porcentaje(
        "¿A qué porcentaje de rebaja quieres alerta?",
        default=15.0
    )
    
    print(f"  ℹ️  Recibirás alertas cuando el precio baje {porcentaje_rebaja}% vs media")
    
    # 5. Resumen antes de crear
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE LA RUTA:")
    print("=" * 70)
    print(f"  Origen → Destino: {origen} → {destino}")
    print(f"  Búsqueda IDA: {fecha_inicio.strftime('%d-%m-%Y')} a {fecha_fin.strftime('%d-%m-%Y')}")
    print(f"  Vuelo de regreso: {'SÍ' if es_ida_vuelta else 'NO'}")
    
    if es_ida_vuelta:
        print(f"  Búsqueda VUELTA: {dias_regreso_min}-{dias_regreso_max} días después")
    
    print(f"  Rebaja para alerta: {porcentaje_rebaja}%")
    print(f"  Precio mínimo: SE CALCULARÁ AUTOMÁTICAMENTE 🤖")
    print("=" * 70)
    
    # 6. Confirmar
    if not solicitar_si_no("¿Confirmar esta ruta?"):
        print("  ❌ Cancelado\n")
        return False
    
    # 7. Crear ruta
    try:
        print("\n  ⏳ Creando ruta...\n")
        
        ruta = crear_ruta(
            origen=origen,
            destino=destino,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            es_ida_vuelta=es_ida_vuelta,
            dias_regreso_min=dias_regreso_min,
            dias_regreso_max=dias_regreso_max,
            porcentaje_rebaja=porcentaje_rebaja,
            precio_min_automatico=True  # 🤖 Cálculo automático
        )
        
        logger.info(f"\n✅ Ruta creada exitosamente (ID: {ruta.id})")
        logger.info(f"   Monitoreo comenzará en la próxima búsqueda automática")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear ruta: {e}")
        return False


def listar_rutas():
    """Mostrar todas las rutas activas"""
    print("\n" + "=" * 70)
    print("📋 RUTAS ACTIVAS EN MONITOREO")
    print("=" * 70)
    
    rutas = obtener_rutas_activas()
    
    if not rutas:
        print("  (Sin rutas en monitoreo)")
        return
    
    for idx, ruta in enumerate(rutas, 1):
        print(f"\n  {idx}. {ruta.origen} → {ruta.destino}")
        print(f"     Período: {ruta.fecha_inicio.strftime('%d-%m-%Y')} → {ruta.fecha_fin.strftime('%d-%m-%Y')}")
        print(f"     Alerta: {ruta.porcentaje_rebaja_alerta}% rebaja (desde {ruta.precio_minimo_alerta}€)")
        
        if ruta.es_ida_vuelta:
            print(f"     Regreso: {ruta.dias_regreso_min}-{ruta.dias_regreso_max} días después")
        
        if ruta.ultima_busqueda:
            print(f"     Última búsqueda: {ruta.ultima_busqueda.strftime('%d-%m-%Y %H:%M')}")
        else:
            print(f"     Última búsqueda: (pendiente)")
    
    print("\n" + "=" * 70)


def ver_estadisticas_ruta(ruta_id: int = None):
    """Ver estadísticas de precios de una ruta"""
    if not ruta_id:
        ruta_id = int(input("  🔢 ID de la ruta: "))
    
    db = SessionLocal()
    try:
        ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
        
        if not ruta:
            print(f"  ❌ Ruta {ruta_id} no encontrada")
            return
        
        print(f"\n📊 ESTADÍSTICAS: {ruta.origen} → {ruta.destino}")
        print("=" * 70)
        
        stats = CalculadorAlertasInteligentes.obtener_estadisticas_ruta(ruta_id)
        
        if stats and stats['precios_encontrados'] > 0:
            print(f"  Precios registrados: {stats['precios_encontrados']}")
            print(f"  Media histórica: {stats['media']:.2f}€")
            print(f"  Precio mínimo encontrado: {stats['minimo']:.2f}€")
            print(f"  Precio máximo encontrado: {stats['maximo']:.2f}€")
            print(f"  Mediana: {stats['mediana']:.2f}€")
            print(f"  Variabilidad (desv. est.): {stats['desviacion_std']:.2f}€")
            print(f"\n  Precio mínimo de alerta configurado: {ruta.precio_minimo_alerta}€")
        else:
            print(f"  (Sin historial de precios aún)")
        
        print("=" * 70 + "\n")
    
    finally:
        db.close()


def eliminar_ruta():
    """Desactivar una ruta (no la elimina, solo la desactiva)"""
    rutas = obtener_rutas_activas()
    
    if not rutas:
        print("  ❌ No hay rutas activas para eliminar")
        return
    
    print("\n  Rutas activas:")
    for idx, ruta in enumerate(rutas, 1):
        print(f"  {idx}. {ruta.origen} → {ruta.destino} (ID: {ruta.id})")
    
    while True:
        try:
            ruta_id = int(input("\n  🔢 ID de la ruta a eliminar: "))
            
            db = SessionLocal()
            try:
                ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
                
                if not ruta:
                    print(f"  ❌ Ruta {ruta_id} no encontrada")
                    continue
                
                if not solicitar_si_no(f"¿Eliminar {ruta.origen} → {ruta.destino}?"):
                    print("  ❌ Cancelado")
                    return
                
                ruta.activo = False
                db.commit()
                
                logger.info(f"✅ Ruta {ruta_id} desactivada")
                return
            finally:
                db.close()
        
        except ValueError:
            print("  ❌ Introduce un número válido")


def menu_principal():
    """Menú principal del gestor de rutas"""
    while True:
        print("\n" + "=" * 70)
        print("🛫 FLIGHT TRACKER - Gestor de Rutas")
        print("=" * 70)
        print("  1. ➕ Agregar nueva ruta")
        print("  2. 📋 Listar rutas activas")
        print("  3. 📊 Ver estadísticas de ruta")
        print("  4. 🗑️  Eliminar ruta")
        print("  5. ❌ Salir")
        print("=" * 70)
        
        opcion = input("\n  Elige opción (1-5): ").strip()
        
        if opcion == "1":
            agregar_nueva_ruta()
        elif opcion == "2":
            listar_rutas()
        elif opcion == "3":
            ver_estadisticas_ruta()
        elif opcion == "4":
            eliminar_ruta()
        elif opcion == "5":
            print("\n  👋 Hasta luego!\n")
            break
        else:
            print("  ❌ Opción inválida")


def main():
    """Función principal"""
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n  👋 Interrupted\n")
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

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
