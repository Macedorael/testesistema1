#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys

def testar_sistema():
    base_url = 'http://localhost:5000'
    
    print("🧪 TESTANDO SISTEMA DO CONSULTÓRIO")
    print("=" * 50)
    
    # Rotas para testar - divididas por categoria
    rotas_frontend = [
        ('/', 'Página Principal'),
        ('/inicial.html', 'Página Inicial'),
        ('/entrar.html', 'Página de Login'),
        ('/index.html', 'Dashboard'),
        ('/funcionarios.html', 'Página Funcionários'),
        ('/especialidades.html', 'Página Especialidades'),
    ]
    
    rotas_api = [
        ('/api/users/check-session', 'Verificar Sessão'),
        ('/api/patients', 'API Pacientes'),
        ('/api/funcionarios', 'API Funcionários'),
        ('/api/especialidades', 'API Especialidades'),
        ('/api/appointments', 'API Consultas'),
        ('/api/payments', 'API Pagamentos'),
        ('/api/dashboard/stats', 'API Dashboard'),
    ]
    
    print("\n📄 TESTANDO PÁGINAS FRONTEND:")
    print("-" * 50)
    
    frontend_ok = 0
    for rota, nome in rotas_frontend:
        try:
            response = requests.get(f'{base_url}{rota}', timeout=5)
            status = response.status_code
            
            if status == 200:
                resultado = "✅ OK"
                frontend_ok += 1
            elif status == 302:
                resultado = "🔄 REDIRECT"
                frontend_ok += 1
            elif status == 404:
                resultado = "❌ NÃO ENCONTRADA"
            else:
                resultado = f"⚠️  STATUS {status}"
                
            print(f"{nome:20} {rota:20} {resultado}")
            
        except requests.exceptions.ConnectionError:
            print(f"{nome:20} {rota:20} ❌ SERVIDOR OFFLINE")
        except Exception as e:
            print(f"{nome:20} {rota:20} ❌ ERRO: {str(e)[:20]}")
    
    print("\n🔌 TESTANDO APIs:")
    print("-" * 50)
    
    api_ok = 0
    for rota, nome in rotas_api:
        try:
            response = requests.get(f'{base_url}{rota}', timeout=5)
            status = response.status_code
            
            if status in [200, 401, 403]:  # 401/403 são OK para APIs que precisam de auth
                resultado = "✅ OK" if status == 200 else f"🔐 AUTH ({status})"
                api_ok += 1
            elif status == 404:
                resultado = "❌ NÃO ENCONTRADA"
            elif status == 405:
                resultado = "⚠️  MÉTODO NÃO PERMITIDO"
                api_ok += 1  # Endpoint existe, só não aceita GET
            else:
                resultado = f"⚠️  STATUS {status}"
                
            print(f"{nome:20} {rota:25} {resultado}")
            
        except requests.exceptions.ConnectionError:
            print(f"{nome:20} {rota:25} ❌ SERVIDOR OFFLINE")
        except Exception as e:
            print(f"{nome:20} {rota:25} ❌ ERRO: {str(e)[:20]}")
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    
    total_frontend = len(rotas_frontend)
    total_api = len(rotas_api)
    total_geral = total_frontend + total_api
    total_ok = frontend_ok + api_ok
    
    print(f"📄 Frontend: {frontend_ok}/{total_frontend} funcionando")
    print(f"🔌 APIs: {api_ok}/{total_api} funcionando")
    print(f"📈 Total: {total_ok}/{total_geral} funcionando")
    
    # Calcular porcentagem
    porcentagem = (total_ok / total_geral) * 100 if total_geral > 0 else 0
    
    print(f"\n📊 Taxa de sucesso: {porcentagem:.1f}%")
    
    if porcentagem >= 80:
        print("\n🎉 SISTEMA FUNCIONANDO MUITO BEM!")
    elif porcentagem >= 60:
        print("\n✅ SISTEMA FUNCIONANDO ADEQUADAMENTE")
    elif porcentagem >= 40:
        print("\n⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
    else:
        print("\n🚨 SISTEMA COM PROBLEMAS CRÍTICOS")
    
    # Teste adicional: verificar se o servidor está realmente rodando
    print("\n🔍 TESTE ADICIONAL - Status do Servidor:")
    try:
        response = requests.get(f'{base_url}/', timeout=2)
        print(f"✅ Servidor respondendo na porta 5000 (Status: {response.status_code})")
    except:
        print("❌ Servidor não está respondendo na porta 5000")
    
    return total_ok, total_geral

if __name__ == '__main__':
    testar_sistema()