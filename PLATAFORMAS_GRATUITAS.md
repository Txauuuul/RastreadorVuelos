# 🆓 PLATAFORMAS GRATUITAS PARA DESPLEGAR PYTHON

## 📊 COMPARATIVA GRATUITA (2025)

| Plataforma | Precio | Uptime 24/7 | Facilidad | Python | Recomendación |
|-----------|--------|-----------|-----------|--------|----------------|
| **Render** | ✅ GRATIS | ⚠️ Se duerme* | ⭐⭐⭐⭐⭐ | ✅ Excelente | 🥇 **MEJOR** |
| Google Cloud Run | Gratuito (300 min/mes) | ✅ Sí | ⭐⭐⭐ | ✅ Excelente | 🥈 Bueno |
| Fly.io | Gratuito ($3 crédito) | ✅ Sí | ⭐⭐⭐⭐ | ✅ Excelente | 🥉 Alternativa |
| PythonAnywhere | Gratuito (limitado) | ⚠️ Limitado | ⭐⭐⭐ | ✅ Excelente | ⚠️ No ideal |
| Replit | ✅ GRATIS | ⚠️ Se duerme | ⭐⭐⭐⭐ | ✅ Excelente | ⚠️ Para hobby |
| Railway | $5/mes mín | ✅ Sí | ⭐⭐⭐⭐⭐ | ✅ Excelente | 💰 De pago |
| Heroku | ❌ YA NO GRATUITO | ❌ | - | ✅ | ❌ |

**\* "Se duerme" = El servicio se pausa después de 15 min inactividad. Pero se reactiva al siguiente acceso (sin problema para un scheduler que se ejecuta cada 2 horas)

---

## 🥇 OPCIÓN RECOMENDADA: RENDER (100% GRATUITO)

### ¿Por qué Render es perfecto para tu caso?

1. **100% GRATUITO** indefinidamente
2. **Excelente documentación**
3. **Conecta directo con GitHub**
4. **Se reactiva automáticamente** cuando hay ejecución
5. **Variables de entorno muy fáciles**
6. **No requiere tarjeta de crédito**

### La "limitación" en realidad es una ventaja:

Tu bot se ejecuta así:
```
00:00 - Búsqueda #1 (13 segundos)
02:00 - Búsqueda #2 (13 segundos)  
04:00 - Búsqueda #3 (13 segundos)
...
```

Después de 15 min inactividad, Render lo pausa. Pero **cuando llega la siguiente búsqueda (2 horas después), se reactiva automáticamente**.

**CONCLUSIÓN:** Para tu caso, esto es **perfecto gratuito 100%** 🎉

---

## 🚀 PASOS PARA DESPLEGAR EN RENDER (GRATUITO)

### **Paso 1: Subir código a GitHub** (ya hecho ✅)

```bash
# Ya lo hiciste, pero recordatorio:
git add .
git commit -m "Flight Tracker ready for Render"
git push origin main
```

### **Paso 2: Registrarse en Render**

1. Ve a https://render.com
2. Haz clic en **"Sign up"**
3. Autentica con GitHub
4. Autoriza a Render acceder a tus repos

### **Paso 3: Crear nuevo servicio**

1. Dashboard → **"New Web Service"**
2. Conecta tu repo `RastreadorVuelos`
3. Render detectará automáticamente que es Python

### **Paso 4: Configurar el servicio**

```
Name: flight-tracker
Region: Frankfurt (Europe) [más cercano]
Build Command: pip install -r requirements.txt
Start Command: python main.py
Plan: Free
```

### **Paso 5: Variables de entorno**

Haz clic en **"Environment"** y agrega:

```
AMADEUS_CLIENT_ID=tu_id
AMADEUS_CLIENT_SECRET=tu_secret
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
DEBUG=False
```

### **Paso 6: Deploy**

Haz clic en **"Create Web Service"**

Render empezará a:
1. Clonar tu repo
2. Instalar dependencias
3. **Ejecutar `python main.py`**

**Espera 2-3 minutos...** ✅

Deberías ver en los logs:
```
[INFO] ✅ Flight Tracker Scheduler inicializado
[INFO] 🚀 FLIGHT TRACKER INICIADO
[INFO] 🔄 CHECK #1
[INFO] ✅ Check completado exitosamente
```

---

## 📱 COMANDOS DE TELEGRAM (NOVEDAD)

Una vez desplegado, **NO necesitas `manage_flights.py` localmente**.

Ahora puedes gestionar TODO desde Telegram:

### **Comandos disponibles:**

```
/start          - Ver guía de bienvenida
/lista          - Ver vuelos monitoreados
/agregar        - Agregar nuevo vuelo ➕
/modificar      - Cambiar parámetros ✏️
/eliminar       - Dejar de monitorear 🗑️
/historial      - Ver precios históricos 📊
/estadisticas   - Ver resumen global 📈
```

### **Ejemplo de uso:**

```
TÚ: /agregar
BOT: ¿Código IATA origen?
TÚ: MAD
BOT: ¿Código IATA destino?
TÚ: CDG
BOT: ¿Fecha (DD-MM-YYYY)?
TÚ: 25-02-2025
BOT: ¿Precio mínimo (€)?
TÚ: 50
BOT: ¿Reducción respecto media (%)?
TÚ: 15
BOT: ✅ Vuelo agregado correctamente
```

**¡Así de simple!** **SIN NECESIDAD DE CÓDIGO NI TERMINAL**

---

## 🔄 CÓMO FUNCIONA EN RENDER

### **Timeline de ejecución:**

