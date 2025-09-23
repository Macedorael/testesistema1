#!/usr/bin/env python3
"""
Script para adicionar a coluna 'role' na tabela users em produção
Este script deve ser executado no servidor de produção
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def get_database_url():
    """Obtém a URL da base de dados a partir das variáveis de ambiente"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render.com usa postgres:// mas SQLAlchemy precisa de postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Fallback para SQLite local (para testes)
    return 'sqlite:///src/database/app.db'

def check_role_column_exists(engine):
    """Verifica se a coluna 'role' já existe na tabela users"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        return 'role' in column_names
    except Exception as e:
        print(f"❌ Erro ao verificar colunas: {e}")
        return False

def add_role_column(engine):
    """Adiciona a coluna 'role' na tabela users"""
    try:
        with engine.connect() as conn:
            # Adicionar a coluna 'role' com valor padrão 'user'
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
            conn.commit()
            print("✅ Coluna 'role' adicionada com sucesso!")
            return True
    except SQLAlchemyError as e:
        print(f"❌ Erro ao adicionar coluna 'role': {e}")
        return False

def update_admin_user_role(engine):
    """Atualiza o role do usuário admin para 'admin'"""
    try:
        with engine.connect() as conn:
            # Atualizar usuário admin
            result = conn.execute(text("""
                UPDATE users 
                SET role = 'admin' 
                WHERE email = 'admin@consultorio.com' OR username = 'admin'
            """))
            conn.commit()
            
            if result.rowcount > 0:
                print(f"✅ {result.rowcount} usuário(s) admin atualizado(s) com role 'admin'")
            else:
                print("⚠️ Nenhum usuário admin encontrado para atualizar")
            
            return True
    except SQLAlchemyError as e:
        print(f"❌ Erro ao atualizar role do admin: {e}")
        return False

def verify_migration(engine):
    """Verifica se a migração foi bem-sucedida"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, email, role FROM users LIMIT 5"))
            users = result.fetchall()
            
            print("\n📋 VERIFICAÇÃO PÓS-MIGRAÇÃO:")
            print("=" * 50)
            for user in users:
                print(f"   ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}")
            
            # Verificar se existe pelo menos um admin
            admin_result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'"))
            admin_count = admin_result.scalar()
            
            if admin_count > 0:
                print(f"\n✅ {admin_count} usuário(s) com role 'admin' encontrado(s)")
            else:
                print("\n⚠️ Nenhum usuário com role 'admin' encontrado")
            
            return True
    except SQLAlchemyError as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🔧 MIGRAÇÃO: ADICIONANDO COLUNA 'ROLE' NA TABELA USERS")
    print("=" * 60)
    
    # Obter URL da base de dados
    database_url = get_database_url()
    print(f"📊 Base de dados: {database_url.split('@')[0] + '@***' if '@' in database_url else database_url}")
    
    try:
        # Criar engine
        engine = create_engine(database_url)
        
        # Verificar se a coluna já existe
        print("\n🔍 Verificando se a coluna 'role' já existe...")
        if check_role_column_exists(engine):
            print("✅ A coluna 'role' já existe na tabela users!")
            print("⚠️ Migração não necessária.")
            return
        
        print("❌ A coluna 'role' não existe. Iniciando migração...")
        
        # Adicionar coluna 'role'
        print("\n🔧 Adicionando coluna 'role'...")
        if not add_role_column(engine):
            print("❌ Falha ao adicionar coluna 'role'")
            sys.exit(1)
        
        # Atualizar role do usuário admin
        print("\n👤 Atualizando role do usuário admin...")
        update_admin_user_role(engine)
        
        # Verificar migração
        print("\n🧪 Verificando migração...")
        verify_migration(engine)
        
        print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ A coluna 'role' foi adicionada à tabela users")
        print("✅ O usuário admin foi configurado com role 'admin'")
        print("✅ Todos os outros usuários têm role 'user' por padrão")
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()