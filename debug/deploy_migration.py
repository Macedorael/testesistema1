#!/usr/bin/env python3
"""
Script de Deploy Automático com Migração
Executa automaticamente a migração da coluna user_id na tabela funcionarios durante o deploy
"""

import os
import sys
import subprocess
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url():
    """Obtém a URL do banco de dados baseada no ambiente"""
    # Prioridade: variável de ambiente DATABASE_URL (produção)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render.com usa postgres://, mas SQLAlchemy 1.4+ requer postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info(f"Usando DATABASE_URL de produção: {database_url[:20]}...")
        return database_url
    
    # Fallback para desenvolvimento local
    local_db = "sqlite:///src/database/app.db"
    logger.info(f"Usando banco local: {local_db}")
    return local_db

def check_table_exists(engine, table_name):
    """Verifica se uma tabela existe no banco de dados"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        exists = table_name in tables
        logger.info(f"Tabela '{table_name}' {'existe' if exists else 'não existe'}")
        return exists
    except Exception as e:
        logger.error(f"Erro ao verificar tabela {table_name}: {e}")
        return False

def check_column_exists(engine, table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        # Primeiro verifica se a tabela existe
        if not check_table_exists(engine, table_name):
            logger.error(f"Tabela '{table_name}' não existe")
            return False
            
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        exists = column_name in column_names
        logger.info(f"Coluna '{column_name}' na tabela '{table_name}' {'existe' if exists else 'não existe'}")
        return exists
    except Exception as e:
        logger.error(f"Erro ao verificar coluna {column_name} na tabela {table_name}: {e}")
        return False

def migrate_table_user_id(engine, table_name):
    """Adiciona a coluna user_id em uma tabela específica se não existir"""
    try:
        # Verifica se a tabela existe
        if not check_table_exists(engine, table_name):
            logger.error(f"Tabela '{table_name}' não existe. Migração não pode prosseguir.")
            return False
            
        # Verifica se a coluna user_id já existe
        if check_column_exists(engine, table_name, 'user_id'):
            logger.info(f"Coluna 'user_id' já existe na tabela '{table_name}'. Migração não necessária.")
            return True
        
        logger.info(f"Iniciando migração: adicionando coluna 'user_id' na tabela '{table_name}'")
        
        # Detecta o tipo de banco de dados
        db_url = str(engine.url)
        is_postgresql = 'postgresql' in db_url
        is_sqlite = 'sqlite' in db_url
        
        with engine.connect() as conn:
            if is_postgresql:
                logger.info(f"Detectado PostgreSQL - executando migração para {table_name}")
                
                # Adiciona a coluna user_id
                conn.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN user_id INTEGER
                """))
                
                # Adiciona a constraint de foreign key
                conn.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ADD CONSTRAINT fk_{table_name}_user_id 
                    FOREIGN KEY (user_id) REFERENCES users(id)
                """))
                
                # Atualiza registros existentes com user_id = 1 (admin padrão)
                result = conn.execute(text(f"""
                    UPDATE {table_name} 
                    SET user_id = 1 
                    WHERE user_id IS NULL
                """))
                
                logger.info(f"Atualizados {result.rowcount} registros em {table_name} com user_id = 1")
                
            elif is_sqlite:
                logger.info(f"Detectado SQLite - executando migração para {table_name}")
                
                # SQLite não suporta ADD CONSTRAINT, então criamos sem constraint
                conn.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN user_id INTEGER
                """))
                
                # Atualiza registros existentes
                result = conn.execute(text(f"""
                    UPDATE {table_name} 
                    SET user_id = 1 
                    WHERE user_id IS NULL
                """))
                
                logger.info(f"Atualizados {result.rowcount} registros em {table_name} com user_id = 1")
            
            conn.commit()
            
        logger.info(f"Migração da tabela {table_name} concluída com sucesso!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Erro na migração da tabela {table_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado na migração da tabela {table_name}: {e}")
        return False