```
T=0min   → Render inicia tu app
T=0min   → El scheduler corre el primer check
T=1min   → Si no hay actividad, Render pausa el servicio
T=120min → Próxima búsqueda (2 horas después)
T=120min → Render reactiva automáticamente
T=120min → El scheduler corre el segundo check
T=121min → Vuelve a pausar
...
```

**Tu bot está "durmiendo" pero se reactiva automáticamente cuando lo necesita** 🤖

---

## 🆚 RENDER vs RAILWAY

| Aspecto | Render Free | Railway $5 |
|--------|------------|-----------|
| **Costo** | ✅ $0/mes | 💰 $5/mes |
| **Uptime 24/7** | ⚠️ Se pausa* | ✅ Sí |
| **Para tu caso** | ✅ Perfecto | Overkill |
| **Facilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Recomendación** | 🥇 USAR ESTO | Próximo nivel |

\* Pero se reactiva automáticamente, perfecto para scheduler cada 2 horas

---

## 🎯 FLUJO COMPLETO RECOMENDADO

### **Fase 1: Desarrollo Local** (YA HECHO)
```bash
python manage_flights.py         # Agregar vuelos
python main.py --mode test       # Probar
```

### **Fase 2: Desplegar en Render** (AHORA)
1. GitHub repo actualizado ✅
2. Render account created
3. Setup en Render (5 minutos)
4. **¡Listo! Bot 24/7**

### **Fase 3: Gestionar desde Telegram** (NUEVO)
```
Abre Telegram
/agregar
Sigue el flujo
✅ Nuevo vuelo monitoreado
```

**Nunca más necesitas tocar terminal** 🎉

---

## ⚠️ COSAS A TENER EN CUENTA

### ✅ Lo que SÍ funciona en Render

- ✅ Búsquedas cada 2 horas
- ✅ Alertas por Telegram
- ✅ BD SQLite local
- ✅ Logs en la consola de Render
- ✅ Comandos de Telegram

### ⚠️ La "limitación" que no es limitación

- 🔄 Se pausa después de 15 min inactividad
- 🔄 Se reactiva al siguiente check (2 horas después)
- 🔄 **PERFECTO para tu caso**

### ❌ Lo que NO funciona bien

- ❌ Cambios persistentes en archivos locales
  - Como `data/vuelos.db` se "resetea" cada reinicio
  - **SOLUCIÓN:** Render + PostgreSQL (pero eso es pago)
  - **MEJOR SOLUCIÓN:** Usar comandos Telegram (ya está) 

---

## 🔧 MIGRAR DE RAILWAY A RENDER

Si ya fuiste a Railway:

```bash
# En Render, agregar mismo archivo Procfile:
worker: python main.py

# O en Dockerfile (mismo que en Railway):
FROM python:3.11-slim
...
CMD ["python", "main.py"]

# Las variables de entorno van igual
```

**Es prácticamente el mismo deploy, solo más barato** 🎉

---

## 📞 TROUBLESHOOTING EN RENDER

### **"No encuentro mis vuelos"**
- Los vuelos se guardan en `data/vuelos.db` en memoria
- Usa `/lista` en Telegram para ver
- Usa `/agregar` para añadir nuevos

### **Se ejecuta pero no envía alertas**
- Verifica logs en Render dashboard
- Verifica que `DEBUG=False`
- Verifica credenciales Telegram

### **El servicio se pausó y no se reactiva**
- Es normal en Render gratuito
- Se reactiva automáticamente en el siguiente job
- Si quieres 24/7 real, sube a Render pro ($7/mes) o Railway ($5/mes)

### **Quiero actualizar el código**
```bash
git push origin main
# Render se redeploy automáticamente
```

---

## 💡 PRO TIPS

### **1. Monitorear logs en Render:**
```
Dashboard → Services → flight-tracker → Logs
```

### **2. Recibir alertas si algo falla:**
Render puede enviar emails, pero Telegram es mejor:
- Usa `/estadisticas` cada día
- Si no ves cambios, algo no funciona

### **3. Actualizar vuelos sin redeploy:**
```
/eliminar (ID del vuelo viejo)
/agregar (nuevo vuelo)
¡Listo! Sin necesidad de tocar GitHub
```

### **4. Copia de seguridad de datos:**
```bash
# Descargar BD de Render (si es posible)
# O exportar vuelos via Telegram commands
```

---

## ✅ CHECKLIST ANTES DE RENDER

- [ ] GitHub repo con código actualizado
- [ ] `.env` en `.gitignore` (no subido)
- [ ] `Procfile` o `Dockerfile` en raíz
- [ ] Credenciales listas (Amadeus, Telegram)
- [ ] Cuenta Render creada (gratis)
- [ ] Variables de entorno copiadas

---

## 🚀 RESUMEN EJECUTIVO

**Tu solución 100% gratuita:**
1. **Código** → GitHub ✅
2. **Hosting** → Render (GRATIS)
3. **Gestión** → Telegram Bot (Desde el móvil)
4. **Coste anual** → $0

**Después de desplegar:**
- Lee [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md) para aprender todos los comandos
- Usa `/agregar` para añadir vuelos desde Telegram
- Recibe alertas automáticas sin tocar el código

**¡Eso es todo lo que necesitas!** 🎉

---

## 📚 Documentación Relacionada

- 💬 **[TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md)** - Guía completa de cómo usar cada comando del bot
- 🚀 **[CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)** - Instrucciones detalladas de despliegue
- 📖 **[README.md](README.md)** - Introducción y arquitectura general
