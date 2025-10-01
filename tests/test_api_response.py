#!/usr/bin/env python3
"""
Script para testar diretamente as respostas da API do dashboard
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    base_url = "http://localhost:5000"
    
    print("=== TESTANDO ENDPOINTS DA API ===\n")
    
    # Teste 1: Sessões de hoje
    print("1. Testando /api/dashboard/sessions/today")
    try:
        response = requests.get(f"{base_url}/api/dashboard/sessions/today")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Dados retornados: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar se há sessões e se têm especialidade
            if data.get('sessions'):
                for session in data['sessions']:
                    funcionario_nome = session.get('funcionario_nome', 'N/A')
                    especialidade = session.get('funcionario_especialidade', 'N/A')
                    print(f"  - Funcionário: {funcionario_nome}, Especialidade: {especialidade}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Próximas sessões
    print("2. Testando /api/dashboard/sessions/upcoming")
    try:
        response = requests.get(f"{base_url}/api/dashboard/sessions/upcoming?limit=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Dados retornados: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Verificar se há sessões e se têm especialidade
            if data.get('sessions'):
                for session in data['sessions']:
                    funcionario_nome = session.get('funcionario_nome', 'N/A')
                    especialidade = session.get('funcionario_especialidade', 'N/A')
                    print(f"  - Funcionário: {funcionario_nome}, Especialidade: {especialidade}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_api_endpoints()