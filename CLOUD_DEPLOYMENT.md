# 🚀 GUÍA DE DESPLIEGUE EN LA NUBE - Flight Tracker

## 📋 ÍNDICE

1. [Opción 1: Railway (Recomendado)](#opción-1-railway-recomendado)
2. [Opción 2: Render](#opción-2-render)
3. [Opción 3: Google Cloud Run](#opción-3-google-cloud-run)
4. [Comparativa de opciones](#comparativa-de-opciones)

---

## ✨ OPCIÓN 1: RAILWAY (RECOMENDADO)

Railway es **la mejor opción** para este proyecto porque:
- ✅ **Fácil de usar** (conecta directo con GitHub)
- ✅ **Gratis al principio** ($5/mes de crédito gratuito)
- ✅ **Base de datos incluida**
- ✅ **Variables de entorno seguras**
- ✅ **Soporte para Python**

### **Paso 1: Preparar el código para Railway**

```bash
# 1. Crear archivo Procfile (le dice a Railway cómo ejecutar)
echo "worker: python main.py" > Procfile

# 2. Crear archivo railway.json (configuración)
```

**railway.json:**
```json
{
  "build": {
    "builder": "dockerfile"
  }
}
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### **Paso 2: Subir a GitHub**

```bash
# Inicializar Git
git init
git add .
git commit -m "Initial commit: Flight Tracker"

# Crear repositorio en GitHub y subirlo
git remote add origin https://github.com/TU_USUARIO/Rastreador.git
git branch -M main
git push -u origin main
```

### **Paso 3: Conectar con Railway**

1. Ve a https://railway.app
2. Haz clic en **"Start a New Project"**
3. Selecciona **"Deploy from GitHub"**
4. Autoriza Railway y selecciona tu repositorio
5. Configura las variables de entorno (next step)

### **Paso 4: Configurar Variables de Entorno**

En el dashboard de Railway:

1. Ve a **Settings** → **Variables**
2. Añade tus credenciales:

```
AMADEUS_CLIENT_ID=tu_client_id
AMADEUS_CLIENT_SECRET=tu_client_secret
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id
DEBUG=False
```

3. Railway desplegará automáticamente

### **Paso 5: Verificar que está funcionando**

```bash
# Ver logs en Railway
railway logs

# Deberías ver:
# [2025-02-19 14:30:45] [INFO] ✅ Flight Tracker Scheduler inicializado
# [2025-02-19 14:30:45] [INFO] 🚀 FLIGHT TRACKER INICIADO
```

---

## ✨ OPCIÓN 2: RENDER

Render también es excelente y **totalmente gratuito** (pero con limitaciones):

### **Ventajas:**
- ✅ Gratuito indefinidamente (con limitaciones)
- ✅ Base de datos PostgreSQL incluida
- ✅ Fácil integración con GitHub
- ✅ SSL automático

### **Desventajas:**
- ⚠️ Los servicios gratuitos se "duermen" después de 15 min inactividad
- ⚠️ Menos poder computacional

### **Configuración rápida:**

1. Ve a https://render.com
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu GitHub repo
4. **Runtime:** Python 3.11
5. **Build Command:** `pip install -r requirements.txt`
6. **Start Command:** `python main.py`
7. Añade variables de entorno
8. Deploy

---

## ✨ OPCIÓN 3: GOOGLE CLOUD RUN

Google Cloud es **muy poderoso** pero requiere configuración más complicada:

### **Ventajas:**
- ✅ Muy escalable
- ✅ Buena documentación
- ✅ $300 de crédito gratuito
- ✅ Integración con otros servicios Google

### **Desventajas:**
- ⚠️ Más complejo de configurar
- ⚠️ Requiere tarjeta de crédito

### **Configuración básica:**

```bash
# 1. Instalar Google Cloud CLI
# Ver: https://cloud.google.com/sdk/docs/install

# 2. Autenticarse
gcloud auth login

# 3. Crear proyecto
gcloud projects create flight-tracker

# 4. Desplegar
gcloud run deploy flight-tracker \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📊 COMPARATIVA DE OPCIONES

| Feature | Railway | Render | Google Cloud Run |
|---------|---------|--------|------------------|
| **Precio** | $5/mes crédito | Gratis | $300 gratis |
| **Facilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **GitHub Integration** | ✅ Excelente | ✅ Excelente | ✅ Buena |
| **Base de Datos** | ✅ Incluida | ✅ Incluida | ⚠️ Requiere config |
| **Uptime 24/7** | ✅ Sí | ⚠️ Se duerme | ✅ Sí |
| **Python Support** | ✅ Excelente | ✅ Excelente | ✅ Excelente |
| **Variables Env** | ✅ Fácil | ✅ Fácil | ✅ Fácil |

**RECOMENDACIÓN:** 🥇 **Railway** (mejor equilibrio precio/facilidad)

---

## 🔧 ARCHIVOS NECESARIOS PARA DESPLEGAR

Asegúrate de tener estos archivos en tu repo:

```
Rastreador/
├── main.py ✅
├── requirements.txt ✅
├── Procfile (para Railway)
├── Dockerfile (para Railway)
├── .gitignore (para no subir .env)
├── src/
│   ├── __init__.py ✅
│   ├── config.py ✅
│   ├── logger.py ✅
│   ├── api.py ✅
│   ├── database.py ✅
│   ├── alerts.py ✅
│   ├── notifications.py ✅
│   └── scheduler.py ✅
├── data/ (gitignore this)
└── logs/ (gitignore this)
```

### **.gitignore necesario:**

```
# Entorno virtual
venv/
env/

# Variables de entorno
.env
.env.local
.env.*.local

# Datos locales
data/
logs/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 🚀 FLUJO COMPLETO DE DESPLIEGUE EN RAILWAY

### **1. Preparar archivos (local)**

```bash
# En la carpeta del proyecto
echo "worker: python main.py" > Procfile

# Crear Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
EOF
```

### **2. Crear .gitignore**

```bash
echo ".env
venv/
data/
logs/
__pycache__/
*.pyc
.DS_Store" > .gitignore
```

### **3. Subir a GitHub**

```bash
git init
git add .
git commit -m "Flight Tracker: Ready for production"
git remote add origin https://github.com/TU_USUARIO/Rastreador.git
git push -u origin main
```

### **4. En Railway Dashboard**

1. **New Project** → **GitHub**
2. Selecciona repositorio
3. Railway detectará `Procfile` y `Dockerfile`
4. Añade variables de entorno (AMADEUS, TELEGRAM, DEBUG=False)
5. **Deploy** automáticamente
6. Ver logs para confirmar que funciona

### **5. Verificar que está ejecutándose**

```bash
# Ver logs en Railway (desde Dashboard o CLI)
railway logs

# Deberías ver cada 2 horas:
# [INFO] 🔄 CHECK #1
# [INFO] ✅ Búsqueda completada
```

---

## 💾 BASE DE DATOS EN LA NUBE

Tu BD SQLite local (`data/vuelos.db`) se guardará en **Railway's ephemeral storage**.

**IMPORTANTE:** Railway limpia el almacenamiento cada deploy, así que:

### **Opción A: Usar PostgreSQL (Recomendado)**

Railway proporciona PostgreSQL gratuito. Para usarlo, modifica `config.py`:

```python
import os
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Conexión a PostgreSQL (requiere psycopg2)
    import psycopg2
    # ... configurar PostgreSQL
else:
    # SQLite local (desarrollo)
    DB_PATH = "data/vuelos.db"
```

### **Opción B: Guardar datos en archivos (Más simple)**

Crear un servicio de storage como:
- AWS S3
- Google Cloud Storage
- Dropbox API

---

## 🔔 MONITOREAR EL BOT EN LA NUBE

Una vez desplegado, querrás verificar que está funcionando correctamente. Puedes:

### **1. Recibir reportes diarios**
Ya está configurado para enviar reporte a las 09:00

### **2. Ver logs en Railway**
- Dashboard → Logs
- Filtra por errores o warnings

### **3. Crear uptime monitor**
- https://uptimerobot.com (gratis)
- Recibe alertas si el bot cae

---

## ⚠️ TROUBLESHOOTING

### **El bot no envía alertas**
```bash
# 1. Verificar logs
railway logs

# 2. Verificar variables de entorno
railway env

# 3. Verificar que al menos 1 vuelo está monitoreado
```

### **Error de BD cerrada**
Railway puede resetear la BD. Usa PostgreSQL en lugar de SQLite.

### **El bot se ejecuta pero no busca vuelos**
Verifica que `DEBUG=False` en variables de entorno.

### **Errores de Telegram**
- Confirma que `TELEGRAM_BOT_TOKEN` es correcto
- Confirma que `TELEGRAM_CHAT_ID` es un número válido

---

## 📞 SOPORTE Y RECURSOS

- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **Google Cloud Run:** https://cloud.google.com/run/docs
- **Python-Telegram-Bot:** https://python-telegram-bot.readthedocs.io

---

## ✅ CHECKLIST PRE-DESPLIEGUE

- ✅ `.env` funcionando localmente
- ✅ `python main.py` ejecuta sin errores
- ✅ Telegram bot recibe mensajes
- ✅ Al menos 1 vuelo monitoreado
- ✅ `.gitignore` creado (no subir `.env`)
- ✅ `Procfile` creado
- ✅ `Dockerfile` creado
- ✅ Repositorio GitHub creado
- ✅ `DEBUG=False` en variables de entorno cloud

¡Listo! 🚀
