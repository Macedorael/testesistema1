#!/usr/bin/env python3
"""
Script para testar todas as rotas disponíveis
"""

import requests
import json
import sys
from datetime import datetime

def test_routes():
    """Testa as principais rotas da aplicação"""
    
    # URLs para testar
    base_urls = [
        'https://consultorio-psicologia.onrender.com',
        'http://localhost:5000'  # Para comparação local
    ]
    
    # Rotas para testar
    test_routes = [
        ('GET', '/'),
        ('GET', '/api'),
        ('POST', '/api/login'),
        ('GET', '/api/especialidades'),
        ('GET', '/api/funcionarios'),
        ('GET', '/api/users'),
        ('OPTIONS', '/api/login'),
        ('OPTIONS', '/api/especialidades')
    ]
    
    print("🔍 TESTE DE ROTAS DISPONÍVEIS")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\n📍 Testando: {base_url}")
        print("-" * 30)
        
        for method, route in test_routes:
            try:
                print(f"\n{method} {route}")
                
                if method == 'GET':
                    response = requests.get(f"{base_url}{route}", timeout=10)
                elif method == 'POST':
                    # Para POST, enviar dados vazios
                    response = requests.post(f"{base_url}{route}", 
                                           json={}, timeout=10)
                elif method == 'OPTIONS':
                    response = requests.options(f"{base_url}{route}", timeout=10)
                
                print(f"   Status: {response.status_code}")
                
                # Mostrar informações relevantes baseadas no status
                if response.status_code == 404:
                    print(f"   ❌ ROTA NÃO ENCONTRADA")
                elif response.status_code == 401:
                    print(f"   🔒 Requer autenticação (esperado)")
                elif response.status_code == 400:
                    print(f"   ⚠️  Bad Request (pode ser esperado para POST vazio)")
                elif response.status_code == 200:
                    print(f"   ✅ OK")
                elif response.status_code == 405:
                    print(f"   ⚠️  Método não permitido")
                else:
                    print(f"   ℹ️  Status: {response.status_code}")
                
                # Mostrar content-type se disponível
                content_type = response.headers.get('content-type', '')
                if content_type:
                    print(f"   Content-Type: {content_type}")
                
                # Para respostas pequenas, mostrar o conteúdo
                if len(response.text) < 200 and response.status_code != 200:
                    try:
                        if 'application/json' in content_type:
                            data = response.json()
                            print(f"   Resposta: {json.dumps(data, indent=2)}")
                        else:
                            print(f"   Resposta: {response.text}")
                    except:
                        print(f"   Resposta (texto): {response.text[:100]}...")
                        
            except requests.exceptions.Timeout:
                print(f"   ❌ TIMEOUT")
            except requests.exceptions.ConnectionError:
                print(f"   ❌ CONEXÃO FALHOU")
            except Exception as e:
                print(f"   ❌ ERRO: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 ANÁLISE")
    print("=" * 50)
    print("- 404 em produção mas não local = problema de deploy/configuração")
    print("- 401 = rota existe mas requer autenticação (bom sinal)")
    print("- 400 para POST vazio = rota existe mas dados inválidos (normal)")
    print("- Timeout = problema de conectividade ou cold start")

if __name__ == '__main__':
    test_routes()