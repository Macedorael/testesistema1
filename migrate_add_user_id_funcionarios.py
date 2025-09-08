#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração para adicionar coluna user_id na tabela funcionarios
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url():
    """Obter URL do banco de dados"""
    # Tentar variáveis de ambiente do Render primeiro
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    # Fallback para desenvolvimento local - usar o mesmo banco da aplicação
    return "sqlite:///src/database/app.db"

def check_table_exists(engine, table_name):
    """Verificar se a tabela existe"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        logger.error(f"Erro ao verificar tabela: {e}")
        return False

def check_column_exists(engine, table_name, column_name):
    """Verificar se a coluna existe na tabela"""
    try:
        if not check_table_exists(engine, table_name):
            logger.warning(f"Tabela {table_name} não existe")
            return False
            
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        return column_name in column_names
    except Exception as e:
        logger.error(f"Erro ao verificar coluna: {e}")
        return False

def migrate_add_user_id_column():
    """Adicionar coluna user_id na tabela funcionarios"""
    database_url = get_database_url()
    logger.info(f"Conectando ao banco: {database_url[:50]}...")
    
    try:
        engine = create_engine(database_url)
        
        # Verificar se a tabela funcionarios existe
        if not check_table_exists(engine, 'funcionarios'):
            logger.error("❌ Tabela funcionarios não existe! Execute a inicialização do banco primeiro.")
            return False
        
        # Verificar se a coluna já existe
        if check_column_exists(engine, 'funcionarios', 'user_id'):
            logger.info("✅ Coluna user_id já existe na tabela funcionarios")
            return True
        
        logger.info("🔧 Adicionando coluna user_id na tabela funcionarios...")
        
        with engine.connect() as conn:
            # Verificar se é PostgreSQL ou SQLite
            if 'postgresql' in database_url or 'postgres' in database_url:
                # PostgreSQL
                logger.info("Detectado PostgreSQL - executando migração...")
                
                # Adicionar coluna user_id
                conn.execute(text("""
                    ALTER TABLE funcionarios 
                    ADD COLUMN IF NOT EXISTS user_id INTEGER
                """))
                
                # Verificar se existe tabela users
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'users'
                    )
                """))
                
                if result.scalar():
                    # Adicionar foreign key constraint
                    try:
                        conn.execute(text("""
                            ALTER TABLE funcionarios 
                            ADD CONSTRAINT fk_funcionarios_user_id 
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        """))
                        logger.info("✅ Foreign key constraint adicionada")
                    except Exception as fk_error:
                        logger.warning(f"Aviso: Não foi possível adicionar FK constraint: {fk_error}")
                
                # Atualizar funcionários existentes com user_id padrão (1)
                result = conn.execute(text("""
                    UPDATE funcionarios 
                    SET user_id = 1 
                    WHERE user_id IS NULL
                """))
                
                updated_rows = result.rowcount
                logger.info(f"✅ {updated_rows} funcionários atualizados com user_id = 1")
                
            else:
                # SQLite
                logger.info("Detectado SQLite - executando migração...")
                
                # No SQLite, precisamos recriar a tabela
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS funcionarios_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL DEFAULT 1,
                        nome VARCHAR(100) NOT NULL,
                        telefone VARCHAR(20),
                        email VARCHAR(100),
                        especialidade_id INTEGER,
                        obs TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (especialidade_id) REFERENCES especialidades(id),
                        UNIQUE(user_id, email)
                    )
                """))
                
                # Copiar dados existentes
                conn.execute(text("""
                    INSERT INTO funcionarios_new 
                    (id, user_id, nome, telefone, email, especialidade_id, obs, created_at, updated_at)
                    SELECT 
                        id, 1 as user_id, nome, telefone, email, especialidade_id, obs, 
                        created_at, updated_at
                    FROM funcionarios
                """))
                
                # Substituir tabela antiga
                conn.execute(text("DROP TABLE funcionarios"))
                conn.execute(text("ALTER TABLE funcionarios_new RENAME TO funcionarios"))
                
                logger.info("✅ Tabela funcionarios recriada com coluna user_id")
            
            conn.commit()
            logger.info("✅ Migração concluída com sucesso!")
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"❌ Erro de banco de dados: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return False

def verify_migration():
    """Verificar se a migração foi bem-sucedida"""
    database_url = get_database_url()
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar estrutura da tabela
            if 'postgresql' in database_url or 'postgres' in database_url:
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'funcionarios'
                    ORDER BY ordinal_position
                """))
            else:
                result = conn.execute(text("PRAGMA table_info(funcionarios)"))
            
            columns = result.fetchall()
            logger.info("📋 Estrutura atual da tabela funcionarios:")
            for col in columns:
                logger.info(f"   - {col}")
            
            # Contar funcionários
            result = conn.execute(text("SELECT COUNT(*) FROM funcionarios"))
            count = result.scalar()
            logger.info(f"📊 Total de funcionários: {count}")
            
            # Verificar user_ids
            result = conn.execute(text("""
                SELECT user_id, COUNT(*) as count 
                FROM funcionarios 
                GROUP BY user_id 
                ORDER BY user_id
            """))
            
            user_counts = result.fetchall()
            logger.info("👥 Distribuição por user_id:")
            for user_id, count in user_counts:
                logger.info(f"   - User ID {user_id}: {count} funcionários")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MIGRAÇÃO: Adicionar coluna user_id na tabela funcionarios")
    print("=" * 60)
    
    # Executar migração
    if migrate_add_user_id_column():
        print("\n🔍 Verificando migração...")
        verify_migration()
        print("\n✅ Migração concluída! A coluna user_id foi adicionada com sucesso.")
    else:
        print("\n❌ Falha na migração. Verifique os logs acima.")
        sys.exit(1)