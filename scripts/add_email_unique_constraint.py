#!/usr/bin/env python3
"""
Script para adicionar restrição de unicidade composta (user_id, email) na tabela patients
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from src.models.usuario import db

# Criar app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'consultorio-psicologia-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db.init_app(app)

def add_email_unique_constraint():
    """Adiciona restrição de unicidade composta (user_id, email) na tabela patients"""
    with app.app_context():
        try:
            # Verificar se a restrição já existe
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA index_list(patients)")).fetchall()
            
            constraint_exists = any('unique_user_email' in str(row) for row in result)
            
            if constraint_exists:
                print("✅ Restrição de unicidade de email por usuário já existe")
                return
            
            print("🔄 Verificando emails duplicados por usuário...")
            
            # Verificar se existem emails duplicados por usuário
            with db.engine.connect() as conn:
                duplicates = conn.execute(db.text("""
                    SELECT user_id, email, COUNT(*) as count
                    FROM patients 
                    GROUP BY user_id, email 
                    HAVING COUNT(*) > 1
                """)).fetchall()
            
            if duplicates:
                print("⚠️  Encontrados emails duplicados por usuário:")
                for dup in duplicates:
                    print(f"   - User ID: {dup[0]}, Email: {dup[1]}, Quantidade: {dup[2]}")
                
                print("\n❌ Não é possível adicionar a restrição com dados duplicados.")
                print("   Por favor, resolva os emails duplicados primeiro.")
                return False
            
            print("🔄 Adicionando restrição de unicidade composta...")
            
            # SQLite não suporta ADD CONSTRAINT diretamente
            # Precisamos recriar a tabela com a nova restrição
            
            with db.engine.connect() as conn:
                # 1. Criar tabela temporária com a restrição
                conn.execute(db.text("""
                    CREATE TABLE patients_temp (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        nome_completo VARCHAR(200) NOT NULL,
                        telefone VARCHAR(20) NOT NULL,
                        email VARCHAR(120) NOT NULL,
                        data_nascimento DATE NOT NULL,
                        observacoes TEXT,
                        nome_contato_emergencia VARCHAR(200),
                        telefone_contato_emergencia VARCHAR(20),
                        grau_parentesco_emergencia VARCHAR(50),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        UNIQUE (user_id, email)
                    )
                """))
                
                # 2. Copiar dados
                conn.execute(db.text("""
                    INSERT INTO patients_temp (
                        id, user_id, nome_completo, telefone, email, data_nascimento,
                        observacoes, nome_contato_emergencia, telefone_contato_emergencia,
                        grau_parentesco_emergencia, created_at, updated_at
                    )
                    SELECT 
                        id, user_id, nome_completo, telefone, email, data_nascimento,
                        observacoes, nome_contato_emergencia, telefone_contato_emergencia,
                        grau_parentesco_emergencia, created_at, updated_at
                    FROM patients
                """))
                
                # 3. Remover tabela original
                conn.execute(db.text("DROP TABLE patients"))
                
                # 4. Renomear tabela temporária
                conn.execute(db.text("ALTER TABLE patients_temp RENAME TO patients"))
                
                # 5. Recriar índices
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id)
                """))
                
                conn.commit()
            
            print("✅ Restrição de unicidade adicionada com sucesso!")
            print("📊 Verificando nova estrutura da tabela...")
            
            # Verificar nova estrutura
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA table_info(patients)")).fetchall()
            
            print("\n📋 Colunas da tabela patients:")
            for row in result:
                print(f"  - {row[1]} ({row[2]})")
            
            # Verificar índices
            with db.engine.connect() as conn:
                indexes = conn.execute(db.text("PRAGMA index_list(patients)")).fetchall()
            
            print("\n📋 Índices da tabela patients:")
            for idx in indexes:
                print(f"  - {idx[1]} (unique: {bool(idx[2])})")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar restrição: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Iniciando adição de restrição de unicidade de email...")
    success = add_email_unique_constraint()
    if success:
        print("\n✅ Migração concluída com sucesso!")
    else:
        print("\n❌ Migração falhou!")
        sys.exit(1)