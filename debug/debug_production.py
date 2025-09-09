#!/usr/bin/env python3
"""
Script para diagnosticar problemas específicos de produção
"""

import os
import sys
from io import StringIO

def debug_production_environment():
    """Simula ambiente de produção e diagnostica problemas"""
    
    print("🔧 DIAGNÓSTICO DO AMBIENTE DE PRODUÇÃO")
    print("=" * 60)
    
    # Simular variáveis de ambiente de produção
    print("\n1. Configurando ambiente de produção...")
    print("-" * 40)
    
    # Backup das variáveis originais
    original_env = {
        'FLASK_ENV': os.environ.get('FLASK_ENV'),
        'DATABASE_URL': os.environ.get('DATABASE_URL')
    }
    
    # Configurar ambiente de produção
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db'  # URL fictícia
    
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL')[:50]}...")
    
    # Capturar logs de inicialização
    print("\n2. Testando inicialização em modo produção...")
    print("-" * 40)
    
    captured_output = StringIO()
    old_stdout = sys.stdout
    
    try:
        # Limpar módulos já importados para forçar reimportação
        modules_to_remove = []
        for module_name in sys.modules.keys():
            if module_name.startswith('src.'):
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            del sys.modules[module_name]
        
        # Capturar logs
        sys.stdout = captured_output
        
        # Importar novamente com ambiente de produção
        from src.main import app
        
        # Restaurar stdout
        sys.stdout = old_stdout
        
        # Analisar logs
        output = captured_output.getvalue()
        print("\n📋 LOGS DE INICIALIZAÇÃO (PRODUÇÃO):")
        print("-" * 40)
        
        errors = []
        warnings = []
        success = []
        
        for line in output.split('\n'):
            if line.strip():
                if '[ERROR]' in line:
                    errors.append(line)
                    print(f"❌ {line}")
                elif '[DEBUG]' in line and 'OK' in line:
                    success.append(line)
                    print(f"✅ {line}")
                elif '[DEBUG]' in line:
                    print(f"ℹ️  {line}")
                else:
                    print(f"   {line}")
        
        print("\n3. Verificando rotas em modo produção...")
        print("-" * 40)
        
        # Verificar rotas registradas
        api_routes = []
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api'):
                api_routes.append(rule.rule)
        
        critical_routes = ['/api/login', '/api/especialidades', '/api/funcionarios']
        
        print(f"Total de rotas API: {len(api_routes)}")
        for route in critical_routes:
            found = route in api_routes
            status = "✅ OK" if found else "❌ FALTANDO"
            print(f"   {route}: {status}")
        
        print("\n4. Testando configuração de banco de dados...")
        print("-" * 40)
        
        try:
            # Testar configuração do banco
            db_config = app.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"   Database URI: {db_config[:50] if db_config else 'NÃO CONFIGURADO'}...")
            
            # Verificar se há problemas de conexão simulados
            if 'postgresql://' in str(db_config):
                print("   ✅ Configuração PostgreSQL detectada")
            elif 'sqlite://' in str(db_config):
                print("   ⚠️  Usando SQLite (desenvolvimento)")
            else:
                print("   ❌ Configuração de banco não reconhecida")
                
        except Exception as e:
            print(f"   ❌ Erro na configuração do banco: {e}")
        
        print("\n5. Resumo do diagnóstico...")
        print("-" * 40)
        print(f"   Erros encontrados: {len(errors)}")
        print(f"   Importações bem-sucedidas: {len(success)}")
        
        if errors:
            print("\n❌ ERROS CRÍTICOS:")
            for error in errors:
                print(f"   • {error}")
        
        if len(api_routes) < 10:  # Esperamos pelo menos 10 rotas API
            print("\n⚠️  AVISO: Poucas rotas API registradas")
        
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ ERRO CRÍTICO durante inicialização: {str(e)}")
        print(f"Tipo: {type(e).__name__}")
        
        # Mostrar logs capturados
        output = captured_output.getvalue()
        if output:
            print("\n📋 LOGS ANTES DO ERRO:")
            for line in output.split('\n'):
                if line.strip() and '[ERROR]' in line:
                    print(f"❌ {line}")
    
    finally:
        # Restaurar variáveis de ambiente originais
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSÕES")
    print("=" * 60)
    print("- Se há erros em produção mas não em dev: problema de configuração")
    print("- Se rotas não são registradas: problema de importação ou dependência")
    print("- Se banco falha: problema de URL ou credenciais")
    print("- Verifique os logs do Render para confirmar o diagnóstico")

if __name__ == '__main__':
    debug_production_environment()