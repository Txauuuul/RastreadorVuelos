# 🛫 Flight Tracker - Rastreador de Vuelos

Un **rastreador automático de vuelos** que monitorea precios en Amadeus y **envía alertas por Telegram** cuando encuentra gangas.

> 📬 **¿POR DÓNDE EMPIEZO?**  
> Si es tu primera vez aquí, ve a [HOJA_DE_RUTA.md](HOJA_DE_RUTA.md) para guías personalizadas según tu situación.

## ✨ Características

✅ **Búsqueda automática cada 2 horas** en Amadeus API  
✅ **Alertas inteligentes** cuando el precio baja del umbral  
✅ **Análisis de historial** de 30 días para detectar "gangas reales"  
✅ **Notificaciones por Telegram** instantáneas  
✅ **Reporte diario** a las 09:00  
✅ **Base de datos SQLite** con historial de precios  
✅ **Logs detallados** para debugging  
✅ **Compatible con nube** (Railway, Render, GCP)  

---

## 🚀 INICIO RÁPIDO (Local)

### 1. Clonar / Descargar

```bash
cd Rastreador
```

### 2. Crear entorno virtual

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # macOS/Linux
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar plantilla
copy .env.example .env

# Editar con tus credenciales
notepad .env
```

Necesitas obtener:
- **Amadeus:** https://developers.amadeus.com
- **Telegram Bot:** @BotFather en Telegram

### 5. Probar que funciona

```bash
# Probar módulo API
python -m src.api

# Probar BD
python -m src.database

# Probar notificaciones
python -m src.notifications

# Ejecutar un check único
python main.py --mode test
```

### 6. Agregar vuelos a monitorear

```bash
python manage_flights.py
```

**Opción interactiva:**
```
1. Ver vuelos monitoreados
2. Agregar nuevo vuelo
3. Modificar parámetros
4. Eliminar vuelo
...
```

### 7. Ejecutar el tracker

```bash
# Modo desarrollo (1 check y termina)
set DEBUG=True
python main.py

# Modo producci​ón (24/7)
set DEBUG=False
python main.py
```

**Output esperado:**
```
[INFO] 🚀 FLIGHT TRACKER INICIADO
[INFO] 🔄 CHECK #1
[INFO] ✅ 1 vuelo(s) a revisar
[INFO] 🔍 Buscando: MAD → CDG (25-02-2025)
[INFO] ✅ MAD→CDG: 89.50€ (IB)
[INFO] 🚨 No hay alertas en este momento
[INFO] ✅ Check completado exitosamente
```

---

## 📱 GESTIONAR VUELOS

```bash
python manage_flights.py
```

### Opciones:
1. **Ver vuelos monitoreados** → Lista todos
2. **Agregar nuevo vuelo** → Ruta + fecha + precios
3. **Modificar parámetros** → Cambiar umbrales
4. **Eliminar vuelo** → Dejar de monitorear
5. **Ver historial de precios** → Últimos 30 días
6. **Ver estadísticas** → Resumen global

---

## 🌐 DESPLEGAR EN LA NUBE

### 🥇 Opción recomendada: Render (100% GRATUITO)

Ver documento completo: [PLATAFORMAS_GRATUITAS.md](PLATAFORMAS_GRATUITAS.md)

**Guía paso a paso:** [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md) ⭐

**Ventajas:**
- ✅ Completamente gratuito
- ✅ Excelente documentación
- ✅ Deploy automático desde GitHub
- ✅ Se reactiva automáticamente cada 2 horas
- ✅ Variables de entorno muy fáciles

**Pasos rápidos:**
1. Código en GitHub ✅
2. Crear cuenta en https://render.com
3. "New Web Service" → seleccionar tu repo
4. Agregar variables de entorno
5. ¡Listo! Bot 24/7 gratuito

### Más opciones

Ver [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) para comparativa Railway, Google Cloud, etc.

---

## 📊 CÓMO FUNCIONA

### Flujo de ejecución:

```
SCHEDULER (cada 2 horas)
  │
  ├─→ API: Buscar vuelos en Amadeus
  │    └─→ BD: Guardar precios
  │
  ├─→ ALERTS: Detectar oportunidades
  │    ├─ Precio < umbral mínimo?
  │    └─ Precio 15% menos que promedio?
  │
  └─→ NOTIFICATIONS: Enviar por Telegram
       └─→ BD: Registrar que se envió
```

### Jobs automáticos:

| Job | Frecuencia | Función |
|-----|-----------|---------|
| 🔍 Check+Alert | Cada 2 horas | Busca y notifica |
| 📊 Reporte | 09:00 diariamente | Resumen del día |
| 🧹 Limpieza | Cada 30 días | Elimina datos >30d |
| 📈 Estadísticas | Cada 1 hora | Log de stats |

---

## 💬 COMANDOS DE TELEGRAM

Una vez desplegado en la nube, **gestiona TODO desde Telegram sin tocar el código:**

### Comandos disponibles:

```
/start          → Ver lista de comandos disponibles
/lista          → Ver todos los vuelos monitoreados (con IDs)
/agregar        → Añadir nuevo vuelo (5 pasos: origen→destino→fecha→precio→reducción%)
/modificar      → Cambiar precio mínimo o % de reducción
/eliminar       → Dejar de monitorear un vuelo
/historial      → Ver últimos 5 precios de un vuelo
/estadisticas   → Ver estadísticas globales
```

### Ejemplo de uso interactivo:

```
You: /agregar
Bot: ¿Código IATA origen? (ej: MAD, BCN, BIO)
You: MAD
Bot: ✅ Origen: MAD
     ¿Destino?
