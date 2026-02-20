# ⚡ QUICKSTART: Deploy en 5 Minutos

## 1️⃣ GitHub (3 min)

```powershell
# a) Sign up: https://github.com/signup
# b) Generar token: GitHub → Settings → Developer settings → 
#    Personal access tokens → Tokens (classic) → Generate new

# c) En terminal:
cd c:\XAMP\htdocs\Rastreador
git init
git add .
git commit -m "Flight Tracker v3 - 3 APIs + Deploy"
git remote add origin https://github.com/TU_USUARIO/flight-tracker.git
git branch -M main
git push -u origin main
# (Usuario: TU_USUARIO, Contraseña: PEGA_EL_TOKEN)
```

## 2️⃣ Render (2 min)

1. **Sign up**: https://render.com (usa GitHub para más rápido)
2. **Create Web Service**:
   - Selecciona repositorio: `flight-tracker`
   - Name: `flight-tracker`
   - Runtime: `Python 3.11`
   - Build: `pip install -r requirements.txt`
   - Start: `python run_combined.py`
   - Instance: Free
   - Create

3. **Environment Variables** (mientras está deployando):
   - AMADEUS_CLIENT_ID = tu_valor
   - AMADEUS_CLIENT_SECRET = tu_valor
   - RAPIDAPI_KEY = tu_valor
   - TELEGRAM_TOKEN = tu_valor
   - DATABASE_URL = postgresql://... (si usas DB remoto)

4. **Save** → Render auto-deploya

## ✅ Done!

- Bot activo en Telegram 24/7
- Búsqueda automática cada 5 horas
- Alertas por precio
- Deploy automático con `git push`

## 📂 Archivos Creados

- `render.yaml` → Config para Render
- `GUIA_DEPLOY_GITHUB_RENDER.md` → Guía completa
- `setup_deploy.py` → Verificación de setup
- `agregar_rutas.py` → Script para agregar rutas
- `.env.example` → Template de variables

## 🔗 Links Útiles

- [Crear Token GitHub](https://github.com/settings/tokens/new)
- [Render Dashboard](https://dashboard.render.com)
- [Amadeus API Keys](https://developer.amadeus.com)
- [RapidAPI Keys](https://rapidapi.com/user/me)
- [Telegram BotFather](https://t.me/botfather)

## 🆘 Si Algo Falla

1. Ver logs en Render → [tu-servicio] → Logs
2. Revisar Variables de Entorno en Render Settings
3. Probar localmente primero: `python run_combined.py`
4. Hacer `git push` nuevamente (Render auto-redeploya)

---

**¿Necesitas ayuda?** Revisa `GUIA_DEPLOY_GITHUB_RENDER.md`
