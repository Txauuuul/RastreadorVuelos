"""
ARQUITECTURA DEL FLIGHT TRACKER
=================================

ÍNDICE DE MÓDULOS:
1. config.py - Configuración centralizada
2. logger.py - Sistema de logging
3. database.py - ORM con SQLAlchemy
4. api.py - Integración Amadeus
5. airport_utils.py - Traducción ciudad→IATA
6. alert_calculator.py - Cálculo inteligente de alertas
7. manage_flights.py - CLI para gestionar rutas
8. telegram_bot.py [NUEVO] - Bot de Telegram
9. flight_search_worker.py [NUEVO] - Motor de búsqueda automática
10. scheduler.py - Orquestador de tareas


FLUJO COMPLETO DEL SISTEMA:
============================

1. USUARIO AGREGA RUTA (vía Telegram /agregar o CLI)
   ↓
   @telegram_bot.add_flight()
   → Conversación multi-paso (origen, destino, fechas, rebaja)
   → database.crear_ruta()
   → Se guarda en tabla "rutas" con precio_minimo_alerta automático
   
2. CADA 5 HORAS - BÚSQUEDA AUTOMÁTICA
   ↓
   run_search_worker.py
   → flight_search_worker.SearchWorker.ejecutar_ciclo_busqueda()
   → Para cada ruta activa:
      → api.AmadeusAPI.search_flights_date_range()
      → Busca TODOS los vuelos en el rango
      → Retorna lista de vuelos con precios
      → database.guardar_precio() - Guarda cada precio
   → alert_calculator.precio_es_buena_oferta()
      → Compara precio actual vs histórico
      → Verifica si cumple % rebaja
   → Si hay ofertas → telegram_bot envia alertas
   
3. USUARIO BUSCA MANUALMENTE
   ↓
   /buscar en Telegram
   → telegram_bot.buscar_ahora()
   → Busca en todas las rutas AHORA
   → Muestra resultados inmediatos


FLUJO DE DETECCIÓN DE OFERTAS:
==============================

Precio Mínimo (automático):
  precioMinimo = promedio_últimos_60días × (1 - porcentajeRebaja/100)
  
Ejemplo:
  - Promedio histórico: 100€
  - Porcentaje rebaja: 20%
  - Precio mínimo alerta: 100 × (1 - 0.20) = 80€

Detección:
  SI precio_actual ≤ precio_mínimo_alerta:
    → ES OFERTA
    → Enviar alerta a Telegram
    → Guardar en tabla "alertas"


MODELOS DE BASE DE DATOS:
==========================

1. RUTAS (rutas monitoreadas)
   - id (PK)
   - origen (IATA): "MAD"
   - destino (IATA): "BCN"
   - fecha_inicio: 2026-03-01
   - fecha_fin: 2026-06-30
   - es_ida_vuelta: True/False
   - dias_regreso_min: 7
   - dias_regreso_max: 14
   - porcentaje_rebaja_alerta: 20
   - precio_minimo_alerta: 80.0 (calculado automáticamente)
   - activa: True
   - creada_en: DateTime

2. PRECIOS_HISTORICOS (cada búsqueda guarda precios)
   - id (PK)
   - ruta_id (FK → rutas)
   - origen: "MAD"
   - destino: "BCN"
   - fecha_vuelo: 2026-04-15
   - precio: 75.5
   - aerolinea: "Iberia"
   - escalas: 0
   - duracion: 120 (minutos)
   - fuente: "amadeus"
   - fecha_registro: DateTime (cuando se guardó)

3. ALERTAS (cuando se detecta una oferta)
   - id (PK)
   - ruta_id (FK → rutas)
   - precio_detectado: 75.5
   - precio_umbral: 80.0
   - tipo_alerta: "rebaja_porcentaje" / "precio_minimo"
   - enviada_telegram: True/False
   - fecha: DateTime


COMO ENCAJAN LOS MÓDULOS:
==========================

telegram_bot.py
├─ Recibe: Comandos del usuario (/agregar, /buscar, /listar)
├─ Llama: database.crear_ruta(), guardar_precio()
├─ Llama: api.AmadeusAPI.search_flights_date_range()
└─ Envía: Mensajes a TELEGRAM_CHAT_ID

flight_search_worker.py
├─ Ejecuta: Cada 5 horas (loop asyncio)
├─ Llama: api.AmadeusAPI.search_flights_date_range()
├─ Llama: database.guardar_precio()
├─ Llama: alert_calculator.precio_es_buena_oferta()
└─ Envía: Alertas a Telegram

api.py
├─ Métodos:
│  ├─ search_flights() - Busca UN día
│  ├─ search_flights_date_range() - Busca TODO el rango (muestreo cada 3 días)
│  └─ _parse_flight_offers() - Procesa JSON de Amadeus
└─ Auth: OAuth2 con AMADEUS_CLIENT_ID/SECRET

alert_calculator.py
├─ Funciones:
│  ├─ calcular_precio_minimo_automatico()
│  ├─ obtener_estadisticas_ruta()
│  └─ precio_es_buena_oferta()
└─ Usa: database.guardar_precio() para leer histórico

manage_flights.py
├─ CLI interactivo (si ejecutas desde terminal)
└─ Usa: database.crear_ruta(), alert_calculator, airport_utils


INSTALACIÓN Y EJECUCIÓN:
========================

1. INSTALAR DEPENDENCIAS:
   pip install -r requirements.txt

2. CONFIGURAR .env:
   AMADEUS_CLIENT_ID=tu_id
   AMADEUS_CLIENT_SECRET=tu_secret
   TELEGRAM_BOT_TOKEN=tu_token
   TELEGRAM_CHAT_ID=tu_chat_id
   DATABASE_URL=postgresql://user:pass@host:5432/db

3. EJECUTAR BOT DE TELEGRAM (en terminal 1):
   python run_telegram_bot.py
   
   Esto inicia un listener que espera comandos de Telegram
   └─ Uso: /agregar, /listar, /buscar, /ayuda

4. EJECUTAR BUSCADOR AUTOMÁTICO (en terminal 2):
   python run_search_worker.py
   
   Esto busca cada 5 horas automáticamente
   └─ Busca → Guarda → Detecta ofertas → Alerta Telegram

5. [OPCIONAL] CLI INTERACTIVO (en terminal 3):
   python manage_flights.py
   
   Menú para agregar rutas sin Telegram


PREGUNTAS FRECUENTES:
====================

P: ¿Cómo se previene que Render se duerma?
R: UptimeRobot pide un endpoint cada 5 minutos
   Necesitas crear un endpoint Flask/FastAPI que responda:
   app.route('/ping', methods=['GET'])
   return 'OK'

P: ¿Cómo funcionan las búsquedas en rango?
R: No se busca CADA DÍA (sería lento).
   Se busca cada 3 días: 01, 04, 07, 10... hasta la fecha fin
   Así cubre el rango sin saturar el API

P: ¿Qué pasa si Amadeus rechaza una búsqueda?
R: flight_search_worker captura la excepción y:
   - La registra en logs
   - Continúa con la siguiente ruta
   - No deja de ejecutarse

P: ¿Cómo agrego una ruta?
R: Desde Telegram: /agregar
   O desde CLI: python manage_flights.py → Opción 1

P: ¿Cómo recibo alertas?
R: Si el sistema está corriendo detectará ofertas
   Y las enviará al TELEGRAM_CHAT_ID cada 5 horas


ARCHIVOS CREADOS EN ESTA SESIÓN:
================================

✅ src/telegram_bot.py (300+ líneas)
   - FlightTrackerBot class
   - Conversation handler para /agregar
   - Métodos: start, add_flight, listar_rutas, buscar_ahora

✅ src/flight_search_worker.py (250+ líneas)
   - SearchWorker class
   - Loop automático cada 5 horas
   - Detección de ofertas
   - Envío de alertas

✅ run_telegram_bot.py
   - Script para ejecutar el bot

✅ run_search_worker.py
   - Script para ejecutar el worker

✅ ARQUITECTURA.txt (este archivo)
   - Explicación de cómo funciona todo


COMO FUNCIONAN LOS LOOPS ASYNCIOS:
==================================

CONCEPTO CLAVE: async/await

Sin async (bloqueante):
  print("Buscando...")
  respuesta = requests.get(url)  # SE ESPERA aquí
  print("Encontré!")

Con async (no bloqueante):
  print("Buscando...")
  respuesta = await api.search()  # No bloquea, puede hacer otra cosa
  print("Encontré!")

Esto permite que while True no saturé CPU:

while True:
    await worker.buscar()        # Toma 30-60 segundos
    await asyncio.sleep(18000)   # Espera 5 horas sin usar CPU
    

PRÓXIMAS FUNCIONALIDADES OPCIONALES:
===================================

1. Endpoint Flask para /ping (prevenir Render sleep)
2. Dashboard web para ver estadísticas de búsquedas
3. Exportar resultados a CSV/Excel
4. Notificaciones por email además de Telegram
5. Comparar precios entre múltiples agencias
6. Historial detallado en BD
7. Gráficos de precios vs tiempo
"""

if __name__ == "__main__":
    print(__doc__)
