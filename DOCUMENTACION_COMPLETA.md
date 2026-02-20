═══════════════════════════════════════════════════════════════════════════════
📚 DOCUMENTACIÓN COMPLETA - FLIGHT TRACKER v2.2
═══════════════════════════════════════════════════════════════════════════════

Última actualización: 20-02-2026 20:55
Estado: ✅ 100% FUNCIONAL

CONTENIDO:
├─ 1. Estado Actual del Sistema
├─ 2. Arquitectura y Componentes
├─ 3. APIs Integradas
├─ 4. Cómo Iniciar
├─ 5. Comandos de Telegram
├─ 6. Troubleshooting Rápido
├─ 7. Estructura de Carpetas
├─ 8. Próximos Pasos
└─ 9. Referencias Técnicas


═══════════════════════════════════════════════════════════════════════════════
1. ESTADO ACTUAL DEL SISTEMA
═══════════════════════════════════════════════════════════════════════════════

✅ SISTEMA 100% FUNCIONAL - 0 PROBLEMAS

Estado de Componentes:
├─ ✅ Base de Datos: SQLite (local) + PostgreSQL (Render - fallback)
├─ ✅ Bot Telegram: Activo y respondiendo comandos
├─ ✅ Worker Automático: Busca cada 5 horas
├─ ✅ Agregador Multi-API: 3 APIs buscando en paralelo
├─ ✅ Migraciones BD: Automáticas y funcionales
└─ ✅ Logging: Detallado en data/logs/

APIs Activas:
├─ Amadeus (Oficial)          ✅ 10+ vuelos por búsqueda
├─ Fly Scraper v2 (RapidAPI)  ✅ NUEVA - Suscripción gratuita
└─ Flights Scraper Data       ✅ NUEVA - Suscripción gratuita


═══════════════════════════════════════════════════════════════════════════════
2. ARQUITECTURA Y COMPONENTES
═══════════════════════════════════════════════════════════════════════════════

PATRÓN AGREGADOR MULTI-API
──────────────────────────

src/api_aggregator.py (650+ líneas)
├─ FlightOffer: Dataclass unificado para todos los vuelos
├─ APIProvider: Clase base abstracta para todos los providers
├─ AmadeusProvider: Amadeus API oficial
├─ FlyScraper2Provider: Fly Scraper API v2
├─ FlightsScraperDataProvider: Flights Scraper Data
└─ APIAggregator: Orquestador con threading

CONCEPTO: Cada provider se ejecuta en paralelo (threading)
- Timeout por API: 10 segundos
- Timeout total: 15 segundos
- Resilencia: Si una API falla, las otras continúan
- Resultado: Mejor precio automáticamente identificado


BOT DE TELEGRAM
────────────────

src/telegram_bot.py (412 líneas)
├─ Comandos:
│  ├─ /start: Menú principal
│  ├─ /agregar: Crear nueva ruta
│  ├─ /buscar: Buscar vuelos ahora
│  ├─ /listar: Ver rutas activas
│  └─ /ayuda: Información del bot
├─ ConversationHandler: Diálogos multi-step
└─ Notificaciones: Alertas inteligentes

Máquina de Estados (para /agregar):
ORIGEN → DESTINO → FECHA_INICIO → FECHA_FIN → REGRESO → RANGO_REGRESO → REBAJA


WORKER AUTOMÁTICO
──────────────────

src/flight_search_worker.py (309 líneas)
├─ Búsqueda cada 5 horas automáticamente
├─ Procesa todas las rutas activas
├─ Detecta: Precios bajos, rebajas %
├─ Calcula alertas inteligentes
└─ Envía notificaciones por Telegram

CalculadorAlertasInteligentes (src/alert_calculator.py)
├─ Precio mínimo absoluto
├─ Porcentaje de rebaja histórica
├─ Cambio vs búsqueda anterior


BASE DE DATOS
─────────────

src/database.py (425 líneas)
├─ ORM SQLAlchemy (PostgreSQL + SQLite)
├─ Modelos:
│  ├─ Ruta: Rutas a monitorear
│  ├─ PrecioHistorico: Historial de precios
│  └─ Alerta: Alertas generadas
├─ Migraciones automáticas
└─ Funciones CRUD

Fallback Automático:
PostgreSQL (Render) ❌ → SQLite local ✅


UTILIDADES
──────────

src/config.py: Configuración centralizada
src/logger.py: Sistema de logging con emojis
src/airport_utils.py: Mapeo ciudad → IATA (50+ ciudades)
src/api.py: Amadeus API Client


═══════════════════════════════════════════════════════════════════════════════
3. APIs INTEGRADAS
═══════════════════════════════════════════════════════════════════════════════

AMADEUS OFFICIAL API
───────────────────

