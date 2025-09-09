#!/usr/bin/env python3
"""
Script para testar a API de especialidades em produção
"""

import requests
import json
import sys
from datetime import datetime

def test_production_api():
    """Testa a API de especialidades em produção"""
    
    # URLs para testar
    base_urls = [
        'https://consultorio-psicologia.onrender.com',
        'http://localhost:5000'  # Para comparação local
    ]
    
    print("🔍 TESTE DA API DE ESPECIALIDADES")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\n📍 Testando: {base_url}")
        print("-" * 30)
        
        try:
            # Teste 1: Verificar se o servidor está respondendo
            print("1. Testando conectividade...")
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            # Teste 2: Testar API de especialidades sem autenticação
            print("\n2. Testando API especialidades (sem auth)...")
            api_response = requests.get(f"{base_url}/api/especialidades", timeout=10)
            print(f"   Status: {api_response.status_code}")
            print(f"   Content-Type: {api_response.headers.get('content-type', 'N/A')}")
            
            if api_response.status_code == 401:
                print("   ✅ Resposta esperada: 401 (não autenticado)")
            else:
                print(f"   ⚠️  Resposta inesperada: {api_response.status_code}")
                try:
                    content = api_response.json()
                    print(f"   Conteúdo: {json.dumps(content, indent=2)}")
                except:
                    print(f"   Conteúdo (texto): {api_response.text[:200]}...")
            
            # Teste 3: Verificar se há erros de CORS
            print("\n3. Testando CORS...")
            cors_headers = {
                'Origin': 'https://consultorio-psicologia.onrender.com',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            cors_response = requests.options(f"{base_url}/api/especialidades", 
                                           headers=cors_headers, timeout=10)
            print(f"   Status: {cors_response.status_code}")
            print(f"   CORS Headers: {dict(cors_response.headers)}")
            
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT: Servidor não respondeu em 10 segundos")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONEXÃO: Não foi possível conectar ao servidor")
        except Exception as e:
            print(f"   ❌ ERRO: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    print("- Se localhost funciona mas produção não, pode ser problema de deploy")
    print("- Se ambos retornam 401, a API está funcionando (precisa de autenticação)")
    print("- Se há timeout em produção, pode ser problema de cold start no Render")
    print("- Verifique os logs do Render para mais detalhes")

if __name__ == '__main__':
    test_production_api()