#!/usr/bin/env python3
"""
Script para migrar o tamanho da coluna password_hash de 128 para 256 caracteres
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def migrate_password_hash_column():
    """
    Migra a coluna password_hash para suportar 256 caracteres
    """
    
    # Configurar URL do banco de dados
    if os.getenv('RENDER'):
        # Produção no Render
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("[ERROR] DATABASE_URL não encontrada no ambiente de produção")
            return False
    else:
        # Desenvolvimento local
        database_url = 'sqlite:///consultorio.db'
    
    print(f"[INFO] Conectando ao banco de dados...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            print("[INFO] Conexão estabelecida com sucesso")
            
            # Verificar se estamos usando PostgreSQL ou SQLite
            if 'postgresql' in database_url or 'postgres' in database_url:
                print("[INFO] Detectado PostgreSQL - executando migração...")
                
                # Alterar o tamanho da coluna password_hash
                migration_sql = text("""
                    ALTER TABLE users 
                    ALTER COLUMN password_hash TYPE VARCHAR(256)
                """)
                
                connection.execute(migration_sql)
                connection.commit()
                print("[SUCCESS] Coluna password_hash migrada para VARCHAR(256) com sucesso!")
                
            elif 'sqlite' in database_url:
                print("[INFO] Detectado SQLite - migração não necessária (SQLite não tem limite rígido de VARCHAR)")
                
            else:
                print("[WARNING] Tipo de banco de dados não reconhecido")
                return False
                
        return True
        
    except SQLAlchemyError as e:
        print(f"[ERROR] Erro na migração: {str(e)}")
        return False
    except Exception as e:
        print(f"[ERROR] Erro inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    print("=== Migração da Coluna password_hash ===")
    print("Alterando tamanho de VARCHAR(128) para VARCHAR(256)")
    print()
    
    success = migrate_password_hash_column()
    
    if success:
        print("\n[SUCCESS] Migração concluída com sucesso!")
        print("A coluna password_hash agora suporta hashes de até 256 caracteres.")
    else:
        print("\n[ERROR] Migração falhou. Verifique os logs acima.")
        sys.exit(1)