You: NYC
Bot: ✅ Destino: NYC
     ¿Fecha salida? (DD-MM-YYYY)
You: 25-12-2024
Bot: ✅ Fecha: 25-12-2024
     ¿Precio mínimo (EUR)? (ej: 300)
You: 300
Bot: ✅ Mínimo: 300 EUR
     ¿Reducción mínima (%)? (ej: 15)
You: 15
Bot: ✨ Vuelo creado:
    🛫 MAD → NYC
    📅 25-12-2024
    💰 Mínimo: 300€ o -15% histórico
```

### Alertas automáticas:

El bot envía **automáticamente**:

1. **Alertas de precios** cuando detecta:
   - Precio por debajo del mínimo establecido
   - Precio 15% menos que el promedio histórico

2. **Resumen diario** a las 09:00 AM
   - Vuelos monitoreados
   - Alertas enviadas
   - Precio promedio

---

## 📋 ESTRUCTURA DEL PROYECTO

```
Rastreador/
├── main.py                    # Punto de entrada
├── manage_flights.py          # Gestor interactivo de vuelos (LOCAL)
├── requirements.txt           # Dependencias Python
│
├── src/
│   ├── __init__.py
│   ├── config.py              # Variables de entorno
│   ├── logger.py              # Sistema de logs
│   ├── api.py                 # Conexión con Amadeus
│   ├── database.py            # BD SQLite
│   ├── alerts.py              # Detección de alertas
│   ├── notifications.py       # Envío Telegram
│   ├── scheduler.py           # Orquestador principal
│   └── telegram_commands.py   # Comandos del bot Telegram
│
├── data/
│   └── vuelos.db              # Base de datos (gitignore)
│
├── logs/
│   └── rastreador.log         # Log de ejecución (gitignore)
│
├── .env                       # Variables secretas (gitignore)
├── .env.example               # Plantilla (SÍ subir)
├── .gitignore                 # Archivos a ignorar en Git
├── Dockerfile                 # Para despliegue en nube
├── Procfile                   # Para despliegue en nube
│
├── README.md                  # Este archivo
├── TELEGRAM_COMMANDS.md       # Guía de comandos del bot ⭐
├── CLOUD_DEPLOYMENT.md        # Guía de despliegue en nube
├── PLATAFORMAS_GRATUITAS.md   # Análisis de hosting gratuito
└── requirements.txt           # Dependencias
```

**Documentos principales:**
- 📖 **README.md** - Inicio rápido y arquitectura
- 💬 **TELEGRAM_COMMANDS.md** - Guía completa de comandos (LEE ESTO)
- 🚀 **PRIMER_DESPLIEGUE.md** - Guía paso a paso para Render (COMIENZA AQUÍ)
- ☁️ **PLATAFORMAS_GRATUITAS.md** - Análisis de hosting gratuito
- 🚀 **CLOUD_DEPLOYMENT.md** - Instrucciones detalladas de despliegue

---

## 🔧 DEPENDENCIAS

Todas incluidas en `requirements.txt`:

```
requests              # HTTP calls
amadeus              # API de Amadeus
python-dotenv        # Variables de entorno
python-dateutil      # Manejo de fechas
schedule             # Scheduler de tareas
python-telegram-bot  # Bot de Telegram
numpy                # Análisis numérico
pandas               # Data frames
```

---

## 🐛 TROUBLESHOOTING

### El bot no busca vuelos
- ✅ Verifica que `DEBUG=False` (en `.env` o Railway)
- ✅ Verifica que al menos 1 vuelo está monitoreado (`python manage_flights.py`)
- ✅ Revisa logs por errores

### No recibo alertas
- ✅ Verifica que Telegram token es correcto
- ✅ Verifica que el chat ID es un número
- ✅ Ejecuta `python -m src.notifications` para probar envío

### Error: Event loop is closed
- ✅ Este error fue SOLUCIONADO en `notifications.py`
- ✅ Si aparece de nuevo, actualiza el código

### La BD está corrupta
```bash
# Eliminar BD y recrearla
del data/vuelos.db
python -m src.database
```

### Logs vacíos en nube
- ✅ Railway: Dashboard → Logs
- ✅ Render: Dashboard → Logs
- ✅ Verifica variables de entorno

---

## 📞 RECURSOS

- **Amadeus Docs:** https://developers.amadeus.com/
- **Telegram Bot API:** https://core.telegram.org/bots
- **Python-Telegram-Bot:** https://python-telegram-bot.readthedocs.io
- **Railway Docs:** https://docs.railway.app
- **Schedule Library:** https://schedule.readthedocs.io

---

## 📈 MEJORAS FUTURAS

- 🔮 Comparar precios entre múltiples aeropuertos
- 🔮 Predicción de precios con ML
- 🔮 Soporte para vuelos de ida y vuelta
- 🔮 Filtros por aerolíneas
- 🔮 Búsqueda de hoteles + vuelos
- 🔮 Dashboard web
- 🔮 API REST propia

---

## 📄 LICENSE

Este proyecto es de código abierto. Úsalo libremente.

---

## 🙏 CONTRIBUCIONES

¿Encontraste un bug? ¿Tienes idea para mejorar?  
Abre un issue o pull request.

---

**¡Feliz ahorro de dinero en vuelos! ✈️💰**

Para desplegar en nube, ve a [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)
