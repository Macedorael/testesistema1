#!/usr/bin/env python3
"""
Teste de isolamento em produção
Verifica se usuários diferentes conseguem ver dados uns dos outros
"""

import requests
import json

def test_production_isolation():
    """Testa isolamento entre usuários em produção"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== TESTE DE ISOLAMENTO EM PRODUÇÃO ===")
    
    # Credenciais dos usuários
    user1 = {"email": "teste@email.com", "password": "123456"}
    user2 = {"email": "teste2@email.com", "password": "123456"}
    
    sessions = {}
    
    # Login dos usuários
    print("\n1. Fazendo login dos usuários...")
    for i, user in enumerate([user1, user2], 1):
        session = requests.Session()
        
        # Login
        login_response = session.post(f"{base_url}/api/login", json=user)
        if login_response.status_code == 200:
            print(f"   ✓ Usuário {i} ({user['email']}) logado com sucesso")
            sessions[f"user{i}"] = session
        else:
            print(f"   ✗ Erro no login do usuário {i}: {login_response.status_code}")
            return
    
    # Testar especialidades
    print("\n2. Testando isolamento de especialidades...")
    
    especialidades_user1 = sessions["user1"].get(f"{base_url}/api/especialidades")
    especialidades_user2 = sessions["user2"].get(f"{base_url}/api/especialidades")
    
    if especialidades_user1.status_code == 200 and especialidades_user2.status_code == 200:
        try:
            esp1_data = especialidades_user1.json()
            esp2_data = especialidades_user2.json()
        except:
            print(f"   ✗ Erro ao decodificar JSON das especialidades")
            print(f"   User1 response: {especialidades_user1.text[:200]}")
            print(f"   User2 response: {especialidades_user2.text[:200]}")
            return
        
        # Extrair lista de especialidades da resposta
        if isinstance(esp1_data, dict) and 'especialidades' in esp1_data:
            esp1_data = esp1_data['especialidades']
        if isinstance(esp2_data, dict) and 'especialidades' in esp2_data:
            esp2_data = esp2_data['especialidades']
        
        # Verificar se é lista
        if not isinstance(esp1_data, list) or not isinstance(esp2_data, list):
            print(f"   ✗ Resposta não é uma lista")
            print(f"   User1 type: {type(esp1_data)}, data: {str(esp1_data)[:200]}")
            print(f"   User2 type: {type(esp2_data)}, data: {str(esp2_data)[:200]}")
            return
        
        print(f"   Usuário 1 vê {len(esp1_data)} especialidades")
        print(f"   Usuário 2 vê {len(esp2_data)} especialidades")
        
        # Verificar se há sobreposição de IDs
        ids_user1 = {esp['id'] for esp in esp1_data}
        ids_user2 = {esp['id'] for esp in esp2_data}
        overlap = ids_user1.intersection(ids_user2)
        
        if overlap:
            print(f"   ⚠️  PROBLEMA: Especialidades compartilhadas (IDs: {overlap})")
            for esp in esp1_data:
                if esp['id'] in overlap:
                    print(f"      - ID {esp['id']}: '{esp['nome']}' (User_ID: {esp.get('user_id', 'N/A')})")
        else:
            print("   ✓ Isolamento de especialidades OK - nenhuma sobreposição")
        
        # Mostrar detalhes
        print("\n   Detalhes das especialidades:")
        print(f"   Usuário 1 ({user1['email']}):")
        for esp in esp1_data[:3]:  # Mostrar apenas 3 primeiras
            print(f"      - ID {esp['id']}: '{esp['nome']}' (User_ID: {esp.get('user_id', 'N/A')})")
        
        print(f"   Usuário 2 ({user2['email']}):")
        for esp in esp2_data[:3]:  # Mostrar apenas 3 primeiras
            print(f"      - ID {esp['id']}: '{esp['nome']}' (User_ID: {esp.get('user_id', 'N/A')})")
    
    else:
        print(f"   ✗ Erro ao buscar especialidades: User1={especialidades_user1.status_code}, User2={especialidades_user2.status_code}")
    
    # Testar funcionários
    print("\n3. Testando isolamento de funcionários...")
    
    funcionarios_user1 = sessions["user1"].get(f"{base_url}/api/funcionarios")
    funcionarios_user2 = sessions["user2"].get(f"{base_url}/api/funcionarios")
    
    if funcionarios_user1.status_code == 200 and funcionarios_user2.status_code == 200:
        try:
            func1_data = funcionarios_user1.json()
            func2_data = funcionarios_user2.json()
        except:
            print(f"   ✗ Erro ao decodificar JSON dos funcionários")
            print(f"   User1 response: {funcionarios_user1.text[:200]}")
            print(f"   User2 response: {funcionarios_user2.text[:200]}")
            return
        
        # Extrair lista de funcionários da resposta
        if isinstance(func1_data, dict) and 'funcionarios' in func1_data:
            func1_data = func1_data['funcionarios']
        if isinstance(func2_data, dict) and 'funcionarios' in func2_data:
            func2_data = func2_data['funcionarios']
        
        # Verificar se é lista
        if not isinstance(func1_data, list) or not isinstance(func2_data, list):
            print(f"   ✗ Resposta não é uma lista")
            print(f"   User1 type: {type(func1_data)}, data: {str(func1_data)[:200]}")
            print(f"   User2 type: {type(func2_data)}, data: {str(func2_data)[:200]}")
            return
        
        print(f"   Usuário 1 vê {len(func1_data)} funcionários")
        print(f"   Usuário 2 vê {len(func2_data)} funcionários")
        
        # Verificar se há sobreposição de IDs
        ids_user1 = {func['id'] for func in func1_data}
        ids_user2 = {func['id'] for func in func2_data}
        overlap = ids_user1.intersection(ids_user2)
        
        if overlap:
            print(f"   ⚠️  PROBLEMA: Funcionários compartilhados (IDs: {overlap})")
            for func in func1_data:
                if func['id'] in overlap:
                    print(f"      - ID {func['id']}: '{func['nome']}' (User_ID: {func.get('user_id', 'N/A')})")
        else:
            print("   ✓ Isolamento de funcionários OK - nenhuma sobreposição")
        
        # Mostrar detalhes
        print("\n   Detalhes dos funcionários:")
        print(f"   Usuário 1 ({user1['email']}):")
        for func in func1_data[:3]:  # Mostrar apenas 3 primeiros
            print(f"      - ID {func['id']}: '{func['nome']}' (User_ID: {func.get('user_id', 'N/A')})")
        
        print(f"   Usuário 2 ({user2['email']}):")
        for func in func2_data[:3]:  # Mostrar apenas 3 primeiros
            print(f"      - ID {func['id']}: '{func['nome']}' (User_ID: {func.get('user_id', 'N/A')})")
    
    else:
        print(f"   ✗ Erro ao buscar funcionários: User1={funcionarios_user1.status_code}, User2={funcionarios_user2.status_code}")
    
    # Testar criação de especialidade com mesmo nome
    print("\n4. Testando criação de especialidades com mesmo nome...")
    
    test_especialidade = {
        "nome": "Teste Isolamento Produção",
        "descricao": "Teste para verificar isolamento"
    }
    
    # Criar especialidade para usuário 1
    create1 = sessions["user1"].post(f"{base_url}/api/especialidades", json=test_especialidade)
    if create1.status_code == 201:
        print("   ✓ Usuário 1 criou especialidade com sucesso")
        esp1_id = create1.json().get('id')
        
        # Tentar criar especialidade com mesmo nome para usuário 2
        create2 = sessions["user2"].post(f"{base_url}/api/especialidades", json=test_especialidade)
        if create2.status_code == 201:
            print("   ✓ Usuário 2 também criou especialidade com mesmo nome - ISOLAMENTO OK!")
            esp2_id = create2.json().get('id')
            
            # Limpar especialidades de teste
            sessions["user1"].delete(f"{base_url}/api/especialidades/{esp1_id}")
            sessions["user2"].delete(f"{base_url}/api/especialidades/{esp2_id}")
            print("   ✓ Especialidades de teste removidas")
        else:
            print(f"   ✗ Usuário 2 não conseguiu criar especialidade: {create2.status_code}")
            # Limpar especialidade do usuário 1
            sessions["user1"].delete(f"{base_url}/api/especialidades/{esp1_id}")
    else:
        print(f"   ✗ Usuário 1 não conseguiu criar especialidade: {create1.status_code}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == '__main__':
    test_production_isolation()