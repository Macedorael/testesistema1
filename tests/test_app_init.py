#!/usr/bin/env python3
"""
Script para testar a inicialização da aplicação
"""

import os
import sys
from io import StringIO

def test_app_initialization():
    """Testa a inicialização da aplicação capturando logs"""
    
    print("🚀 TESTE DE INICIALIZAÇÃO DA APLICAÇÃO")
    print("=" * 50)
    
    # Capturar stdout para ver os logs de debug
    old_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        print("\n1. Testando importação do main.py...")
        sys.stdout = old_stdout  # Restaurar para mostrar esta mensagem
        
        # Capturar novamente para os logs de importação
        sys.stdout = captured_output
        
        # Importar o módulo main (isso executará todos os prints de debug)
        from src.main import app
        
        # Restaurar stdout
        sys.stdout = old_stdout
        
        # Mostrar os logs capturados
        output = captured_output.getvalue()
        print("\n📋 LOGS DE INICIALIZAÇÃO:")
        print("-" * 30)
        for line in output.split('\n'):
            if line.strip():
                if '[ERROR]' in line:
                    print(f"❌ {line}")
                elif '[DEBUG]' in line:
                    print(f"✅ {line}")
                else:
                    print(f"ℹ️  {line}")
        
        print("\n2. Testando rotas registradas...")
        print("-" * 30)
        
        # Listar todas as rotas registradas
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        # Filtrar rotas da API
        api_routes = [r for r in routes if r['rule'].startswith('/api')]
        
        print(f"Total de rotas: {len(routes)}")
        print(f"Rotas da API: {len(api_routes)}")
        
        print("\n📍 ROTAS DA API REGISTRADAS:")
        for route in sorted(api_routes, key=lambda x: x['rule']):
            methods = [m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']]
            print(f"   {route['rule']} -> {methods} ({route['endpoint']})")
        
        # Verificar rotas específicas que estão falhando
        critical_routes = ['/api/login', '/api/especialidades', '/api/funcionarios']
        print("\n🔍 VERIFICAÇÃO DE ROTAS CRÍTICAS:")
        for critical_route in critical_routes:
            found = any(r['rule'] == critical_route for r in api_routes)
            status = "✅ ENCONTRADA" if found else "❌ NÃO ENCONTRADA"
            print(f"   {critical_route}: {status}")
        
        print("\n3. Testando configuração da aplicação...")
        print("-" * 30)
        print(f"   Debug mode: {app.debug}")
        print(f"   Testing mode: {app.testing}")
        print(f"   Environment: {os.environ.get('FLASK_ENV', 'não definido')}")
        print(f"   Database URL: {os.environ.get('DATABASE_URL', 'não definido')[:50]}...")
        
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ ERRO durante inicialização: {str(e)}")
        print(f"Tipo do erro: {type(e).__name__}")
        
        # Mostrar logs capturados mesmo em caso de erro
        output = captured_output.getvalue()
        if output:
            print("\n📋 LOGS CAPTURADOS ANTES DO ERRO:")
            print("-" * 30)
            for line in output.split('\n'):
                if line.strip():
                    if '[ERROR]' in line:
                        print(f"❌ {line}")
                    elif '[DEBUG]' in line:
                        print(f"✅ {line}")
                    else:
                        print(f"ℹ️  {line}")
    
    print("\n" + "=" * 50)
    print("📊 DIAGNÓSTICO")
    print("=" * 50)
    print("- Se há erros de importação: problema de dependências ou sintaxe")
    print("- Se rotas críticas não estão registradas: problema no blueprint")
    print("- Se tudo parece OK: problema pode ser específico do ambiente Render")

if __name__ == '__main__':
    test_app_initialization()