# 💬 Guía de Comandos Telegram

Este documento explica cómo usar todos los comandos del bot de Telegram para gestionar tus vuelos.

---

## 🎯 Comandos Principales

### `/start` - Iniciar Bot
**Qué hace:** Muestra un mensaje de bienvenida con la lista de todos los comandos disponibles.

```
/start
```

**Respuesta del bot:**
```
¡Hola! 👋 Soy tu rastreador de vuelos.

Comandos disponibles:
/lista - Ver todos los vuelos monitoreados
/agregar - Añadir un nuevo vuelo
/modificar - Cambiar parámetros de un vuelo
/eliminar - Dejar de monitorear un vuelo
/historial - Ver historial de precios
/estadisticas - Ver estadísticas globales
```

---

## 📋 `/lista` - Ver Vuelos Monitoreados

**Qué hace:** Muestra todos los vuelos que estás monitoreando.

```
/lista
```

**Respuesta del bot:**
```
✈️ Vuelos monitoreados:

1. 🛫 MAD → NYC
   📅 25-12-2024
   💰 Mínimo: 300€ | -15% histórico
   ✅ ACTIVO

2. 🛫 BCN → LDN
   📅 15-08-2025
   💰 Mínimo: 200€ | -20% histórico
   ✅ ACTIVO

Total: 2 vuelos siendo monitoreados
```

**Cómo se usa:**
- Útil para ver los **IDs de los vuelos** (1, 2, 3, etc.)
- Necesitarás estos IDs para modificar o eliminar vuelos
- Muestra el estado (ACTIVO/INACTIVO)

---

## ✈️ `/agregar` - Añadir Nuevo Vuelo

**Qué hace:** Inicia un proceso de 5 pasos para agregar un nuevo vuelo a monitorear.

```
/agregar
```

### Paso 1: Origen
**Bot:** `¿Código IATA origen? (ej: MAD, BCN, BIO)`

**Ejemplos de códigos IATA válidos:**
```
MAD - Madrid (Barajas)
BCN - Barcelona (El Prat)
SVQ - Sevilla (San Pablo)
BIO - Bilbao
IBZ - Ibiza
AGP - Málaga
ALC - Alicante
NYC - Nueva York
LDN - Londres
CDG - París
ARN - Estocolmo
PRG - Praga
```

**Escribes:** `MAD`

**Bot responde:** ✅ Origen: MAD

### Paso 2: Destino
**Bot:** `¿Destino?`

**Escribes:** `NYC`

**Bot responde:** ✅ Destino: NYC

### Paso 3: Fecha de salida
**Bot:** `¿Fecha salida? (DD-MM-YYYY)`

**Formato:** Día-Mes-Año (dentro de 365 días)

**Ejemplos válidos:**
```
25-12-2024 ✅
15-08-2025 ✅
01-06-2025 ✅
```

**Escribes:** `25-12-2024`

**Bot responde:** ✅ Fecha: 25-12-2024

### Paso 4: Precio mínimo
**Bot:** `¿Precio mínimo (EUR)? (ej: 300)`

**Notas:**
- Sin símbolo €, solo números
- Será el precio por debajo del cual recibirás alertas
- Basado en precios reales encontrados

**Escribes:** `300`

**Bot responde:** ✅ Mínimo: 300 EUR

### Paso 5: Reducción mínima
**Bot:** `¿Reducción mínima (%)? (ej: 15)`

**Notas:**
- Sin símbolo %, solo números
- El bot comparará vs el promedio de los últimos 30 días
- Recibirás alerta si el precio es 15% menos que el promedio

**Escribes:** `15`

**Bot responde:**
```
✨ Vuelo creado exitosamente:

🛫 MAD → NYC
📅 25-12-2024
💰 Alertas cuando:
   • Precio < 300€ (umbral absoluto)
   • Precio < promedio -15% (histórico)

🔍 Próximo chequeo en ~2 horas
```

