#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar logs detalhados das rotas de funcionários e especialidades
"""

import requests
import json
import logging

# Configurar logging para capturar tudo
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

BASE_URL = "http://localhost:5000"

def test_routes_with_logs():
    """Testa as rotas com logs detalhados"""
    print("🔍 TESTANDO ROTAS COM LOGS DETALHADOS")
    print("=" * 60)
    
    # Primeiro, tentar fazer login para obter sessão
    login_data = {
        "email": "admin@teste.com",
        "password": "123456"
    }
    
    session = requests.Session()
    
    print("\n1. Tentando fazer login...")
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"   Status: {login_response.status_code}")
        print(f"   Resposta: {login_response.text[:200]}...")
        
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print("   ❌ Falha no login - testando sem autenticação")
    except Exception as e:
        print(f"   ❌ Erro no login: {e}")
    
    print("\n2. Testando rota de funcionários...")
    try:
        func_response = session.get(f"{BASE_URL}/api/funcionarios")
        print(f"   Status: {func_response.status_code}")
        print(f"   Headers: {dict(func_response.headers)}")
        print(f"   Resposta: {func_response.text}")
        
        if func_response.status_code == 200:
            try:
                data = func_response.json()
                print(f"   ✅ JSON válido: {len(data.get('funcionarios', []))} funcionários")
            except:
                print("   ⚠️ Resposta não é JSON válido")
        else:
            print(f"   ❌ Erro na rota de funcionários")
    except Exception as e:
        print(f"   ❌ Erro ao acessar funcionários: {e}")
    
    print("\n3. Testando rota de especialidades...")
    try:
        esp_response = session.get(f"{BASE_URL}/api/especialidades")
        print(f"   Status: {esp_response.status_code}")
        print(f"   Headers: {dict(esp_response.headers)}")
        print(f"   Resposta: {esp_response.text}")
        
        if esp_response.status_code == 200:
            try:
                data = esp_response.json()
                print(f"   ✅ JSON válido: {len(data.get('especialidades', []))} especialidades")
            except:
                print("   ⚠️ Resposta não é JSON válido")
        else:
            print(f"   ❌ Erro na rota de especialidades")
    except Exception as e:
        print(f"   ❌ Erro ao acessar especialidades: {e}")
    
    print("\n" + "=" * 60)
    print("📋 INSTRUÇÕES:")
    print("1. Verifique os logs do servidor (terminal onde roda python wsgi.py)")
    print("2. Procure por mensagens com [FUNCIONARIOS] e [ESPECIALIDADES]")
    print("3. Os logs mostrarão exatamente onde está ocorrendo o erro")
    print("4. Em produção, esses logs aparecerão nos logs do Render")

if __name__ == "__main__":
    test_routes_with_logs()