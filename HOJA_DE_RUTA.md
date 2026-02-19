# 📑 HOJA DE RUTA - POR DÓNDE EMPEZAR

¡Felicidades! Tienes un **rastreador de vuelos completo y listo para desplegar**.

Esta guía te muestra en qué orden leer la documentación según tu situación.

---

## 🎯 ESCENARIOS

### 1️⃣ "Quiero desplegar AHORA en Render"

**Ruta recomendada:**

```
1. Lee PRIMER_DESPLIEGUE.md (15 minutos)
   ↓
2. Lee TELEGRAM_COMMANDS.md (10 minutos)
   ↓
3. ¡Deployment hecho! 🎉
```

**Documentos:**
- ⭐ [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md) - Paso a paso
- [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md) - Cómo usar el bot

---

### 2️⃣ "Quiero entender qué es esto PRIMERO"

**Ruta recomendada:**

```
1. Lee README.md (secciones: ✨ Características, 📊 Cómo funciona)
   ↓
2. Lee PLATAFORMAS_GRATUITAS.md (entender costos)
   ↓
3. Lee PRIMER_DESPLIEGUE.md (cuando estés listo)
   ↓
4. Lee TELEGRAM_COMMANDS.md (después de desplegar)
```

**Documentos:**
- [README.md](README.md) - Visión general
- [PLATAFORMAS_GRATUITAS.md](PLATAFORMAS_GRATUITAS.md) - Opciones de hosting
- [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md) - Deployment
- [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md) - Uso del bot

---

### 3️⃣ "Tengo dudas técnicas"

**Ruta recomendada:**

```
1. README.md sección "📊 CÓMO FUNCIONA"
   ↓
2. README.md sección "📋 ESTRUCTURA DEL PROYECTO"
   ↓
3. README.md sección "🐛 TROUBLESHOOTING"
```

**Documentos:**
- [README.md](README.md) - Toda la arquitectura

---

### 4️⃣ "Quiero ver toda la documentación" 

**Orden completo por relevancia:**

| # | Documento | Tiempo | Lugar |
|---|-----------|--------|-------|
| 1 | 🚀 [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md) | 15 min | COMIENZA AQUÍ |
| 2 | 💬 [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md) | 10 min | Después de desplegar |
| 3 | 📖 [README.md](README.md) | 20 min | Arquitectura general |
| 4 | ☁️ [PLATAFORMAS_GRATUITAS.md](PLATAFORMAS_GRATUITAS.md) | 10 min | Si quieres alternativas |
| 5 | 🚀 [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) | 15 min | Si usas Railway/GCP |

---

## 📋 DOCUMENTO RÁPIDO

Si **tienes poco tiempo**, aquí va el ultra-resumen:

### Qué es este proyecto
```
Un bot de Telegram que busca vuelos cada 2 horas
y te avisa cuando encuentren precios buenos
```

### Cómo funciona
```
SCHEDULER (cada 2h) 
  → Busca vuelos en Amadeus API
  → Guarda precios en BD SQLite
  → Detecta gangas basado en umbrales
  → ¡Te avisa por Telegram!
```

### Desplegar (3 pasos)
```
1. GitHub → Render.com → Conectar repo
2. Agregar variables de entorno (Amadeus, Telegram)
3. ¡Listo! Bot 24/7 sin costo
```

### Uso
```
En Telegram:
  /agregar → Añadir vuelo a monitorear
  /lista → Ver tus vuelos
  /estadisticas → Ver actividad
  /historial → Precios históricos
```

---

## ⏱️ PLAN POR HORAS

### Hora 0-1: Setup Local
```
✅ Clonar repo
✅ Instalar dependencias
✅ Copiar .env
✅ Probar localmente
```

### Hora 1-2: Deployment
```
✅ Subir a GitHub
✅ Crear cuenta Render
✅ Deploy automático
✅ Verificar funciona
```

### Hora 2-3: Configuración
```
✅ Agregar primer vuelo
✅ Ver alerta de prueba
✅ Ajustar umbrales
✅ Agregar más vuelos
```

### Listo!
```
✅ Sistema 24/7 funcionando
✅ Alertas llegando a Telegram
✅ Costo anual: $0
```

---

## 🎓 PARA APRENDER

Si te interesa **entender el código internamente**:

1. **Arquitectura general**
   - Lee: [README.md](README.md) sección "📊 CÓMO FUNCIONA"
   - Concepto: Separación de responsabilidades

2. **Flujo de datos**
   ```
   main.py 
     → scheduler.py (coordina)
       → api.py (obtiene datos)
       → database.py (guarda)
       → alerts.py (analiza)
       → notifications.py (notifica)
   ```

3. **Bases de datos**
   - Archivo: `data/vuelos.db` (SQLite)
   - Tablas: 3 ({watched_flights, price_history, alerts_sent})
   - Queries: 20+ operaciones CRUD

4. **Telegram Bot**
   - Archivo: [src/telegram_commands.py](src/telegram_commands.py) (500 líneas)
   - Patrón: ConversationHandler (máquina de estados)
   - Comandos: 7 disponibles

5. **Alertas**
   - Archivo: [src/alerts.py](src/alerts.py)
   - 2 tipos: umbral absoluto + análisis histórico
   - Deduplicación: cooldown 24h

---

## 🤔 PREGUNTAS FRECUENTES

### ¿Por cuánto me cuesta desplegar?
**Respuesta:** $0. Render es completamente gratuito.

Ver: [PLATAFORMAS_GRATUITAS.md](PLATAFORMAS_GRATUITAS.md)

### ¿Necesito mi PC prendido 24/7?
**Respuesta:** No. El bot corre en Render en la nube.

### ¿Puedo agregar vuelos desde el teléfono?
**Respuesta:** Sí. Usas Telegram desde cualquier dispositivo.

Ver: [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md)

### ¿Cada cuánto busca vuelos?
**Respuesta:** Cada 2 horas automáticamente.

Resumen diario: 09:00 AM

### ¿Cuánto historial guarda?
**Respuesta:** 30 días de precios. Después se limpia automáticamente.

### ¿Puedo personalizar las búsquedas?
**Respuesta:** Sí. Mediante comandos Telegram:
- `/agregar` → Nueva ruta
- `/modificar` → Cambiar umbrales
- `/eliminar` → Dejar de monitorear

Ver: [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md)

---

## 🚨 ALGO NO FUNCIONA

Sigue estos pasos:

1. **Lee la sección Troubleshooting**
   - [README.md](README.md#-troubleshooting) sección 🐛

2. **Si es deployment**
   - [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md#-troubleshooting)

3. **Si es uso del bot**
   - [TELEGRAM_COMMANDS.md](TELEGRAM_COMMANDS.md#-errores-comunes)

---

## 📞 CHECKLIST PREDESPLIEGUE

Antes de hacer deployment, verifica:

- [ ] Código en GitHub
- [ ] `.env` NO está subido
- [ ] Tienes credenciales Amadeus
- [ ] Tienes token de Telegram bot
- [ ] Tienes chat ID de Telegram
- [ ] Cuenta Render creada
- [ ] Procfile y Dockerfile en raíz

Ver: [PRIMER_DESPLIEGUE.md - Paso 1](PRIMER_DESPLIEGUE.md#-requisitos-previos)

---

## 🎉 SIGUIENTE PASO

**¿Listo para empezar?**

👉 **Ve a [PRIMER_DESPLIEGUE.md](PRIMER_DESPLIEGUE.md)**

Toma 15 minutos y tu bot estará 24/7 en Render.

---

**Bienvenido al rastreador de vuelos. ✈️ Que disfrutes encontrando gangas! 💰**
