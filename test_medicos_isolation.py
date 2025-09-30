#!/usr/bin/env python3
"""
Script para testar o isolamento de dados no endpoint /medicos
Verifica se cada usuário vê apenas seus próprios funcionários
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:5000"

def test_medicos_isolation():
    """Testa o isolamento de dados no endpoint /medicos"""
    
    print("=== TESTE DE ISOLAMENTO - ENDPOINT /medicos ===\n")
    
    # Dados de teste para dois usuários diferentes
    users = [
        {"email": "admin@admin.com", "password": "admin123", "name": "Admin"},
        {"email": "teste@teste.com", "password": "teste123", "name": "Teste"}
    ]
    
    sessions = {}
    
    # 1. Fazer login com cada usuário
    for user in users:
        print(f"🔐 Fazendo login com {user['name']} ({user['email']})...")
        
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/login", json=login_data)
            
            if response.status_code == 200:
                # Extrair cookies da sessão
                session_cookie = response.cookies.get('session')
                if session_cookie:
                    sessions[user['name']] = {'session': session_cookie}
                    print(f"✅ Login bem-sucedido para {user['name']}")
                else:
                    print(f"❌ Erro: Cookie de sessão não encontrado para {user['name']}")
                    return
            else:
                print(f"❌ Erro no login para {user['name']}: {response.status_code}")
                print(f"Resposta: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Erro de conexão no login para {user['name']}: {str(e)}")
            return
    
    print("\n" + "="*50)
    
    # 2. Testar endpoint /medicos para cada usuário
    for user_name, session_data in sessions.items():
        print(f"\n🏥 Testando /medicos para {user_name}...")
        
        cookies = {'session': session_data['session']}
        
        try:
            response = requests.get(f"{BASE_URL}/api/medicos", cookies=cookies)
            
            if response.status_code == 200:
                medicos = response.json()
                print(f"✅ Resposta recebida para {user_name}")
                print(f"📊 Quantidade de médicos/funcionários: {len(medicos)}")
                
                if medicos:
                    print(f"👥 Lista de funcionários para {user_name}:")
                    for i, medico in enumerate(medicos, 1):
                        print(f"   {i}. ID: {medico.get('id')}, Nome: {medico.get('nome')}, Especialidade: {medico.get('especialidade')}")
                else:
                    print(f"📝 Nenhum funcionário encontrado para {user_name}")
                
                # Armazenar para comparação
                sessions[user_name]['medicos'] = medicos
                
            else:
                print(f"❌ Erro ao buscar médicos para {user_name}: {response.status_code}")
                print(f"Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro de conexão ao buscar médicos para {user_name}: {str(e)}")
    
    print("\n" + "="*50)
    
    # 3. Análise de isolamento
    print("\n🔍 ANÁLISE DE ISOLAMENTO:")
    
    user_names = list(sessions.keys())
    if len(user_names) >= 2:
        user1, user2 = user_names[0], user_names[1]
        
        medicos1 = sessions[user1].get('medicos', [])
        medicos2 = sessions[user2].get('medicos', [])
        
        # Verificar se há sobreposição de IDs
        ids1 = {medico['id'] for medico in medicos1}
        ids2 = {medico['id'] for medico in medicos2}
        
        overlap = ids1.intersection(ids2)
        
        if overlap:
            print(f"❌ VAZAMENTO DETECTADO!")
            print(f"   {user1} e {user2} compartilham funcionários com IDs: {overlap}")
            print(f"   Isso indica que o isolamento de dados NÃO está funcionando!")
        else:
            print(f"✅ ISOLAMENTO OK!")
            print(f"   {user1} e {user2} não compartilham funcionários.")
            print(f"   Cada usuário vê apenas seus próprios dados.")
        
        print(f"\n📈 Resumo:")
        print(f"   - {user1}: {len(medicos1)} funcionários")
        print(f"   - {user2}: {len(medicos2)} funcionários")
        print(f"   - IDs compartilhados: {len(overlap)}")
    
    print("\n" + "="*50)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_medicos_isolation()