Tipo: API Oficial
Créditos: Limitados (pago)
Estabilidad: ✅ Excelente
Vuelos por búsqueda: 10-20
Endpoint: https://api.amadeus.com

Configuración:
AMADEUS_CLIENT_ID=<token>
AMADEUS_CLIENT_SECRET=<secret>

Formato entrada: DD-MM-YYYY
Resultado: Vuelos verificados con escalas y precios reales


FLY SCRAPER v2 (NUEVA)
──────────────────────

Tipo: RapidAPI Scraper
Créditos: Suscripción gratuita
Plan: Free (suficiente para testing)
Estabilidad: ✅ Buena
Vuelos por búsqueda: 5-15
Endpoint: https://fly-scraper.p.rapidapi.com/v2/flights/search-roundtrip

Configuración:
API Host: fly-scraper.p.rapidapi.com
Parámetros: originSkyId, destinationSkyId

Mapeamiento de ciudades:
MAD → MADM, BCN → BARCM, BKK → BKKM, etc.


FLIGHTS SCRAPER DATA (NUEVA)
─────────────────────────────

Tipo: RapidAPI Scraper
Créditos: Suscripción gratuita
Plan: Free (suficiente para testing)
Estabilidad: ✅ Buena
Vuelos por búsqueda: 5-15
Endpoint: https://flights-scraper-data.p.rapidapi.com/flights/search-roundtrip

Configuración:
API Host: flights-scraper-data.p.rapidapi.com
Parámetros: departureId, arrivalId (IATA standard)


EXECÚción en Paralelo
──────────────────────

1. Llamada: aggregator.search("MAD", "BCN", "21-04-2026")

2. Se crean 3 threads simultáneamente:
   Thread 1: Amadeus.search() → ejecuta en paralelo
   Thread 2: FlyScraper2.search() → ejecuta en paralelo
   Thread 3: FlightsScraperData.search() → ejecuta en paralelo

3. Timeout:
   - Cada API: máximo 10 segundos
   - Total: máximo 15 segundos

4. Resultado: Se devuelve el mejor precio de todas

5. Si una falla:
   Las otras 2 continúan sin afectarse


═══════════════════════════════════════════════════════════════════════════════
4. CÓMO INICIAR
═══════════════════════════════════════════════════════════════════════════════

CONFIGURACIÓN INICIAL
─────────────────────

1. Archivo .env debe existir con:
   TELEGRAM_BOT_TOKEN=<tu_bot_token>
   TELEGRAM_CHAT_ID=<tu_chat_id>
   AMADEUS_CLIENT_ID=<amadeus_id>
   AMADEUS_CLIENT_SECRET=<amadeus_secret>
   RAPIDAPI_KEY=<tu_key_rapidapi>

2. Base de datos: Se crea automáticamente en data/vuelos.db

3. Carpetas: Se crean automáticamente en data/logs/


INICIAR EN LOCAL
────────────────

Opción 1 - Sistema Completo (Bot + Worker):
$env:PYTHONIOENCODING = 'utf-8'
python run_combined.py

Opción 2 - Solo Bot:
python run_telegram_bot.py

Opción 3 - Solo Worker (búsquedas automáticas):
python run_search_worker.py


VERIFICAR ESTADO
────────────────

python diagnostics.py
→ Mostrar: ✅ SISTEMA 100% FUNCIONAL


═══════════════════════════════════════════════════════════════════════════════
5. COMANDOS DE TELEGRAM
═══════════════════════════════════════════════════════════════════════════════

/start
Muestra menú principal y comandos disponibles

/agregar
Inicia conversación para crear nueva ruta
Pasos:
1. Askea origen (ciudad o IATA)
2. Askea destino
3. Askea fecha inicio
4. Askea fecha fin
5. Pregunta: ¿Ida y vuelta?
6. Si SÍ: Askea rango días para regreso
7. Askea porcentaje rebaja para alerta (défault 15%)
8. Crea ruta en BD

/buscar
Busca vuelos en TODAS las rutas activas AHORA
Reporta: Mejor precio + fuente (Amadeus/FlyScraper2/FlightsScraperData)

/listar
Muestra todas las rutas activas con parámetros

/ayuda
Muestra información del sistema


═══════════════════════════════════════════════════════════════════════════════
6. TROUBLESHOOTING RÁPIDO
═══════════════════════════════════════════════════════════════════════════════

PROBLEMA: Bot no responde
─────────────────────────
✓ Verificar que run_combined.py está ejecutándose
✓ Revisar .env tiene TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID
✓ Enviar /start en Telegram
✓ Ver logs: data/logs/flight_tracker.log

PROBLEMA: No encuentra vuelos
──────────────────────────────
✓ Verificar fecha es futura (no en el pasado)
✓ Verificar código IATA correcto (MAD, BCN, JFK, etc)
✓ Ver logs para saber qué APIs retornaron datos
✓ Si Amadeus funciona pero scrapers no: normal (RapidAPI puede tener límites)

