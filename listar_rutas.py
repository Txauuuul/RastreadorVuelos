#!/usr/bin/env python3
"""
Listar todas las rutas de monitoreo activas
"""

from src.database import SessionLocal, Ruta

session = SessionLocal()
rutas = session.query(Ruta).filter_by(activo=True).all()

print("\n" + "=" * 80)
print("📍 RUTAS DE MONITOREO ACTIVAS")
print("=" * 80 + "\n")

if not rutas:
    print("❌ No hay rutas activas\n")
else:
    for r in rutas:
        retorno_info = f"{r.dias_regreso_min}-{r.dias_regreso_max} días" if r.es_ida_vuelta else "Solo ida"
        print(f"✅ Ruta #{r.id}")
        print(f"   Origen → Destino: {r.origen} → {r.destino}")
        print(f"   Período: {r.fecha_inicio.strftime('%Y-%m-%d')} a {r.fecha_fin.strftime('%Y-%m-%d')}")
        print(f"   Retorno: {retorno_info}")
        print(f"   Alerta: {r.porcentaje_rebaja_alerta}% rebaja o menor a €{r.precio_minimo_alerta}")
        print()

print("=" * 80)
print(f"Total: {len(rutas)} ruta(s) activa(s)\n")

session.close()
