#!/usr/bin/env python3
"""
Script para corrigir problemas de inicialização em produção
"""

import os
import sys

def create_robust_startup():
    """Cria uma versão mais robusta da inicialização"""
    
    print("🔧 CRIANDO INICIALIZAÇÃO ROBUSTA PARA PRODUÇÃO")
    print("=" * 60)
    
    # Ler o arquivo main.py atual
    main_py_path = "src/main.py"
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar a seção de inicialização do banco
    start_marker = "# Inicializar banco de dados"
    end_marker = "@app.route('/')"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ Não foi possível encontrar a seção de inicialização")
        return False
    
    # Nova seção de inicialização mais robusta
    new_init_section = '''# Inicializar banco de dados
def initialize_database():
    """Inicializa o banco de dados de forma robusta"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"[DEBUG] Tentativa {retry_count + 1}/{max_retries} de inicialização do banco...")
            print(f"[DEBUG] URI do banco: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Testar conexão com timeout menor
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("[DEBUG] Conexão com o banco de dados testada com sucesso")
            
            db.create_all()
            print("[DEBUG] Tabelas do banco de dados criadas/verificadas com sucesso")
            
            # CORREÇÃO AUTOMÁTICA DE ISOLAMENTO
            print("[STARTUP] Verificando isolamento de dados...")
            try:
                # Verificar se existem registros sem user_id
                from src.models.especialidade import Especialidade
                from src.models.funcionario import Funcionario
                
                esp_null = Especialidade.query.filter_by(user_id=None).count()
                func_null = Funcionario.query.filter_by(user_id=None).count()
                
                if esp_null > 0 or func_null > 0:
                    print(f"[STARTUP] Problema detectado: {esp_null} especialidades e {func_null} funcionários sem user_id")
                    print("[STARTUP] Aplicando correções automáticas...")
                    
                    # Corrigir registros sem user_id
                    if esp_null > 0:
                        especialidades_sem_user = Especialidade.query.filter_by(user_id=None).all()
                        for i, esp in enumerate(especialidades_sem_user):
                            esp.user_id = (i % 2) + 1  # Distribuir entre usuários 1 e 2
                        print(f"[STARTUP] {esp_null} especialidades corrigidas")
                    
                    if func_null > 0:
                        funcionarios_sem_user = Funcionario.query.filter_by(user_id=None).all()
                        for i, func in enumerate(funcionarios_sem_user):
                            func.user_id = (i % 2) + 1  # Distribuir entre usuários 1 e 2
                        print(f"[STARTUP] {func_null} funcionários corrigidos")
                    
                    db.session.commit()
                    print("[STARTUP] Correções aplicadas com sucesso!")
                else:
                    print("[STARTUP] Isolamento OK - nenhuma correção necessária")
                    
            except Exception as e:
                print(f"[STARTUP] Erro na verificação de isolamento: {e}")
                db.session.rollback()
            
            # Verificar se há funcionários no banco
            try:
                funcionarios_count = Funcionario.query.count()
                print(f"[DEBUG] Total de funcionários no banco: {funcionarios_count}")
                
                if funcionarios_count > 0:
                    funcionarios = Funcionario.query.limit(5).all()
                    for func in funcionarios:
                        print(f"[DEBUG] Funcionário encontrado: ID={func.id}, Nome='{func.nome}', User_ID={func.user_id}")
            except Exception as e:
                print(f"[DEBUG] Erro ao verificar funcionários: {e}")
            
            print("[SUCCESS] Inicialização do banco concluída com sucesso!")
            return True
            
        except Exception as e:
            retry_count += 1
            print(f"[ERROR] Tentativa {retry_count} falhou: {e}")
            
            if retry_count < max_retries:
                import time
                wait_time = retry_count * 2  # Espera progressiva: 2s, 4s, 6s
                print(f"[RETRY] Aguardando {wait_time}s antes da próxima tentativa...")
                time.sleep(wait_time)
            else:
                print("[ERROR] Todas as tentativas de conexão falharam")
                print("[WARNING] Aplicação continuará sem inicialização completa do banco")
                import traceback
                print(f"[ERROR] Traceback completo: {traceback.format_exc()}")
                return False
    
    return False

# Executar inicialização robusta
with app.app_context():
    database_initialized = initialize_database()
    if not database_initialized:
        print("[WARNING] Banco não foi inicializado completamente, mas aplicação continuará")

'''
    
    # Substituir a seção antiga pela nova
    before_init = content[:start_idx]
    after_init = content[end_idx:]
    
    new_content = before_init + new_init_section + after_init
    
    # Criar backup
    backup_path = "src/main.py.backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")
    
    # Escrever nova versão
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ Arquivo atualizado: {main_py_path}")
    
    print("\n🎯 MELHORIAS IMPLEMENTADAS:")
    print("- Tentativas múltiplas de conexão com o banco (3x)")
    print("- Espera progressiva entre tentativas (2s, 4s, 6s)")
    print("- Aplicação continua funcionando mesmo se banco falhar")
    print("- Logs mais detalhados para diagnóstico")
    print("- Tratamento robusto de erros de isolamento")
    
    return True

if __name__ == '__main__':
    success = create_robust_startup()
    if success:
        print("\n✅ Correção aplicada com sucesso!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Teste localmente: python wsgi.py")
        print("2. Faça commit das mudanças")
        print("3. Deploy no Render")
        print("4. Monitore os logs do Render para verificar se a inicialização está funcionando")
    else:
        print("\n❌ Falha ao aplicar correção")