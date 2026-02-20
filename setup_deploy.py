#!/usr/bin/env python3
"""
setup_deploy.py - Script de inicialización para Deploy
Ejecutar este script antes de subir a GitHub
"""

import os
import sys
from pathlib import Path

def check_file(filename, required=True):
    """Verificar que un archivo existe"""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    return exists

def check_files():
    """Verificar que todos los archivos necesarios existen"""
    print("\n" + "="*60)
    print("📋 VERIFICANDO ARCHIVOS NECESARIOS")
    print("="*60 + "\n")
    
    required_files = [
        "requirements.txt",
        "render.yaml",
        ".gitignore",
        ".env.example",  # Crear si no existe
        "GUIA_DEPLOY_GITHUB_RENDER.md",
    ]
    
    required_dirs = [
        "src",
        "data",
    ]
    
    all_ok = True
    
    # Archivos
    for file in required_files:
        if not check_file(file):
            all_ok = False
    
    print()
    
    # Directorios
    for dir in required_dirs:
        exists = os.path.isdir(dir)
        status = "✅" if exists else "❌"
        print(f"{status} {dir}/")
        if not exists:
            all_ok = False
    
    return all_ok

def create_env_example():
    """Crear archivo .env.example si no existe"""
    if not os.path.exists(".env.example"):
        print("\n📝 Creando .env.example...")
        
        env_content = """# Flight Tracker - Variables de Entorno
# Copiar este archivo a .env y llenar con tus valores

# Amadeus API (https://developer.amadeus.com)
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret

# RapidAPI (https://rapidapi.com)
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST_FLYSCRAPER2=fly-scraper.p.rapidapi.com
RAPIDAPI_HOST_FLIGHTSSCRAPER=flights-scraper-data.p.rapidapi.com

# Telegram Bot (@BotFather)
TELEGRAM_TOKEN=your_telegram_bot_token

# Database
# Para desarrollo local usa SQLite (por defecto)
# Para producción en Render usa PostgreSQL:
# DATABASE_URL=postgresql://user:password@host:5432/flight_tracker
DATABASE_URL=sqlite:///data/vuelos.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/flight_tracker.log

# Búsqueda automática
SEARCH_INTERVAL_HOURS=5
"""
        
        with open(".env.example", "w") as f:
            f.write(env_content)
        
        print("✅ .env.example creado")

def create_git_init_script():
    """Crear script para inicializar repo git"""
    if not os.path.exists(".git"):
        print("\n⚙️  Iniciando repositorio Git...")
        os.system("git init")
        os.system("git add .")
        os.system('git commit -m "Initial commit: Flight Tracker with 3 APIs"')
        print("✅ Git inicializado")

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║    🚀 SETUP DEPLOY - FLIGHT TRACKER                           ║
║    Preparar proyecto para GitHub + Render                     ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # 1. Verificar archivos
    if not check_files():
        print("\n⚠️  FALTAN ARCHIVOS NECESARIOS")
        sys.exit(1)
    
    # 2. Crear .env.example
    create_env_example()
    
    # 3. Información para GitHub
    print("\n" + "="*60)
    print("📌 PRÓXIMOS PASOS")
    print("="*60 + "\n")
    
    print("""
1️⃣  GITHUB
    • Crea cuenta en https://github.com
    • Crea nuevo repositorio: flight-tracker
    • Genera token en Settings > Personal access tokens
    
2️⃣  SUBIR CÓDIGO
    git remote add origin https://github.com/TU_USUARIO/flight-tracker.git
    git branch -M main
    git push -u origin main
    
3️⃣  RENDER
    • Crea cuenta en https://render.com
    • Autentica con GitHub
    • Create Web Service → Selecciona repositorio
    • Configure environment variables
    • Deploy ✅
    
📖 Ver instrucciones completas en:
   GUIA_DEPLOY_GITHUB_RENDER.md
    """)
    
    print("\n✅ SISTEMA LISTO PARA DEPLOY")

if __name__ == "__main__":
    main()