---

## ✏️ `/modificar` - Cambiar Parámetros

**Qué hace:** Permite cambiar el precio mínimo o la reducción % de un vuelo ya monitoreado.

```
/modificar
```

### Paso 1: Seleccionar vuelo
**Bot:** `¿Qué vuelo deseas modificar? (Número 1, 2, 3...)`

**Mostraremos la lista como en `/lista`**

**Escribes:** `1`

**Bot responde:** ✅ Seleccionaste: MAD → NYC (25-12-2024)

### Paso 2: Nuevo precio mínimo
**Bot:** `¿Nuevo precio mínimo (EUR)? (Actual: 300)`

**Escribes:** `280`

**Bot responde:** ✅ Precio mínimo actualizado: 280€

### Paso 3: Nueva reducción %
**Bot:** `¿Nueva reducción (%)? (Actual: 15)`

**Escribes:** `20`

**Bot responde:**
```
✅ Parámetros actualizados:

🛫 MAD → NYC (25-12-2024)
💰 Mínimo: 280€ | -20% histórico

✨ Los cambios están en efecto inmediatamente
```

---

## 🗑️ `/eliminar` - Dejar de Monitorear

**Qué hace:** Deja de monitorear un vuelo (lo marca como inactivo).

```
/eliminar
```

### Paso 1: Seleccionar vuelo
**Bot:** `¿Qué vuelo deseas eliminar? (Número 1, 2, 3...)`

**Escribes:** `1`

**Bot responde:**
```
⚠️ Confirma que deseas eliminar:
🛫 MAD → NYC (25-12-2024)

Escribe: "sí" para confirmar
```

### Paso 2: Confirmar
**Escribes:** `sí`

**Bot responde:**
```
✅ Vuelo eliminado exitosamente

MAD → NYC ya no está siendo monitoreado.
Puedes agregarlo nuevamente cuando quieras con /agregar
```

---

## 📊 `/historial` - Ver Historial de Precios

**Qué hace:** Muestra los últimos 5 precios registrados de un vuelo.

```
/historial
```

### Paso 1: Seleccionar vuelo
**Bot:** `¿De qué vuelo quieres ver el historial? (1, 2, 3...)`

**Escribes:** `1`

**Bot responde:**
```
📈 Historial: MAD → NYC (25-12-2024)

Últimos 5 precios registrados:

1. 285€ - IB (Iberia) - 23/01/25 14:30
2. 290€ - IB (Iberia) - 23/01/25 10:15
3. 295€ - VY (Vueling) - 22/01/25 16:45
4. 300€ - IB (Iberia) - 22/01/25 08:00
5. 305€ - AF (Air France) - 21/01/25 15:30

📊 Estadísticas:
   • Mínimo: 285€
   • Máximo: 305€
   • Promedio: 295€
   • Tendencia: 📉 bajando
```

---

## 📈 `/estadisticas` - Ver Estadísticas Globales

**Qué hace:** Muestra estadísticas totales del sistema.

```
/estadisticas
```

**Respuesta del bot:**
```
📊 ESTADÍSTICAS GLOBALES

✈️ Vuelos Monitoreados: 3 activos

💰 Precios:
   • Mínimo registrado: 85€
   • Máximo registrado: 950€
   • Promedio: 425€

🚨 Alertas Enviadas (últimos 30 días):
   • Total alertas: 12
   • Precio bajo umbral: 8
   • Precio bajo histórico: 4

📅 Actividad:
   • Último chequeo: hace 15 minutos
   • Próximo chequeo: en 1 hora 45 minutos
   • Datos almacenados: 156 registros
```

---

## ⚠️ Errores Comunes y Soluciones

### "Código IATA inválido"
**Problema:** Escribiste un código que no existe (ej: "ABC")

**Solución:** Usa códigos IATA reales:
```
MAD, BCN, SVQ, BIO, AGP, NYC, LDN, CDG, ARN, PRG
```

