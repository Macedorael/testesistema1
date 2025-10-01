#!/usr/bin/env python3
"""
Script para debugar a resposta da API das sessões de hoje
"""

import requests
import json
from pprint import pprint

def debug_api_response():
    print("=== DEBUGANDO RESPOSTA DA API ===\n")
    
    # URL base
    base_url = "http://localhost:5000"
    
    # Fazer login
    login_data = {
        "email": "admin@consultorio.com",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    print("1. Fazendo login...")
    login_response = session.post(f"{base_url}/api/login", json=login_data)
    print(f"Status do login: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("Erro no login!")
        return
    
    print("Login realizado com sucesso!\n")
    
    # Testar API das sessões de hoje
    print("2. Testando /api/dashboard/sessions/today")
    today_response = session.get(f"{base_url}/api/dashboard/sessions/today")
    print(f"Status: {today_response.status_code}")
    
    if today_response.status_code == 200:
        data = today_response.json()
        print("Estrutura da resposta:")
        pprint(data, width=120)
        
        if data.get('data') and len(data['data']) > 0:
            print("\n=== CAMPOS DA PRIMEIRA SESSÃO ===")
            first_session = data['data'][0]
            for key, value in first_session.items():
                print(f"{key}: {value}")
        else:
            print("Nenhuma sessão encontrada")
    else:
        print(f"Erro: {today_response.text}")

if __name__ == "__main__":
    debug_api_response()