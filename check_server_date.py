#!/usr/bin/env python3
"""
Script para verificar a data atual que o servidor está usando
"""

import requests
from datetime import datetime, date
import json

# Configurações
BASE_URL = 'http://localhost:5000'
LOGIN_DATA = {
    'email': 'admin@test.com',
    'password': 'admin123'
}

def main():
    print("=== VERIFICANDO DATA DO SERVIDOR ===")
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_response = session.post(f'{BASE_URL}/api/login', json=LOGIN_DATA)
    print(f"Status do login: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("Erro no login!")
        print(login_response.text)
        return
    
    print("Login realizado com sucesso!")
    
    # 2. Verificar data atual do Python
    print(f"\n2. Data atual do Python: {date.today()}")
    print(f"   Datetime atual: {datetime.now()}")
    
    # 3. Testar endpoint de sessões de hoje
    print("\n3. Testando /api/dashboard/sessions/today")
    today_response = session.get(f'{BASE_URL}/api/dashboard/sessions/today')
    print(f"Status: {today_response.status_code}")
    
    if today_response.status_code == 200:
        data = today_response.json()
        print(f"Resposta: {json.dumps(data, indent=2)}")
        if data.get('data'):
            print(f"Encontradas {len(data['data'])} sessões para hoje")
        else:
            print("Nenhuma sessão encontrada para hoje")
    else:
        print(f"Erro: {today_response.text}")
    
    # 4. Testar endpoint de sessões futuras
    print("\n4. Testando /api/dashboard/sessions/upcoming")
    upcoming_response = session.get(f'{BASE_URL}/api/dashboard/sessions/upcoming')
    print(f"Status: {upcoming_response.status_code}")
    
    if upcoming_response.status_code == 200:
        data = upcoming_response.json()
        print(f"Resposta: {json.dumps(data, indent=2)}")
        if data.get('data'):
            print(f"Encontradas {len(data['data'])} sessões futuras")
        else:
            print("Nenhuma sessão futura encontrada")
    else:
        print(f"Erro: {upcoming_response.text}")

if __name__ == '__main__':
    main()