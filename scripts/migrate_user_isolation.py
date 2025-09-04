#!/usr/bin/env python3
"""
Script para migrar o banco de dados e adicionar isolamento de dados por usuário
Adiciona campos user_id aos modelos Patient, Payment e Appointment
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.usuario import db, User
from src.models.paciente import Patient
from src.models.pagamento import Payment
from src.models.consulta import Appointment
from src.main import app
from sqlalchemy import text

def migrate_user_isolation():
    """Migra o banco de dados para adicionar isolamento por usuário"""
    # Configurar caminho correto do banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        try:
            print("Iniciando migração para isolamento de dados por usuário...")
            
            print("Adicionando colunas user_id às tabelas existentes...")
            
            # Adicionar coluna user_id à tabela patients se não existir
            try:
                db.session.execute(text("ALTER TABLE patients ADD COLUMN user_id INTEGER"))
                print("Coluna user_id adicionada à tabela patients")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("Coluna user_id já existe na tabela patients")
                else:
                    print(f"Erro ao adicionar coluna user_id à tabela patients: {e}")
            
            # Adicionar coluna user_id à tabela appointments se não existir
            try:
                db.session.execute(text("ALTER TABLE appointments ADD COLUMN user_id INTEGER"))
                print("Coluna user_id adicionada à tabela appointments")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("Coluna user_id já existe na tabela appointments")
                else:
                    print(f"Erro ao adicionar coluna user_id à tabela appointments: {e}")
            
            # Adicionar coluna user_id à tabela payments se não existir
            try:
                db.session.execute(text("ALTER TABLE payments ADD COLUMN user_id INTEGER"))
                print("Coluna user_id adicionada à tabela payments")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("Coluna user_id já existe na tabela payments")
                else:
                    print(f"Erro ao adicionar coluna user_id à tabela payments: {e}")
            
            # Criar todas as tabelas se não existirem
            db.create_all()
            db.session.commit()
            
            # Verificar se existe pelo menos um usuário
            first_user = User.query.first()
            if not first_user:
                print("Nenhum usuário encontrado. Criando usuário admin...")
                admin_user = User(username='admin', email='admin@consultorio.com')
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                first_user = admin_user
                print(f"Usuário admin criado: {first_user.username}")
            
            # Atualizar registros existentes que não têm user_id
            try:
                # Atualizar pacientes
                patients_updated = db.session.execute(
                    text('UPDATE patient SET user_id = :user_id WHERE user_id IS NULL'),
                    {'user_id': first_user.id}
                ).rowcount
                print(f"Pacientes atualizados: {patients_updated}")
                
                # Atualizar pagamentos
                payments_updated = db.session.execute(
                    text('UPDATE payment SET user_id = :user_id WHERE user_id IS NULL'),
                    {'user_id': first_user.id}
                ).rowcount
                print(f"Pagamentos atualizados: {payments_updated}")
                
                # Atualizar agendamentos
                appointments_updated = db.session.execute(
                    text('UPDATE appointment SET user_id = :user_id WHERE user_id IS NULL'),
                    {'user_id': first_user.id}
                ).rowcount
                print(f"Agendamentos atualizados: {appointments_updated}")
                
                db.session.commit()
                
            except Exception as update_error:
                print(f"Aviso: Erro ao atualizar registros existentes: {update_error}")
                print("Isso é normal se as tabelas estão sendo criadas pela primeira vez.")
                db.session.rollback()
            
            print("Migração para isolamento de dados concluída com sucesso!")
            return True
                
        except Exception as e:
            print(f"Erro durante a migração: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Iniciando migração para isolamento de dados por usuário...")
    success = migrate_user_isolation()
    if success:
        print("Migração concluída com sucesso!")
    else:
        print("Falha na migração!")
        sys.exit(1)