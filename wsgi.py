#!/usr/bin/env python3
"""
WSGI entry point for Gunicorn
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Executar correções automáticas na inicialização
try:
    from auto_fix_on_startup import auto_fix_isolation
    print("[STARTUP] Executando verificação automática de isolamento...")
    auto_fix_isolation()
except Exception as e:
    print(f"[STARTUP] Aviso: Erro na verificação automática: {e}")
    print("[STARTUP] Continuando inicialização...")

# Import the Flask app
from src.main import app

if __name__ == "__main__":
    app.run()