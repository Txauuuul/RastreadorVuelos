# 🚀 GUÍA DE PRIMER DESPLIEGUE EN RENDER

Esta guía te llevará paso a paso desde cero hasta tener tu bot 24/7 en la nube.

---

## 📋 REQUISITOS PREVIOS

Antes de empezar, asegúrate de tener:

- ✅ **Código en GitHub** (repo público o privado)
- ✅ **Credenciales Amadeus** (API ID + Secret)
- ✅ **Bot de Telegram creado** (token del bot + chat ID)
- ✅ **Cuenta en Render.com** (registro gratis)

**¿No tienes algo de esto?** Ve a [README.md](README.md) sección "Configurar variables de entorno"

---

## 🛠️ PASO 1: Preparar GitHub

### 1.1 Crear repositorio (si no lo has hecho)

```bash
cd C:\XAMP\htdocs\Rastreador
git init
git add .
git commit -m "Flight Tracker - Rastreador de Vuelos"
git remote add origin https://github.com/TU_USUARIO/Rastreador.git
git branch -M main
git push -u origin main
```

### 1.2 Verificar que .env NO está subido

```bash
git status
```

**Debe MOSTRAR:**
```
nothing to commit, working tree clean
```

**Debe INCLUIR estas líneas en `.gitignore`:**
```
.env
data/
logs/
__pycache__/
*.pyc
venv/
.vscode/
```

✅ Si todo está bien, continúa

---

## 📱 PASO 2: Crear Cuenta en Render

### 2.1 Ir a Render.com

```
https://render.com
```

### 2.2 Registrarse
- Click en "Sign Up"
- Opción: "Sign up with GitHub" (recomendado)
- Autorizar Render para acceder a tu GitHub
- Confirmar email

### 2.3 Conectar repositorio (opcional pero recomendado)
- Ir a Account Settings → Connected Services
- Click "GitHub"
- Seleccionar tu repo "Rastreador"

✅ Cuenta Render lista

---

## ☁️ PASO 3: Crear Web Service en Render

### 3.1 Desde Dashboard Render
```
Dashboard → New + → Web Service
```

### 3.2 Seleccionar repositorio
- Click "Connect" en tu repo "Rastreador"
- Seleccionar branch: `main`

### 3.3 Configurar servicio

**Name (Nombre):**
```
rastreador-vuelos
```

**Region (Región):**
```
Frankfurt (Europa - para mejor latencia)
```

**Runtime (Entorno):**
```
Python 3
```

**Build Command (Comando compilación):**
```
pip install -r requirements.txt
```

**Start Command (Comando inicio):**
```
python main.py
```

### 3.4 Plan (GRATIS)
- Seleccionar "Free" (sin crédito de tarjeta)

✅ Enviado a crear

---

## 🔐 PASO 4: Agregar Variables de Entorno

Mientras se crea el servicio, agrega las variables:

### 4.1 En Render Dashboard
```
Tu servicio → Environment
```

### 4.2 Copiar tus valores de .env

Agrega cada variable:

| Variable | Valor | Ejemplo |
|----------|-------|---------|
| **AMADEUS_CLIENT_ID** | Tu ID Amadeus | `abc123def456` |
| **AMADEUS_CLIENT_SECRET** | Tu Secret Amadeus | `xyz789uvw123` |
| **TELEGRAM_BOT_TOKEN** | Token del bot | `7123456789:ABCdefGHIjklMNOpqrSTU...` |
| **TELEGRAM_CHAT_ID** | Tu chat ID | `987654321` |
| **DEBUG** | `False` | `False` |
| **LOG_LEVEL** | `INFO` | `INFO` |
| **MIN_PRICE_THRESHOLD** | 100 | `100` |

**¿Dónde encontrar cada valor?**

**Amadeus:**
```
https://developers.amadeus.com
- Login → My Self Service Workspace
- Click en tu app
- Client ID
- Client Secret
```

**Telegram:**
```
En Telegram chat con tu bot:
/start
Bot responde con tu CHAT_ID

De BotFather:
/mybots → selecciona bot → HTTP API → token
```

### 4.3 Save (Guardar)
- Click "Save Changes"
- Render redeploya automáticamente

✅ Variables guardadas

---

## ✅ PASO 5: Esperar Deploy

### 5.1 Monitorear el despliegue

En Render Dashboard:
```
Tu servicio → Logs
```

**Espera a ver algo como:**
```
[INFO] 🚀 FLIGHT TRACKER INICIADO
[INFO] 📅 Próximo check: XX:XX
```

**Si ves errores, revisa la sección "Troubleshooting" más abajo**

⏱️ Tiempo estimado: 2-5 minutos

---

## 📲 PASO 6: Primer Check

### 6.1 Abrir Telegram

Busca tu bot en Telegram.

### 6.2 Enviar comando
```
/start
```

