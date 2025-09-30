#!/usr/bin/env python3
"""
Script para adicionar campos telefone e data_nascimento à tabela users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.models.base import db
from sqlalchemy import text

def create_app():
    """Cria a aplicação Flask para migração"""
    app = Flask(__name__)
    
    # Configuração do banco de dados - mesma lógica do main.py
    if os.getenv('DATABASE_URL'):
        # Produção - PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        # Corrige URL do PostgreSQL se necessário
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"[DEBUG] Usando PostgreSQL: {database_url[:50]}...")
    else:
        # Desenvolvimento - SQLite
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'database', 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
        print(f"[DEBUG] Usando SQLite: {db_path}")
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = 'temp-migration-key'
    db.init_app(app)
    return app

def migrate_add_user_fields():
    """Adiciona campos telefone e data_nascimento à tabela users"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se as colunas já existem
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
            
            # Adicionar coluna telefone se não existir
            if 'telefone' not in columns:
                print("Adicionando coluna 'telefone' à tabela users...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN telefone VARCHAR(20)"))
                    conn.commit()
                print("✓ Coluna 'telefone' adicionada com sucesso!")
            else:
                print("✓ Coluna 'telefone' já existe")
            
            # Adicionar coluna data_nascimento se não existir
            if 'data_nascimento' not in columns:
                print("Adicionando coluna 'data_nascimento' à tabela users...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN data_nascimento DATE"))
                    conn.commit()
                print("✓ Coluna 'data_nascimento' adicionada com sucesso!")
            else:
                print("✓ Coluna 'data_nascimento' já existe")
            
            print("\n✅ Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🔄 Iniciando migração para adicionar campos de usuário...")
    success = migrate_add_user_fields()
    
    if success:
        print("✅ Migração executada com sucesso!")
    else:
        print("❌ Falha na migração!")
        sys.exit(1)