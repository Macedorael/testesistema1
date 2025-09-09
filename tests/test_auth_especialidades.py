#!/usr/bin/env python3
"""
Script para testar autenticação e acesso às especialidades
"""

import requests
import json
import sys
from datetime import datetime

def test_auth_and_especialidades():
    """Testa autenticação e acesso às especialidades"""
    
    # URLs para testar
    base_urls = [
        'https://consultorio-psicologia.onrender.com',
        'http://localhost:5000'  # Para comparação local
    ]
    
    # Credenciais de teste (usuário admin padrão)
    test_credentials = {
        'email': 'admin@consultorio.com',
        'password': 'admin123'
    }
    
    print("🔐 TESTE DE AUTENTICAÇÃO E ESPECIALIDADES")
    print("=" * 60)
    
    for base_url in base_urls:
        print(f"\n📍 Testando: {base_url}")
        print("-" * 40)
        
        session = requests.Session()
        
        try:
            # Teste 1: Login
            print("1. Testando login...")
            login_response = session.post(
                f"{base_url}/api/login",
                json=test_credentials,
                timeout=15
            )
            print(f"   Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"   ✅ Login bem-sucedido")
                print(f"   Resposta: {json.dumps(login_data, indent=2)}")
                
                # Teste 2: Acessar especialidades com autenticação
                print("\n2. Testando acesso às especialidades...")
                esp_response = session.get(
                    f"{base_url}/api/especialidades",
                    timeout=15
                )
                print(f"   Status: {esp_response.status_code}")
                
                if esp_response.status_code == 200:
                    esp_data = esp_response.json()
                    print(f"   ✅ Especialidades carregadas com sucesso")
                    print(f"   Formato da resposta: {type(esp_data)}")
                    
                    if isinstance(esp_data, dict):
                        print(f"   Chaves: {list(esp_data.keys())}")
                        if 'success' in esp_data:
                            print(f"   Success: {esp_data.get('success')}")
                        if 'especialidades' in esp_data:
                            especialidades = esp_data.get('especialidades', [])
                            print(f"   Número de especialidades: {len(especialidades)}")
                            if especialidades:
                                print(f"   Primeira especialidade: {especialidades[0]}")
                    elif isinstance(esp_data, list):
                        print(f"   Número de especialidades: {len(esp_data)}")
                        if esp_data:
                            print(f"   Primeira especialidade: {esp_data[0]}")
                else:
                    print(f"   ❌ Erro ao carregar especialidades: {esp_response.status_code}")
                    try:
                        error_data = esp_response.json()
                        print(f"   Erro: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"   Erro (texto): {esp_response.text[:200]}...")
                        
            else:
                print(f"   ❌ Falha no login: {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    print(f"   Erro: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Erro (texto): {login_response.text[:200]}...")
                    
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT: Servidor não respondeu em 15 segundos")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONEXÃO: Não foi possível conectar ao servidor")
        except Exception as e:
            print(f"   ❌ ERRO: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 DIAGNÓSTICO")
    print("=" * 60)
    print("- Se login falha: problema de credenciais ou banco de dados")
    print("- Se login funciona mas especialidades falham: problema de autorização")
    print("- Se funciona local mas não em produção: problema de deploy/configuração")
    print("- Se especialidades retornam vazio: problema de dados ou isolamento")

if __name__ == '__main__':
    test_auth_and_especialidades()