**Deberías recibir algo como:**
```
¡Hola! 👋 Soy tu rastreador de vuelos.

Comandos disponibles:
/lista - Ver todos los vuelos monitoreados
/agregar - Añadir un nuevo vuelo
/modificar - Cambiar parámetros de un vuelo
...
```

✅ Si ves esto, ¡FUNCIONA!

---

## ✈️ PASO 7: Agregar Primer Vuelo

### 7.1 En Telegram
```
/agregar
```

### 7.2 Sigue los pasos (5 preguntas)

**Ejemplo:**
```
You: /agregar
Bot: ¿Código IATA origen?
You: MAD
Bot: ✅ Origen: MAD
     ¿Destino?
You: NYC
Bot: ✅ Destino: NYC
     ¿Fecha salida? (DD-MM-YYYY)
You: 25-12-2024
Bot: ✅ Fecha: 25-12-2024
     ¿Precio mínimo (EUR)?
You: 300
Bot: ✅ Mínimo: 300 EUR
     ¿Reducción mínima (%)?
You: 15
Bot: ✨ Vuelo creado exitosamente!
```

### 7.3 Verificar
```
/lista
```

Deberías ver tu vuelo.

✅ Primer vuelo agregado

---

## 🎉 ¡COMPLETADO!

Tu sistema está 100% operativo:

- ✅ Código en GitHub
- ✅ Bot corriendo en Render (gratis)
- ✅ Variables de entorno configuradas
- ✅ Primer vuelo monitoreado
- ✅ Recibirá la primera alerta en ~2 horas

---

## 📊 QUÉ OCURRE AHORA

### Automáticamente cada 2 horas:
1. Bot busca vuelos en Amadeus
2. Compara precios con tu umbral
3. Si hay ganga, ¡te avisa por Telegram!

### Cada día a las 09:00:
1. Resumen completo del día
2. Vuelos monitoreados
3. Alertas enviadas
4. Precio promedio

### Ejemplo de alerta:
```
🚨 ¡¡ALERTA DE PRECIO!!

🛫 MAD → NYC
📅 25-12-2024
💰 Precio: 285€
⬇️ Umbral: 300€
✈️ Iberia (IB)

👉 ¡Ahorra 15€!
```

---

## 🐛 TROUBLESHOOTING

### El bot no responde a /start

**Problema:** Telegram timeout

**Solución:**
1. Verifica que el token en Render es correcto
2. Revisa logs en Render Dashboard
3. Reinicia el servicio (botón "Restart" en Render)

### Errores en logs

**Problema:** Ves en Logs algo rojo

**Soluciones comunes:**
```
"Invalid AMADEUS credentials"
→ Verifica API ID y Secret en Render

"Invalid Telegram token"
→ Verifica token en Render

"Database locked"
→ Espera a que termine la primera búsqueda (2 min)
```

### Ningún vuelo aparece en /lista

**Problema:** Agregaste el vuelo pero no aparece

**Solución:**
1. `/lista` nuevamente
2. Si sigue sin aparecer, revisa logs
3. Intenta `/agregar` nuevamente

### No recibo alertas después de 2 horas

**Posibles razones:**
1. El precio NO cayó por debajo del umbral
2. El precio NO está 15% por debajo del promedio
3. Ya se envió una alerta ayer (cooldown 24h)

**Cómo verificar:**
```
/historial  → Ver últimos precios
/estadisticas → Ver actividad global
```

---

## 📚 PRÓXIMOS PASOS

1. **Leer [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md)**
   - Guía completa de todos los comandos
   - Ejemplos paso a paso
   - Consejos de uso

2. **Monitorear por 24 horas**
   - Verifica que las búsquedas ocurren cada 2 horas
   - Observa los precios que registra
   - Ajusta los umbrales si es necesario

3. **Agregar más vuelos**
   - Una vez veas que funciona, agrega más rutas
   - Prueba diferentes umbrales
   - Encuentra el balance entre alertas útiles y spam

---

## 💡 TIPS PROFESIONALES

### 1. Monitorea precios realistas
```
Investiga precios históricos ANTES de agregar
No pongas un umbral de 100€ para MAD→NYC
Típicamente está 300-600€
```

### 2. Usa múltiples alertas por ruta
```
/agregar MAD→NYC mín=300 reducción=15%
/agregar MAD→NYC mín=280 reducción=10%
```

### 3. Revisa logs regularmente
```
Render Dashboard → Logs
Busca errores o patrones
```

### 4. Mantén actualizado en GitHub
```
Si haces cambios locales:
git add .
git commit -m "mensaje"
git push
→ Render redeploya automáticamente
```

---

## 🆘 SOPORTE

Si algo no funciona:

1. **Revisa esta guía nuevamente**
2. **Lee [README.md](README.md) sección Troubleshooting**
3. **Revisa los logs en Render Dashboard**
4. **Verifica que tus credenciales son correctas**

---

**¡Felicidades! Tu rastreador de vuelos está 24/7 en la nube. 🎉✈️**

Próxima lectura: [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md)