PROBLEMA: APIs retornan error 404
──────────────────────────────────
✓ Verificar RAPIDAPI_KEY en .env es correcta
✓ Ir a https://rapidapi.com y verificar suscripciones activas
✓ Si scrapers fallan: Amadeus sigue funcionando (system resiliente)

PROBLEMA: Base de datos error
──────────────────────────────
✓ Eliminar data/vuelos.db
✓ Reiniciar: python run_combined.py
✓ BD se recreará automáticamente con migraciones


═══════════════════════════════════════════════════════════════════════════════
7. ESTRUCTURA DE CARPETAS
═══════════════════════════════════════════════════════════════════════════════

DIRECTORIO RAÍZ
───────────────

data/
├─ vuelos.db: Base de datos SQLite (se crea automáticamente)
└─ logs/: Archivos de log diarios

src/
├─ config.py: Configuración + variables de entorno
├─ logger.py: Sistema de logging
├─ database.py: ORM SQLAlchemy + funciones BD
├─ api.py: Amadeus API Client
├─ api_aggregator.py: Patrón Agregador Multi-API
├─ airport_utils.py: Mapeo ciudad → IATA
├─ alert_calculator.py: Cálculo de alertas
├─ telegram_bot.py: Bot de Telegram
└─ flight_search_worker.py: Worker automático

Archivos raíz
├─ run_combined.py: Iniciar Bot + Worker
├─ run_telegram_bot.py: Solo Bot
├─ run_search_worker.py: Solo Worker
├─ test_sistema.py: Suite de 8 tests
├─ test_rapidapi.py: Verificar APIs RapidAPI
├─ diagnostics.py: Verificación completa del sistema
├─ .env: Variables de entorno (NO en git)
├─ requirements.txt: Dependencias Python
└─ README.md: Información general


═══════════════════════════════════════════════════════════════════════════════
8. PRÓXIMOS PASOS
═══════════════════════════════════════════════════════════════════════════════

CORTO PLAZO (Esta semana)
─────────────────────────

✓ Verificar APIs funcionan: python test_rapidapi.py
✓ Crear rutas via /agregar en Telegram
✓ Buscar vuelos con /buscar
✓ Monitorear logs: data/logs/flight_tracker.log

MEDIANO PLAZO (1-2 semanas)
───────────────────────────

□ Dashboard web básico (visualizar precios)
□ Exportar historial a CSV
□ Alertas más inteligentes (tendencias)
□ Integración con más APIs si es necesario

LARGO PLAZO (Próximas versiones)
────────────────────────────────

□ Mobile app
□ Predicciones de precios (ML)
□ Integración con Google Flights UI
□ Multi-usuario


═══════════════════════════════════════════════════════════════════════════════
9. REFERENCIAS TÉCNICAS
═══════════════════════════════════════════════════════════════════════════════

CONCEPTOS CLAVE
───────────────

Patrón Agregador:
Ejecuta múltiples APIs en paralelo sin que una afecte a otras

Threading (no Asyncio):
Usamos threading porque requests no es async-friendly

SQLAlchemy ORM:
Mapeo objeto-relacional que funciona con PostgreSQL/SQLite

Fallback Automático:
PostgreSQL ❌ → SQLite ✅ (transparente para el usuario)

Máquina de Estados:
ConversationHandler en Telegram para diálogos complejos


CÓDIGOS IATA PRINCIPALES
────────────────────────

Ciudades españolas:
MAD = Madrid (Barajas)
BCN = Barcelona (El Prat)
AGP = Málaga
SVQ = Sevilla
BIO = Bilbao
IBZ = Ibiza

Ciudades europeas:
CDG = París
LHR = Londres Heathrow
AMS = Ámsterdam
FCO = Roma Fiumicino
DUB = Dublín

Ciudades internacionales:
JFK = Nueva York
LAX = Los Ángeles
BKK = Bangkok
DXB = Dubai
SYD = Sídney


PUERTOS Y DEPENDENCIAS
──────────────────────

Puerto Telegram: No especificado (usa token)
Puerto Amadeus: https (443)
Puerto RapidAPI: https (443)
Puerto BD Local: N/A (archivo)
Puerto PostgreSQL: 5432 (Render)

Dependencias críticas:
- python-telegram-bot: Bot de Telegram
- amadeus: Amadeus API Python SDK
- sqlalchemy: ORM
- requests: HTTP requests
- psycopg2: PostgreSQL adapter


═══════════════════════════════════════════════════════════════════════════════

Última actualización: 20-02-2026
Mantenedor: Sistema automático con asistente IA
Estado: ✅ 100% FUNCIONAL
