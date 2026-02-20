# Procfile - Configuración para Render
# ===================================
# Antes: worker: python main.py
# Ahora: Ejecuta Bot + Buscador en paralelo en UN SOLO proceso
#
# VENTAJAS:
# ✅ 1 solo dyno en Render (gratuito)
# ✅ Bot escucha Telegram 24/7
# ✅ Buscador automático cada 5 horas
# ✅ Sin necesidad de 2 terminales

worker: python run_combined.py
