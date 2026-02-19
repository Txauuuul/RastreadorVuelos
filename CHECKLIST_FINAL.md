# ✅ CHECKLIST FINAL - ANTES DE DESPLEGAR

Esta es tu última verificación antes de poner el bot en producción en Render.

---

## 📝 REQUISITOS TÉCNICOS

### GitHub
- [ ] Código en repositorio GitHub
- [ ] Rama `main` con código actualizado
- [ ] `.env` está en `.gitignore` (NO subido)
- [ ] `Procfile` existe en raíz
- [ ] `requirements.txt` actualizado

**Verificar:**
```bash
git status  # No debe mostrar .env
git log     # Ver últimos commits
```

---

## 🔐 CREDENCIALES

### Amadeus API
- [ ] Tienes AMADEUS_CLIENT_ID (14 caracteres)
- [ ] Tienes AMADEUS_CLIENT_SECRET (32 caracteres)
- [ ] Las credenciales funcionan (testeado localmente)

**Dónde obtener:**
```
https://developers.amadeus.com
→ My Self Service Workspace
→ Tu App
→ Copy variables
```

### Telegram Bot
- [ ] Tienes TELEGRAM_BOT_TOKEN (@BotFather)
- [ ] Tienes TELEGRAM_CHAT_ID (número tu cuenta)
- [ ] Bot responde a /start (testeado localmente)

**Dónde obtener:**
```
Telegram: @BotFather
→ /mybots → tu bot → API Token (copiar)

Tu chat: En Telegram con tu bot /start
Chat ID aparece en logs
```

---

## 👤 CUENTA RENDER

