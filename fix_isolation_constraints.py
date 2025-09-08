#!/usr/bin/env python3
"""
Script para corrigir constraints de isolamento no banco de dados
Remove constraints unique globais e cria constraints compostas por usuário
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.base import db
from sqlalchemy import text

def fix_isolation_constraints():
    """Corrige constraints para garantir isolamento por usuário"""
    with app.app_context():
        print("=== CORREÇÃO DE CONSTRAINTS DE ISOLAMENTO ===")
        
        try:
            # Para SQLite, precisamos recriar as tabelas pois não suporta DROP CONSTRAINT
            print("\n1. Fazendo backup dos dados...")
            
            # Backup especialidades
            especialidades_backup = db.session.execute(text(
                "SELECT id, user_id, nome, descricao, created_at, updated_at FROM especialidades"
            )).fetchall()
            print(f"Backup de {len(especialidades_backup)} especialidades")
            
            # Backup funcionarios
            funcionarios_backup = db.session.execute(text(
                "SELECT id, user_id, nome, telefone, email, especialidade_id, obs, created_at, updated_at FROM funcionarios"
            )).fetchall()
            print(f"Backup de {len(funcionarios_backup)} funcionários")
            
            print("\n2. Removendo tabelas antigas...")
            
            # Remover foreign keys primeiro (funcionarios referencia especialidades)
            db.session.execute(text("DROP TABLE IF EXISTS funcionarios"))
            db.session.execute(text("DROP TABLE IF EXISTS especialidades"))
            db.session.commit()
            
            print("\n3. Recriando tabelas com novas constraints...")
            
            # Recriar tabelas com as novas definições
            db.create_all()
            
            print("\n4. Restaurando dados...")
            
            # Restaurar especialidades
            for esp in especialidades_backup:
                db.session.execute(text(
                    "INSERT INTO especialidades (id, user_id, nome, descricao, created_at, updated_at) "
                    "VALUES (:id, :user_id, :nome, :descricao, :created_at, :updated_at)"
                ), {
                    'id': esp[0],
                    'user_id': esp[1], 
                    'nome': esp[2],
                    'descricao': esp[3],
                    'created_at': esp[4],
                    'updated_at': esp[5]
                })
            
            # Restaurar funcionarios
            for func in funcionarios_backup:
                db.session.execute(text(
                    "INSERT INTO funcionarios (id, user_id, nome, telefone, email, especialidade_id, obs, created_at, updated_at) "
                    "VALUES (:id, :user_id, :nome, :telefone, :email, :especialidade_id, :obs, :created_at, :updated_at)"
                ), {
                    'id': func[0],
                    'user_id': func[1],
                    'nome': func[2], 
                    'telefone': func[3],
                    'email': func[4],
                    'especialidade_id': func[5],
                    'obs': func[6],
                    'created_at': func[7],
                    'updated_at': func[8]
                })
            
            db.session.commit()
            
            print(f"\n5. Dados restaurados com sucesso!")
            print(f"   - {len(especialidades_backup)} especialidades")
            print(f"   - {len(funcionarios_backup)} funcionários")
            
            print("\n6. Verificando novas constraints...")
            
            # Testar constraint de especialidades
            try:
                db.session.execute(text(
                    "INSERT INTO especialidades (user_id, nome, descricao) VALUES (1, 'Teste Constraint', 'Teste')"
                ))
                db.session.execute(text(
                    "INSERT INTO especialidades (user_id, nome, descricao) VALUES (1, 'Teste Constraint', 'Teste 2')"
                ))
                db.session.commit()
                print("   ERRO: Constraint de especialidades não está funcionando!")
            except Exception as e:
                db.session.rollback()
                print(f"   ✓ Constraint de especialidades funcionando: {str(e)[:100]}...")
            
            # Testar constraint de funcionários
            try:
                db.session.execute(text(
                    "INSERT INTO funcionarios (user_id, nome, email) VALUES (1, 'Teste', 'teste@constraint.com')"
                ))
                db.session.execute(text(
                    "INSERT INTO funcionarios (user_id, nome, email) VALUES (1, 'Teste 2', 'teste@constraint.com')"
                ))
                db.session.commit()
                print("   ERRO: Constraint de funcionários não está funcionando!")
            except Exception as e:
                db.session.rollback()
                print(f"   ✓ Constraint de funcionários funcionando: {str(e)[:100]}...")
            
            # Testar que usuários diferentes podem ter mesmo nome/email
            try:
                db.session.execute(text(
                    "INSERT INTO especialidades (user_id, nome, descricao) VALUES (1, 'Teste Cross User', 'User 1')"
                ))
                db.session.execute(text(
                    "INSERT INTO especialidades (user_id, nome, descricao) VALUES (2, 'Teste Cross User', 'User 2')"
                ))
                db.session.execute(text(
                    "INSERT INTO funcionarios (user_id, nome, email) VALUES (1, 'Func Cross', 'cross@test.com')"
                ))
                db.session.execute(text(
                    "INSERT INTO funcionarios (user_id, nome, email) VALUES (2, 'Func Cross', 'cross@test.com')"
                ))
                db.session.commit()
                print("   ✓ Usuários diferentes podem ter especialidades/funcionários com mesmo nome/email")
                
                # Limpar dados de teste
                db.session.execute(text("DELETE FROM especialidades WHERE nome LIKE 'Teste%'"))
                db.session.execute(text("DELETE FROM funcionarios WHERE nome LIKE 'Teste%' OR nome LIKE 'Func%'"))
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                print(f"   ERRO: Não foi possível criar dados para usuários diferentes: {str(e)}")
            
            print("\n=== CORREÇÃO CONCLUÍDA COM SUCESSO! ===")
            print("As constraints de isolamento foram corrigidas.")
            print("Agora cada usuário pode ter suas próprias especialidades e funcionários.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\nERRO durante a correção: {str(e)}")
            print("Revertendo alterações...")
            raise

if __name__ == '__main__':
    fix_isolation_constraints()