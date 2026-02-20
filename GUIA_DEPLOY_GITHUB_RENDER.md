# 🚀 GUÍA COMPLETA: DEPLOY EN RENDER DESDE GITHUB

## 📋 ÍNDICE
1. [Preparar GitHub](#preparar-github)
2. [Crear Repositorio Nuevo](#crear-repositorio-nuevo)
3. [Subir Código a GitHub](#subir-código-a-github)
4. [Configurar Variables de Entorno](#configurar-variables-de-entorno)
5. [Crear Servicio en Render](#crear-servicio-en-render)
6. [Monitoreo y Actualizaciones](#monitoreo-y-actualizaciones)

---

## 1️⃣ PREPARAR GITHUB

### Paso 1.1: Crear Cuenta (si no la tienes)
Si ya tienes GitHub, salta a **Paso 1.2**

1. Ir a https://github.com
2. Click en "Sign up"
3. Completa email, contraseña, usuario
4. Verifica tu email

### Paso 1.2: Generar Token de Acceso Personal
Este token reemplaza la contraseña para operaciones en terminal:

1. En GitHub, click en tu avatar (arriba a la derecha)
2. Settings → Developer settings → Personal access tokens → Fine-grained tokens
3. Click "Generate new token"
4. **Nombre**: FlightTracker-Deploy
5. **Expiration**: 90 days (o más si deseas)
6. **Repository access**: All repositories
7. **Permissions**:
   - ✅ Contents (read & write)
   - ✅ Metadata (read)
8. Click "Generate token"
9. **COPIA EL TOKEN** (aparece una sola vez)

**⚠️ GUARDAR EN LUGAR SEGURO** (necesitarás después)

---

## 2️⃣ CREAR REPOSITORIO NUEVO

### Opción A: Crear Repo NUEVO (Recomendado - Limpio)

1. En GitHub, click "+" (arriba a la derecha) → New repository
2. **Nombre**: `flight-tracker` (o el que prefieras)
3. **Descripción**: "Rastreador automático de vuelos con múltiples APIs"
4. **Privacidad**: Public (recomendado para Render) o Private
5. ✅ "Add .gitignore" → Selecciona "Python"
6. ✅ "Add a README file"
7. Click "Create repository"

### Opción B: Migrar desde Repo Antiguo

Si tienes un repo viejo con commit history:

```powershell
# 1. Clonar repo antiguo como mirror
git clone --mirror https://github.com/TU_USUARIO/REPO_ANTIGUO.git tmp_repo

# 2. Push al nuevo repo
cd tmp_repo
git push --mirror https://github.com/TU_USUARIO/flight-tracker.git

# 3. Limpiar temp
cd ..
Remove-Item tmp_repo -Recurse -Force
```

---

## 3️⃣ SUBIR CÓDIGO A GITHUB

### Método 1: Desde Terminal (Recomendado)

```powershell
# 1. Navegar al proyecto
cd c:\XAMP\htdocs\Rastreador

# 2. Inicializar git (si no está ya inicializado)
git init

# 3. Agregar todos los archivos
git add .

# 4. Crear primer commit
git commit -m "Initial commit: Flight Tracker with 3 APIs (Amadeus, FlyScraper2, FlightsScraperData)"

# 5. Agregar origin (REEMPLAZA TU_USUARIO con tu usuario GitHub)
git remote add origin https://github.com/TU_USUARIO/flight-tracker.git

# 6. Cambiar rama a 'main' si es necesario
git branch -M main

# 7. Push al servidor (te pedirá loguarte)
git push -u origin main

# Cuando te pida usuario: TU_USUARIO
# Cuando te pida contraseña: PEGA EL TOKEN que copies antes
```

### Método 2: Desde GitHub Desktop (UI Gráfica)

1. Descargar desde https://desktop.github.com
2. File → Clone repository
3. Pegar: `https://github.com/TU_USUARIO/flight-tracker.git`
4. Seleccionar carpeta local
5. Cambiar a rama "main"
6. Click "Publish repository"

---

## 4️⃣ CONFIGURAR ARCHIVO `render.yaml`

Crear archivo en raíz del proyecto:

```yaml
# render.yaml - Configuración para Render

services:
  - type: web
    name: flight-tracker-bot
    runtime: python311
    
    # Script de inicio
    startCommand: python run_combined.py
    
    # Carpeta del código
    rootDir: .
    
    # Variables de entorno (se configuran en Render Dashboard)
    envVars:
      - key: AMADEUS_CLIENT_ID
        scope: run_time
      - key: AMADEUS_CLIENT_SECRET
        scope: run_time
      - key: RAPIDAPI_KEY
        scope: run_time
      - key: TELEGRAM_TOKEN
        scope: run_time
      - key: RAPIDAPI_HOST_FLYSCRAPER2
        scope: run_time
      - key: RAPIDAPI_HOST_FLIGHTSSCRAPER
        scope: run_time
      - key: DATABASE_URL
        scope: run_time
```

**Rutas en proyecto:**
```
flight-tracker/
├── render.yaml          ← CREAR ESTE ARCHIVO
├── requirements.txt     ← YA EXISTE
├── run_combined.py
├── src/
│   ├── api_aggregator.py
│   ├── telegram_bot.py
│   ├── database.py
│   └── ...
└── .gitignore
```

---

## 5️⃣ CONFIGURAR VARIABLES DE ENTORNO EN RENDER

**Necesitarás tener listos estos valores:**

```
AMADEUS_CLIENT_ID=tu_amadeus_id
AMADEUS_CLIENT_SECRET=tu_amadeus_secret
RAPIDAPI_KEY=tu_rapidapi_key
TELEGRAM_TOKEN=tu_telegram_token
RAPIDAPI_HOST_FLYSCRAPER2=fly-scraper.p.rapidapi.com
RAPIDAPI_HOST_FLIGHTSSCRAPER=flights-scraper-data.p.rapidapi.com
DATABASE_URL=postgresql://user:password@host:port/dbname
```

**Para obtenerlos:**
- **Amadeus**: https://developer.amadeus.com
- **RapidAPI**: https://rapidapi.com (ya tienes las keys)
- **Telegram**: @BotFather en Telegram
- **PostgreSQL** (opcional): https://render.com → New → PostgreSQL

---

## 6️⃣ CONECTAR GITHUB A RENDER

### Paso 6.1: Ir a Render

1. Ir a https://render.com
2. Click "Sign up" (puedes usar GitHub directo: "Continue with GitHub")
3. Autoriza Render a acceder a tus repos

### Paso 6.2: Crear Nuevo Servicio Web

1. En Dashboard, click "Create +" → "Web Service"
2. Selecciona: "Build and deploy from a Git repository"
3. Click "Connect" al repo `flight-tracker`
4. **Name**: flight-tracker
5. **Environment**: Python 3
6. **Build Command**: `pip install -r requirements.txt`
7. **Start Command**: `python run_combined.py`
8. **Instance Type**: Free (o Starter si necesitas más recursos)
9. Click "Create Web Service"

### Paso 6.3: Agregar Variables de Entorno

1. En la página del servicio, ir a "Environment"
2. Agregar cada variable:
   - `AMADEUS_CLIENT_ID` = tu_valor
   - `AMADEUS_CLIENT_SECRET` = tu_valor
   - `RAPIDAPI_KEY` = tu_valor
   - `TELEGRAM_TOKEN` = tu_valor
   - etc.

**Importante**: Para `DATABASE_URL`:
- Opción A: Usar PostgreSQL de Render
  ```
  postgresql://usuario:password@render-db-hostname:5432/tu_base_datos
  ```
- Opción B: Mantener SQLite (no requiere DATABASE_URL)

### Paso 6.4: Guardar y Desplegar

1. Click "Save"
2. Render automáticamente hace deploy

---

## 7️⃣ MONITOREO Y ACTUALIZACIONES

### Ver Logs en Tiempo Real

```powershell
# En terminal (opcional)
# Render muestra logs en el Dashboard automáticamente
```

1. En Render Dashboard
2. Click en tu servicio `flight-tracker`
3. Tab "Logs"
4. Ver output en vivo

### Actualizar Código

Cada vez que hagas push a GitHub:

```powershell
# 1. Hacer cambios locales
# 2. Commit
git add .
git commit -m "Descripción del cambio"

# 3. Push a GitHub
git push origin main

# 4. Render detecta automáticamente y hace redeploy
```

### Configurar Auto-Deploy

1. En Render, ir a "Settings" del servicio
2. "Auto-Deploy" → Enable
3. Selecciona rama: "main"
4. Guardar

---

## 8️⃣ TROUBLESHOOTING

### Problem: "Module not found"
```
Solución:
1. Asegúrate que requirements.txt está actualizado:
   pip freeze > requirements.txt
2. Git add . && git commit && git push
3. Render hará redeploy
```

### Problem: "Build fails"
```
Revisar Logs en Render:
1. Dashboard → Servicio → Logs
2. Buscar línea con "error"
3. Verificar requirements.txt y Python version
```

### Problem: "Bot no responde en Telegram"
```
Verificar:
1. TELEGRAM_TOKEN correcto en Variables de Entorno
2. Bot tiene webhooks configurados
3. Ver logs: Dashboard → Logs
```

### Problem: "APIs retornan 401"
```
Solución:
1. Verificar RAPIDAPI_KEY en Render
2. Verificar credenciales Amadeus
3. En Render Settings → Environment → revisar valores
```

---

## 9️⃣ COMANDOS GIT ÚTILES

```powershell
# Ver estado del repo
git status

# Ver commits recientes
git log --oneline -5

# Ver cambios sin hacer commit
git diff

# Deshacer cambios locales
git checkout -- .

# Ver ramas
git branch -a

# Cambiar a rama existente
git checkout -b nueva-rama

# Ver qué está en staging
git diff --staged

# Remover archivo del staging (antes de commit)
git reset HEAD archivo.py

# Cambiar mensaje del último commit
git commit --amend -m "Nuevo mensaje"
```

---

## 🔟 VALIDAR QUE TODO FUNCIONA

### En Local Primero

```powershell
cd c:\XAMP\htdocs\Rastreador

# Opcional: Crear venv limpio
python -m venv venv_test
.\venv_test\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Probar ejecución
python diagnostics.py

# Si todo está bien, subir a GitHub
git add .
git commit -m "Ready for production"
git push origin main
```

### En Render

1. Esperar a que Render termine el build (ver "Building..." luego "Active")
2. Ver Logs para confirmar que el bot inicia
3. Enviar mensaje al bot en Telegram para confirmar
4. Verificar que las búsquedas automáticas se ejecutan

---

## 📊 COMPARATIVA: LOCAL vs RENDER

| Aspecto | Local | Render |
|--------|-------|--------|
| **Costo** | Gratis (tu PC activa 24/7) | Gratis (con limitaciones) |
| **Uptime** | Mientras tu PC esté prendido | 99.9% en plan Starter+ |
| **RAM** | La que tengas | Free: 0.5GB, Starter: 2GB |
| **DB** | SQLite local | PostgreSQL en la nube |
| **Escalabilidad** | Limitada | Ilimitada (upgradeable) |
| **Acceso SSH** | N/A | Sí, en algunos planes |

---

## ✅ CHECKLIST FINAL

- [ ] Cuenta GitHub creada
- [ ] Token de acceso personal generado
- [ ] Repositorio `flight-tracker` creado
- [ ] Código pusheado a GitHub
- [ ] `render.yaml` agregado y pusheado
- [ ] Cuenta Render creada
- [ ] Web Service conectado a GitHub
- [ ] Variables de entorno configuradas
- [ ] Build completado exitosamente
- [ ] Bot responde en Telegram
- [ ] Auto-deploy habilitado
- [ ] Logs monitoreados

---

## 📞 NEXT STEPS

1. **AHORA**: Seguir pasos 1-6 para subir a Render
2. **PRUEBA**: Bot en Telegram contestando comandos
3. **MONITOR**: Ver logs cada 5 horas (búsqueda automática)
4. **ITERATE**: Hacer cambios → git push → Render auto-deploya

**¿Necesitas ayuda en algún paso?** Pide screenshots o errores específicos.
