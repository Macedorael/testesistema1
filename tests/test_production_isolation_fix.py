#!/usr/bin/env python3
"""
Script para testar e corrigir isolamento em produção
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_production_isolation():
    """Testa o isolamento em produção e aplica correções se necessário"""
    
    try:
        # Configurar para usar PostgreSQL em produção
        os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
        
        if not os.environ['DATABASE_URL']:
            print("[ERROR] DATABASE_URL não encontrada")
            return False
            
        print(f"[INFO] Conectando ao banco de produção...")
        print(f"[INFO] DATABASE_URL: {os.environ['DATABASE_URL'][:50]}...")
        
        # Importar modelos
        from src.main import app, db
        from src.models.especialidade import Especialidade
        from src.models.funcionario import Funcionario
        from src.models.usuario import Usuario
        
        with app.app_context():
            # Verificar usuários existentes
            usuarios = Usuario.query.all()
            print(f"[INFO] Usuários encontrados: {len(usuarios)}")
            for user in usuarios:
                print(f"  - ID: {user.id}, Email: {user.email}")
            
            # Verificar especialidades sem user_id
            esp_null = Especialidade.query.filter_by(user_id=None).count()
            esp_total = Especialidade.query.count()
            print(f"[INFO] Especialidades: {esp_total} total, {esp_null} sem user_id")
            
            # Verificar funcionários sem user_id
            func_null = Funcionario.query.filter_by(user_id=None).count()
            func_total = Funcionario.query.count()
            print(f"[INFO] Funcionários: {func_total} total, {func_null} sem user_id")
            
            # Mostrar alguns exemplos
            if esp_total > 0:
                print("[INFO] Exemplos de especialidades:")
                especialidades = Especialidade.query.limit(5).all()
                for esp in especialidades:
                    print(f"  - ID: {esp.id}, Nome: {esp.nome}, User_ID: {esp.user_id}")
            
            if func_total > 0:
                print("[INFO] Exemplos de funcionários:")
                funcionarios = Funcionario.query.limit(5).all()
                for func in funcionarios:
                    print(f"  - ID: {func.id}, Nome: {func.nome}, User_ID: {func.user_id}")
            
            # Aplicar correções se necessário
            if esp_null > 0 or func_null > 0:
                print(f"[CORREÇÃO] Aplicando correções automáticas...")
                
                # Obter IDs de usuários válidos
                user_ids = [u.id for u in usuarios]
                if not user_ids:
                    print("[ERROR] Nenhum usuário encontrado para aplicar correções")
                    return False
                
                # Corrigir especialidades
                if esp_null > 0:
                    especialidades_sem_user = Especialidade.query.filter_by(user_id=None).all()
                    for i, esp in enumerate(especialidades_sem_user):
                        esp.user_id = user_ids[i % len(user_ids)]
                    print(f"[CORREÇÃO] {esp_null} especialidades corrigidas")
                
                # Corrigir funcionários
                if func_null > 0:
                    funcionarios_sem_user = Funcionario.query.filter_by(user_id=None).all()
                    for i, func in enumerate(funcionarios_sem_user):
                        func.user_id = user_ids[i % len(user_ids)]
                    print(f"[CORREÇÃO] {func_null} funcionários corrigidos")
                
                # Salvar mudanças
                db.session.commit()
                print("[CORREÇÃO] Mudanças salvas com sucesso!")
                
                # Verificar novamente
                esp_null_after = Especialidade.query.filter_by(user_id=None).count()
                func_null_after = Funcionario.query.filter_by(user_id=None).count()
                print(f"[VERIFICAÇÃO] Após correção: {esp_null_after} especialidades e {func_null_after} funcionários sem user_id")
                
            else:
                print("[INFO] Isolamento OK - nenhuma correção necessária")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Erro durante teste: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    print(f"[INFO] Iniciando teste de isolamento em produção - {datetime.now()}")
    success = test_production_isolation()
    if success:
        print("[INFO] Teste concluído com sucesso")
    else:
        print("[ERROR] Teste falhou")
        sys.exit(1)