- [ ] Cuenta Render creada (https://render.com)
- [ ] Email confirmado
- [ ] Conectada con GitHub (opcional pero recomendado)
- [ ] Métodos de pago verificados (para escalado en futuro)

---

## 📱 BOT TELEGRAM

- [ ] Bot creado en BotFather
- [ ] Nombre del bot configurado
- [ ] Descripción agregada
- [ ] Comandos listados en BotFather

**Comandos en BotFather:**
```
/setcommands

start - Iniciar bot
lista - Ver vuelos monitoreados
agregar - Añadir nuevo vuelo
modificar - Cambiar parámetros
eliminar - Dejar de monitorear
historial - Ver historial de precios
estadisticas - Ver estadísticas globales
```

---

## 🗂️ ARCHIVOS LOCALES

### Archivos que DEBEN estar en raíz
- [ ] `main.py` ✅
- [ ] `manage_flights.py` ✅
- [ ] `requirements.txt` ✅
- [ ] `Procfile` ✅
- [ ] `Dockerfile` ✅
- [ ] `.env.example` ✅
- [ ] `.gitignore` ✅
- [ ] `README.md` ✅

### Carpeta `src/`
- [ ] `__init__.py` ✅
- [ ] `config.py` ✅
- [ ] `logger.py` ✅
- [ ] `api.py` ✅
- [ ] `database.py` ✅
- [ ] `alerts.py` ✅
- [ ] `notifications.py` ✅
- [ ] `scheduler.py` ✅
- [ ] `telegram_commands.py` ✅

### Documentación
- [ ] `README.md` ✅
- [ ] `HOJA_DE_RUTA.md` ✅
- [ ] `PRIMER_DESPLIEGUE.md` ✅
- [ ] `TELEGRAM_COMMANDS.md` ✅
- [ ] `PLATAFORMAS_GRATUITAS.md` ✅
- [ ] `CLOUD_DEPLOYMENT.md` ✅

---

## 🧪 PRUEBAS LOCALES

### Antes de pushear a GitHub

- [ ] `python -m src.api` - API funciona ✅
- [ ] `python -m src.database` - BD crea tablas ✅
- [ ] `python -m src.notifications` - Telegram envía mensaje ✅
- [ ] `python main.py --mode test` - Check único funciona ✅
- [ ] Manager: `python manage_flights.py` - Menu funciona ✅

**Resultado esperado:**
```
Todos los tests sin errors
Bot recibe mensaje en Telegram
"✅ Check completado exitosamente"
```

---

## 🚀 RENDER - SETUP

### Crear Web Service
- [ ] Conectar repositorio GitHub
- [ ] Seleccionar rama `main`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python main.py`
- [ ] Plan: Free (gratuito)

### Variables de Entorno (Environment)
Agregar EXACTAMENTE estas variables:

```
AMADEUS_CLIENT_ID          = [TU_ID]
AMADEUS_CLIENT_SECRET      = [TU_SECRET]
TELEGRAM_BOT_TOKEN         = [TU_TOKEN]
TELEGRAM_CHAT_ID           = [TU_CHAT_ID]
DEBUG                      = False
LOG_LEVEL                  = INFO
MIN_PRICE_THRESHOLD        = 100
```

**Puntos importantes:**
- [ ] DEBUG = `False` (SIN esto solo corre una vez)
- [ ] No hay espacios alrededor del =
- [ ] Los valores sin comillas
- [ ] Verificar cada variable copiada correctamente

---

## 📊 VERIFICACIÓN POST-DEPLOY

### Esperar a que termine el build
- [ ] Status "Live" en Render
- [ ] URL web service visible
- [ ] Logs muestran "[INFO] 🚀 FLIGHT TRACKER INICIADO"

**Tiempo estimado:** 2-5 minutos

### Primer check
- [ ] En Telegram: `/start`
- [ ] Bot responde con bienvenida
- [ ] Mensajes llegan instantáneamente

**Si no responde:**
- [ ] Revisa logs en Render Dashboard
- [ ] Verifica token de Telegram
- [ ] Reinicia servicio en Render

### Agregar primer vuelo
- [ ] `/agregar`
- [ ] Sigue 5 pasos
- [ ] `/lista` muestra el vuelo

**Ejemplo:**
```
/agregar
? MAD
? NYC
? 25-12-2024
? 300
? 15

✨ Vuelo creado exitosamente!
```

---

## 🔍 CHECKS CADA HORA

**Primeras 24 horas:**

- [ ] Cada 2 horas verifica logs en Render
- [ ] Busca señal: `[INFO] 🔍 Buscando: MAD → CDG`
- [ ] Verifica que se escriben precios en BD

**Primeras 48 horas:**

- [ ] Verifica si llega resumen diario a las 09:00
- [ ] Si hay alertas, revisa sección "[INFO] 🚨 ALERTA"
- [ ] Comprueba que el formato es correcto

**Después de 72 horas:**

- [ ] El sistema debe estar 100% operativo
- [ ] Sin errors en logs
- [ ] Alertas llegando a Telegram
- [ ] Listo para "olvidar"

---

## 📱 GESTIÓN DEL BOT

### Comandos básicos que DEBES probar

```
/start          → ✅ Bienvenida
/lista          → ✅ Muestra tus vuelos
/agregar        → ✅ Nuevo vuelo (completa 5 pasos)
/estadisticas   → ✅ Stats globales
```

### Después de agregar vuelos

```
/lista          → Ver IDs de vuelos
/historial      → Seleccionar vuelo N → Ver precios
/modificar      → Cambiar umbrales
/eliminar       → Dejar de monitorear
```

---

## 🚨 ERRORES COMUNES A EVITAR

### ❌ NO hacer esto:

```
DEBUG = True        ← Bot solo corre una vez
DEBUG = "False"     ← String, no boolean
```

### ✅ HACER esto:

```
DEBUG = False       ← Boolean correcto
DEBUG = FALSE       ← También válido (case-insensitive)
```

---

### ❌ NO hacer esto:

```
AMADEUS_CLIENT_ID = " abc123 "  ← Espacios
AMADEUS_CLIENT_ID = 'abc123'    ← Comillas
```

### ✅ HACER esto:

```
AMADEUS_CLIENT_ID = abc123      ← Sin espacios ni comillas
```

---

### ❌ NO hacer esto:

```
.env SUBIDO a GitHub
main.py con credenciales hard-coded
```

### ✅ HACER esto:

```
.env en .gitignore
.env.example como plantilla (sin valores)
```

---

## 📋 VERIFICACIÓN FINAL (ANTES DE PRESIONAR DEPLOY)

```
Código
├─ [ ] GitHub con último push
├─ [ ] .env NO subido
└─ [ ] Procfile + Dockerfile existe

Credenciales  
├─ [ ] Amadeus ID y Secret (testeado)
├─ [ ] Telegram token (testeado)
└─ [ ] Chat ID (número)

Render Setup
├─ [ ] Cuenta creada
├─ [ ] Repo conectado
├─ [ ] Todas las 8 variables agregadas
└─ [ ] DEBUG = False

Tests Locales
├─ [ ] API OK
├─ [ ] Database OK
├─ [ ] Notifications OK
└─ [ ] Main OK
```

---

## 🎯 RESUMEN

**Si checkeaste TODO:**

✅ Tu sistema **ESTÁ LISTO para producción**

👉 **Siguiente paso:** Ve a [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md)

**Tiempo de despliegue:** 5 minutos  
**Tiempo de primeras alertas:** 2 horas

---

## 🆘 Si algo falla

1. **Lee la sección "Troubleshooting"**
   - [README.md](README.md#-troubleshooting)
   - [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md#-troubleshooting)

2. **Revisa logs en Render Dashboard**
   - Dashboard → Tu servicio → Logs

3. **Verifica variables de entorno**
   - Dashboard → Tu servicio → Environment
   - Compara con `.env.example`

4. **Si aún no funciona**
   - Reinicia el servicio en Render
   - Espera 2 minutos
   - Prueba `/start` en Telegram nuevamente

---

**¡Estás a 5 minutos de tener tu rastreador 24/7 en la nube! 🚀**

¿Listo? → [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md)
