#!/usr/bin/env python3
"""
Script para testar a migração da coluna 'role' localmente
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def get_database_url():
    """Obtém a URL da base de dados local"""
    return 'sqlite:///src/database/app.db'

def test_role_migration():
    """Testa a migração da coluna role"""
    print("🧪 TESTANDO MIGRAÇÃO DA COLUNA 'ROLE'")
    print("=" * 50)
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    try:
        # 1. Verificar estrutura atual
        print("\n1️⃣ Verificando estrutura atual da tabela users...")
        inspector = inspect(engine)
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        
        print(f"   Colunas encontradas: {column_names}")
        
        if 'role' in column_names:
            print("   ✅ Coluna 'role' já existe")
        else:
            print("   ❌ Coluna 'role' não existe")
        
        # 2. Verificar usuários atuais
        print("\n2️⃣ Verificando usuários atuais...")
        with engine.connect() as conn:
            if 'role' in column_names:
                result = conn.execute(text("SELECT id, username, email, role FROM users"))
            else:
                result = conn.execute(text("SELECT id, username, email FROM users"))
            
            users = result.fetchall()
            print(f"   Total de usuários: {len(users)}")
            
            for user in users:
                if 'role' in column_names:
                    print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}")
                else:
                    print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: N/A")
        
        # 3. Simular migração se necessário
        if 'role' not in column_names:
            print("\n3️⃣ Simulando migração...")
            with engine.connect() as conn:
                # Adicionar coluna
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                print("   ✅ Coluna 'role' adicionada")
                
                # Popular usuários existentes
                result = conn.execute(text("UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''"))
                print(f"   ✅ {result.rowcount} usuário(s) populado(s) com role 'user'")
                
                # Atualizar admin se existir
                admin_result = conn.execute(text("""
                    UPDATE users 
                    SET role = 'admin' 
                    WHERE email = 'admin@consultorio.com' OR username = 'admin'
                """))
                
                if admin_result.rowcount > 0:
                    print(f"   ✅ {admin_result.rowcount} usuário(s) admin atualizado(s)")
                
                conn.commit()
        
        # 4. Verificação final
        print("\n4️⃣ Verificação final...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, email, role FROM users"))
            users = result.fetchall()
            
            print("   Usuários após migração:")
            for user in users:
                print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}")
            
            # Contar por role
            role_count = conn.execute(text("SELECT role, COUNT(*) FROM users GROUP BY role"))
            roles = role_count.fetchall()
            
            print("\n   Distribuição por role:")
            for role, count in roles:
                print(f"   - {role}: {count} usuário(s)")
        
        print("\n🎉 TESTE DE MIGRAÇÃO CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_role_migration()