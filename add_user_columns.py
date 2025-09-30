#!/usr/bin/env python3
"""
Script de Migração - Adicionar Colunas de Usuário
=================================================

Este script adiciona as colunas telefone e data_nascimento na tabela users
ANTES de qualquer operação do modelo SQLAlchemy.

Deve ser executado PRIMEIRO no processo de deploy.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_database_url():
    """Obtém a URL do banco de dados"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render.com usa postgres://, mas SQLAlchemy 1.4+ requer postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info(f"Usando DATABASE_URL de produção: {database_url[:50]}...")
        return database_url
    
    # Fallback para desenvolvimento local
    local_db = "sqlite:///src/database/app.db"
    logger.info(f"Usando banco local: {local_db}")
    return local_db

def check_column_exists(engine, table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        exists = column_name in column_names
        logger.info(f"Coluna '{column_name}' na tabela '{table_name}' {'existe' if exists else 'não existe'}")
        return exists
    except Exception as e:
        logger.error(f"Erro ao verificar coluna {column_name} na tabela {table_name}: {e}")
        return False

def check_table_exists(engine, table_name):
    """Verifica se uma tabela existe"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        exists = table_name in tables
        logger.info(f"Tabela '{table_name}' {'existe' if exists else 'não existe'}")
        return exists
    except Exception as e:
        logger.error(f"Erro ao verificar tabela {table_name}: {e}")
        return False

def add_user_columns(engine):
    """Adiciona as colunas telefone e data_nascimento na tabela users"""
    logger.info("=== INICIANDO ADIÇÃO DE COLUNAS DE USUÁRIO ===")
    
    try:
        # Verificar se a tabela users existe
        if not check_table_exists(engine, 'users'):
            logger.warning("Tabela 'users' não existe. Criando tabelas primeiro...")
            return True  # Deixar o db.create_all() criar as tabelas com as colunas
        
        with engine.connect() as conn:
            # Detectar tipo de banco
            database_url = get_database_url()
            is_postgresql = 'postgresql://' in database_url
            
            # Verificar e adicionar coluna telefone
            if not check_column_exists(engine, 'users', 'telefone'):
                logger.info("Adicionando coluna 'telefone'...")
                if is_postgresql:
                    conn.execute(text("ALTER TABLE users ADD COLUMN telefone VARCHAR(20) DEFAULT '(00) 00000-0000'"))
                else:
                    conn.execute(text("ALTER TABLE users ADD COLUMN telefone VARCHAR(20) DEFAULT '(00) 00000-0000'"))
                conn.commit()
                logger.info("✅ Coluna 'telefone' adicionada com sucesso")
            else:
                logger.info("✅ Coluna 'telefone' já existe")
            
            # Verificar e adicionar coluna data_nascimento
            if not check_column_exists(engine, 'users', 'data_nascimento'):
                logger.info("Adicionando coluna 'data_nascimento'...")
                if is_postgresql:
                    conn.execute(text("ALTER TABLE users ADD COLUMN data_nascimento DATE DEFAULT '1990-01-01'"))
                else:
                    conn.execute(text("ALTER TABLE users ADD COLUMN data_nascimento DATE DEFAULT '1990-01-01'"))
                conn.commit()
                logger.info("✅ Coluna 'data_nascimento' adicionada com sucesso")
            else:
                logger.info("✅ Coluna 'data_nascimento' já existe")
            
            # Atualizar registros existentes com valores padrão se necessário
            logger.info("Atualizando registros existentes com valores padrão...")
            
            # Atualizar telefones vazios
            result = conn.execute(text("UPDATE users SET telefone = '(00) 00000-0000' WHERE telefone IS NULL OR telefone = ''"))
            if result.rowcount > 0:
                logger.info(f"✅ {result.rowcount} registros atualizados com telefone padrão")
            
            # Atualizar datas de nascimento vazias
            result = conn.execute(text("UPDATE users SET data_nascimento = '1990-01-01' WHERE data_nascimento IS NULL"))
            if result.rowcount > 0:
                logger.info(f"✅ {result.rowcount} registros atualizados com data de nascimento padrão")
            
            conn.commit()
            
        logger.info("=== COLUNAS DE USUÁRIO ADICIONADAS COM SUCESSO ===")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao adicionar colunas de usuário: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO ADIÇÃO DE COLUNAS DE USUÁRIO")
    logger.info("=" * 60)
    
    try:
        # Obter URL do banco
        database_url = get_database_url()
        
        # Criar engine
        engine = create_engine(database_url)
        
        # Testar conexão
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Conexão com banco de dados estabelecida")
        
        # Executar migração
        success = add_user_columns(engine)
        
        if success:
            logger.info("🎉 ADIÇÃO DE COLUNAS EXECUTADA COM SUCESSO!")
            return 0
        else:
            logger.error("💥 FALHA NA ADIÇÃO DE COLUNAS!")
            return 1
            
    except Exception as e:
        logger.error(f"💥 ERRO CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)