def migrate_add_user_id_columns(engine):
    """Adiciona a coluna user_id nas tabelas funcionarios e especialidades"""
    logger.info("=== INICIANDO MIGRAÇÃO DE COLUNAS USER_ID ===")
    
    # Lista de tabelas que precisam da coluna user_id
    tables_to_migrate = ['funcionarios', 'especialidades']
    
    success = True
    for table in tables_to_migrate:
        logger.info(f"Migrando tabela: {table}")
        if not migrate_table_user_id(engine, table):
            logger.error(f"Falha na migração da tabela {table}")
            success = False
        else:
            logger.info(f"Tabela {table} migrada com sucesso")
    
    return success

def verify_table_migration(engine, table_name):
    """Verifica se a migração foi aplicada corretamente em uma tabela específica"""
    try:
        logger.info(f"Verificando migração da tabela {table_name}...")
        
        # Verifica se a coluna existe
        if not check_column_exists(engine, table_name, 'user_id'):
            logger.error(f"Verificação falhou: coluna 'user_id' não encontrada na tabela {table_name}")
            return False
        
        # Verifica dados
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(*) as total, 
                       COUNT(user_id) as with_user_id,
                       COUNT(*) - COUNT(user_id) as null_user_id
                FROM {table_name}
            """))
            
            row = result.fetchone()
            total = row[0]
            with_user_id = row[1]
            null_user_id = row[2]
            
            logger.info(f"Verificação {table_name}: {total} registros total, {with_user_id} com user_id, {null_user_id} com user_id NULL")
            
            if null_user_id > 0:
                logger.warning(f"Atenção: {null_user_id} registros em {table_name} ainda têm user_id NULL")
            
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação da tabela {table_name}: {e}")
        return False

def verify_migration(engine):
    """Verifica se a migração foi aplicada corretamente em todas as tabelas"""
    logger.info("=== VERIFICANDO MIGRAÇÕES ===")
    
    tables_to_verify = ['funcionarios', 'especialidades']
    success = True
    
    for table in tables_to_verify:
        if not verify_table_migration(engine, table):
            success = False
    
    if success:
        logger.info("Verificação de todas as migrações concluída com sucesso")
    else:
        logger.error("Falha na verificação de algumas migrações")
    
    return success

def run_migration():
    """Executa a migração completa"""
    logger.info("=== INICIANDO DEPLOY COM MIGRAÇÃO AUTOMÁTICA ===")
    
    try:
        # Conecta ao banco de dados
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        logger.info("Conexão com banco de dados estabelecida")
        
        # Executa a migração
        if migrate_add_user_id_columns(engine):
            # Verifica a migração
            if verify_migration(engine):
                logger.info("=== MIGRAÇÃO CONCLUÍDA COM SUCESSO ===")
                return True
            else:
                logger.error("=== FALHA NA VERIFICAÇÃO DA MIGRAÇÃO ===")
                return False
        else:
            logger.error("=== FALHA NA MIGRAÇÃO ===")
            return False
            
    except Exception as e:
        logger.error(f"Erro crítico no deploy: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

def install_dependencies():
    """Instala dependências necessárias (apenas em produção)"""
    # Só instala dependências se estivermos em produção (DATABASE_URL definida)
    if not os.getenv('DATABASE_URL'):
        logger.info("Ambiente de desenvolvimento detectado - pulando instalação de dependências")
        return True
        
    logger.info("Verificando e instalando dependências...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        logger.info("Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar dependências: {e}")
        return False

def main():
    """Função principal do deploy"""
    logger.info("=== INICIANDO DEPLOY AUTOMÁTICO ===")
    
    # Instala dependências
    if not install_dependencies():
        logger.error("Falha ao instalar dependências")
        sys.exit(1)
    
    # Executa migração
    if not run_migration():
        logger.error("Falha na migração")
        sys.exit(1)
    
    logger.info("=== DEPLOY CONCLUÍDO COM SUCESSO ===")
    logger.info("Aplicação pronta para uso!")

if __name__ == "__main__":
    main()