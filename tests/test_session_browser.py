#!/usr/bin/env python3
import requests
import json

# URL base do servidor
BASE_URL = "http://localhost:5000"

def test_login_and_session():
    """Testa o login e verifica se a sessão é mantida"""
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    
    print("1. Testando login...")
    
    # Fazer login
    login_data = {
        "email": "oi@oii.com",
        "password": "123456"
    }
    
    login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"Status do login: {login_response.status_code}")
    print(f"Resposta do login: {login_response.text}")
    
    if login_response.status_code == 200:
        print("✅ Login bem-sucedido!")
        
        # Verificar cookies recebidos
        print(f"Cookies recebidos: {session.cookies}")
        
        print("\n2. Testando /api/me...")
        me_response = session.get(f"{BASE_URL}/api/me")
        print(f"Status /api/me: {me_response.status_code}")
        print(f"Resposta /api/me: {me_response.text}")
        
        print("\n3. Testando /api/subscriptions/my-subscription...")
        subscription_response = session.get(f"{BASE_URL}/api/subscriptions/my-subscription")
        print(f"Status subscription: {subscription_response.status_code}")
        print(f"Resposta subscription: {subscription_response.text}")
        
        if subscription_response.status_code == 200:
            data = subscription_response.json()
            if data.get('success') and data.get('subscription'):
                print("✅ Assinatura encontrada!")
                sub = data['subscription']
                print(f"   Plano: {sub.get('plan_type')}")
                print(f"   Status: {sub.get('status')}")
                print(f"   Ativo: {sub.get('is_active')}")
                print(f"   Dias restantes: {sub.get('days_remaining')}")
            else:
                print("❌ Nenhuma assinatura ativa encontrada")
        else:
            print("❌ Erro ao buscar assinatura")
    else:
        print("❌ Falha no login")

if __name__ == "__main__":
    test_login_and_session()