### "Fecha inválida"
**Problema:** Formato incorrecto (ej: "25/12/2024" en lugar de "25-12-2024")

**Solución:** Usa exactamente `DD-MM-YYYY`
```
✅ 25-12-2024
✅ 01-06-2025
❌ 25/12/2024
❌ 2024-12-25
```

### "Precio debe ser un número"
**Problema:** Incluiste simbolo € (ej: "300€")

**Solución:** Solo números
```
✅ 300
❌ 300€
❌ EUR 300
```

### "Porcentaje debe ser entre 1 y 99"
**Problema:** Pusiste un number fuera de rango

**Solución:** 1-99
```
✅ 15
✅ 50
❌ 0
❌ 150
```

---

## 🔔 Cuándo Recibes Notificaciones

### Alertas de Precio
El bot te envía un mensaje cuando:

1. **Precio cae por debajo del umbral mínimo**
   ```
   🚨 ¡¡ALERTA DE PRECIO!!
   
   MAD → NYC (25-12-2024)
   💰 Precio encontrado: 280€
   ⚡ Está por debajo de tu umbral: 300€
   ✈️ Aerolinea: Iberia (IB)
   ```

2. **Precio está 15% (o lo que configuraste) por debajo del promedio**
   ```
   🚨 ¡¡GANCHA DETECTADA!!
   
   MAD → NYC (25-12-2024)
   💰 Precio: 320€
   📊 Promedio histórico: 380€
   💡 Ahorro: -15.8% (60€ de descuento)
   ✈️ Aerolinea: Vueling (VY)
   ```

### Reporte Diario
**A las 09:00 AM (hora del servidor)** recibes un resumen:
```
📊 REPORTE DIARIO - 24 Enero 2025

✈️ Vuelos en monitoreo: 3
🚨 Alertas enviadas: 2
💰 Menor precio encontrado: 285€ (MAD→NYC)
📈 Precio promedio: 425€
```

### Nota sobre Alertas
- El bot espera **24 horas** antes de enviar la misma alerta nuevamente
- Evita spam pero podrás recibir de nuevo si el precio sigue bajando
- El límite se reinicia cada 24 horas

---

## 💡 Consejos de Uso

### 1. Configura Múltiples Rutas
No te limites a una ruta. Agrega las que te interesen:
```
/agregar  → MAD → NYC
/agregar  → BCN → CDG
/agregar  → SVQ → LDN
```

### 2. Usa Precios Realistas
Investiga precios actuales antes de configurar el umbral:
```
✅ MAD → NYC típicamente está entre 250-600€
   Configura mínimo en 300€ para no perder gangas

❌ No configures 100€ porque quizás nunca llegue
```

### 3. Reduce % Debe ser Razonable
```
✅ 15% - Buena relación señal/ruido
✅ 20% - Si eres paciente
❌ 5% - Demasiadas falsas alertas
❌ 50% - Casi nunca ocurrirá
```

### 4. Revisa Historial Regularmente
Usa `/historial` para entender patrones de precios:
```
¿Tendencia al alza o baja?
¿Cuál es el rango típico de precio?
¿Cuándo es más barato (mes, día)?
```

### 5. Mantén Pocos Vuelos Activos
```
✅ 3-5 vuelos - Fácil de gestionar
❌ 20+ vuelos - Demasiadas alertas
```

---

## 📞 Soporte

Si el bot no responde:

1. **Verifica que está desplegado en la nube** (Render, Railway, etc.)
2. **Revisa los logs** en el dashboard de tu plataforma
3. **Reinicia el bot** (redeploy desde la plataforma)

Si tienes dudas sobre los comandos:
- Escribe `/start` para recordar qué comandos existen
- Lee esta guía nuevamente
- Revisa el archivo `README.md` para más detalles

---

**¡Disfruta encontrando gangas en vuelos! ✈️💰**
