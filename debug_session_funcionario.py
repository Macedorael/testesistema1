#!/usr/bin/env python3
"""
Script para debugar a relação session-funcionario-especialidade na API
"""

import requests
import json

# Configurações
BASE_URL = 'http://localhost:5000'
LOGIN_DATA = {
    'email': 'admin@consultorio.com',
    'password': 'admin123'
}

def main():
    print("=== DEBUGANDO SESSION-FUNCIONARIO-ESPECIALIDADE NA API ===")
    
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
    
    # 2. Testar endpoint de sessões de hoje
    print("\n2. Testando /api/dashboard/sessions/today")
    today_response = session.get(f'{BASE_URL}/api/dashboard/sessions/today')
    print(f"Status: {today_response.status_code}")
    
    if today_response.status_code == 200:
        data = today_response.json()
        print(f"Sucesso: {data.get('success')}")
        sessions = data.get('data', [])
        print(f"Número de sessões: {len(sessions)}")
        
        for i, sess in enumerate(sessions):
            print(f"\n=== SESSÃO {i+1} ===")
            print(f"ID: {sess.get('id')}")
            print(f"Funcionário Nome: {sess.get('funcionario_nome')}")
            print(f"Funcionário ID: {sess.get('funcionario_id')}")
            print(f"Funcionário Especialidade: {sess.get('funcionario_especialidade')}")
            print(f"Especialidade Nome: {sess.get('especialidade_nome')}")
            print(f"Psychologist Name: {sess.get('psychologist_name')}")
            
            # Verificar se tem os campos esperados
            has_especialidade_nome = 'especialidade_nome' in sess
            has_funcionario_especialidade = 'funcionario_especialidade' in sess
            
            print(f"Tem 'especialidade_nome': {has_especialidade_nome}")
            print(f"Tem 'funcionario_especialidade': {has_funcionario_especialidade}")
            
            if not has_especialidade_nome:
                print("❌ Campo 'especialidade_nome' AUSENTE!")
            else:
                print(f"✅ Campo 'especialidade_nome': {sess.get('especialidade_nome')}")
    else:
        print(f"Erro: {today_response.text}")

if __name__ == '__main__':
    main()