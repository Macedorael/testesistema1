#!/usr/bin/env python3
"""
Script para testar as APIs com autenticação
"""

import requests
import json
from datetime import datetime

def test_api_with_auth():
    base_url = "http://localhost:5000"
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    
    print("=== TESTANDO APIS COM AUTENTICAÇÃO ===\n")
    
    # Primeiro, fazer login
    print("1. Fazendo login...")
    login_data = {
        "email": "admin@consultorio.com",
        "password": "admin123"
    }
    
    try:
        login_response = session.post(f"{base_url}/api/login", json=login_data)
        print(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Erro no login: {login_response.text}")
            return
        
        print("Login realizado com sucesso!\n")
        
        # Teste 2: Sessões de hoje
        print("2. Testando /api/dashboard/sessions/today")
        response = session.get(f"{base_url}/api/dashboard/sessions/today")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Dados retornados: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar se há sessões e se têm especialidade
            if data.get('sessions'):
                print("\nAnálise das sessões:")
                for i, session_data in enumerate(data['sessions'], 1):
                    funcionario_nome = session_data.get('funcionario_nome', 'N/A')
                    especialidade = session_data.get('funcionario_especialidade', 'N/A')
                    print(f"  Sessão {i}: Funcionário: {funcionario_nome}, Especialidade: {especialidade}")
            else:
                print("Nenhuma sessão encontrada para hoje")
        else:
            print(f"Erro: {response.text}")
        
        print("\n" + "="*50 + "\n")
        
        # Teste 3: Próximas sessões
        print("3. Testando /api/dashboard/sessions/upcoming")
        response = session.get(f"{base_url}/api/dashboard/sessions/upcoming?limit=10")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Dados retornados: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar se há sessões e se têm especialidade
            if data.get('sessions'):
                print("\nAnálise das próximas sessões:")
                for i, session_data in enumerate(data['sessions'], 1):
                    funcionario_nome = session_data.get('funcionario_nome', 'N/A')
                    especialidade = session_data.get('funcionario_especialidade', 'N/A')
                    print(f"  Sessão {i}: Funcionário: {funcionario_nome}, Especialidade: {especialidade}")
            else:
                print("Nenhuma próxima sessão encontrada")
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_api_with_auth()