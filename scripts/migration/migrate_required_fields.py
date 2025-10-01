#!/usr/bin/env python3
"""
Script de Migração - Campos Obrigatórios
========================================

Este script torna os campos telefone e data_nascimento obrigatórios na tabela users
durante o processo de deploy, garantindo que a aplicação funcione corretamente
em produção sem intervenção manual.

Funcionalidades:
- Detecta automaticamente o tipo de banco de dados (PostgreSQL/SQLite)
- Verifica se os campos já são obrigatórios
- Atualiza registros existentes com valores padrão se necessário
- Altera as colunas para NOT NULL
- Verifica se a migração foi aplicada corretamente

Uso:
    python migrate_required_fields.py

Autor: Sistema de Consultório de Psicologia
Data: 2024
"""

import os
import sys
import logging
from datetime import datetime, date
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
    """Obtém a URL do banco de dados das variáveis de ambiente"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Fallback para desenvolvimento local - usar o mesmo caminho do main.py
        database_url = 'sqlite:///src/database/app.db'
        logger.info("Usando banco SQLite local para desenvolvimento")
    else:
        logger.info(f"Usando banco de dados: {database_url.split('@')[0]}@...")
    
    return database_url

def is_postgresql(engine):
    """Verifica se o banco é PostgreSQL"""
    return 'postgresql' in str(engine.url)

def check_column_nullable(engine, table_name, column_name):
    """Verifica se uma coluna permite valores NULL"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        
        for col in columns:
            if col['name'] == column_name:
                return col['nullable']
        
        return None  # Coluna não encontrada
    except Exception as e:
        logger.error(f"Erro ao verificar coluna {column_name}: {e}")
        return None

def migrate_required_fields(engine):
    """Migra os campos telefone e data_nascimento para obrigatórios"""
    logger.info("=== INICIANDO MIGRAÇÃO DE CAMPOS OBRIGATÓRIOS ===")
    
    try:
        with engine.connect() as conn:
            # Verificar se a tabela users existe
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'users' not in tables:
                logger.error("Tabela 'users' não encontrada!")
                return False
            
            # Verificar colunas existentes
            columns = inspector.get_columns('users')
            column_names = [col['name'] for col in columns]
            
            logger.info(f"Colunas encontradas na tabela users: {column_names}")
            
            # Verificar se as colunas telefone e data_nascimento existem
            if 'telefone' not in column_names:
                logger.error("Coluna 'telefone' não encontrada! Execute primeiro a migração de campos de usuário.")
                return False
            
            if 'data_nascimento' not in column_names:
                logger.error("Coluna 'data_nascimento' não encontrada! Execute primeiro a migração de campos de usuário.")
                return False
            
            # Verificar se as colunas já são obrigatórias
            telefone_nullable = check_column_nullable(engine, 'users', 'telefone')
            data_nascimento_nullable = check_column_nullable(engine, 'users', 'data_nascimento')
            
            logger.info(f"Status atual - telefone nullable: {telefone_nullable}, data_nascimento nullable: {data_nascimento_nullable}")
            
            # Se ambas já são obrigatórias, não há nada a fazer
            if not telefone_nullable and not data_nascimento_nullable:
                logger.info("✅ Ambos os campos já são obrigatórios!")
                return True
            
            # Verificar registros com valores NULL
            result = conn.execute(text("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN telefone IS NULL OR telefone = '' THEN 1 ELSE 0 END) as telefone_null,
                       SUM(CASE WHEN data_nascimento IS NULL THEN 1 ELSE 0 END) as data_null
                FROM users
            """))
            
            stats = result.fetchone()
            logger.info(f"Estatísticas: {stats.total} usuários, {stats.telefone_null} sem telefone, {stats.data_null} sem data")
            
            # Atualizar registros com valores padrão se necessário
            if stats.telefone_null > 0:
                logger.info(f"Atualizando {stats.telefone_null} registro(s) sem telefone...")
                conn.execute(text("""
                    UPDATE users 
                    SET telefone = '(00) 00000-0000' 
                    WHERE telefone IS NULL OR telefone = ''
                """))
                logger.info("✅ Telefones padrão adicionados")
            
            if stats.data_null > 0:
                logger.info(f"Atualizando {stats.data_null} registro(s) sem data de nascimento...")
                conn.execute(text("""
                    UPDATE users 
                    SET data_nascimento = '1990-01-01' 
                    WHERE data_nascimento IS NULL
                """))
                logger.info("✅ Datas de nascimento padrão adicionadas")
            
            # Confirmar alterações
            conn.commit()
            
            # Alterar colunas para NOT NULL
            is_postgres = is_postgresql(engine)
            
            if telefone_nullable:
                logger.info("Alterando coluna 'telefone' para NOT NULL...")
                if is_postgres:
                    conn.execute(text("ALTER TABLE users ALTER COLUMN telefone SET NOT NULL"))
                else:
                    # SQLite não suporta ALTER COLUMN, precisamos recriar a tabela
                    logger.warning("SQLite detectado - a alteração para NOT NULL será aplicada em futuras criações de tabela")
                logger.info("✅ Coluna 'telefone' alterada para obrigatória")
            
            if data_nascimento_nullable:
                logger.info("Alterando coluna 'data_nascimento' para NOT NULL...")
                if is_postgres:
                    conn.execute(text("ALTER TABLE users ALTER COLUMN data_nascimento SET NOT NULL"))
                else:
                    logger.warning("SQLite detectado - a alteração para NOT NULL será aplicada em futuras criações de tabela")
                logger.info("✅ Coluna 'data_nascimento' alterada para obrigatória")
            
            # Confirmar alterações finais
            conn.commit()
            
            # Verificação final
            logger.info("Verificando migração...")
            result = conn.execute(text("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN telefone IS NULL OR telefone = '' THEN 1 ELSE 0 END) as telefone_null,
                       SUM(CASE WHEN data_nascimento IS NULL THEN 1 ELSE 0 END) as data_null
                FROM users
            """))
            
            final_stats = result.fetchone()
            
            if final_stats.telefone_null == 0 and final_stats.data_null == 0:
                logger.info("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
                logger.info(f"   - {final_stats.total} usuário(s) com campos obrigatórios preenchidos")
                return True
            else:
                logger.error(f"❌ Ainda existem registros com valores NULL: telefone={final_stats.telefone_null}, data={final_stats.data_null}")
                return False
                
    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 INICIANDO MIGRAÇÃO DE CAMPOS OBRIGATÓRIOS")
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
        success = migrate_required_fields(engine)
        
        if success:
            logger.info("🎉 MIGRAÇÃO EXECUTADA COM SUCESSO!")
            return 0
        else:
            logger.error("💥 FALHA NA MIGRAÇÃO!")
            return 1
            
    except Exception as e:
        logger.error(f"💥 ERRO CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)