#!/usr/bin/env python3
"""
Script para remover a coluna CPF da tabela de pacientes
"""

import sys
import os

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

def remove_cpf_column():
    """Remove a coluna CPF da tabela patients"""
    with app.app_context():
        try:
            # Verificar se a coluna CPF existe
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA table_info(patients)")).fetchall()
            
            columns = [row[1] for row in result]
            
            if 'cpf' not in columns:
                print("✅ Coluna CPF já foi removida da tabela patients")
                return
            
            print("🔄 Removendo coluna CPF da tabela patients...")
            
            # SQLite não suporta DROP COLUMN diretamente
            # Precisamos recriar a tabela sem a coluna CPF
            
            with db.engine.connect() as conn:
                # 1. Criar tabela temporária sem CPF
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
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """))
                
                # 2. Copiar dados (exceto CPF)
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
                
                # 5. Recriar índices se necessário
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id)
                """))
                
                conn.commit()
            
            print("✅ Coluna CPF removida com sucesso!")
            print("📊 Verificando estrutura da tabela...")
            
            # Verificar nova estrutura
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA table_info(patients)")).fetchall()
            
            print("\n📋 Colunas da tabela patients:")
            for row in result:
                print(f"  - {row[1]} ({row[2]})")
            
        except Exception as e:
            print(f"❌ Erro ao remover coluna CPF: {e}")
            raise

if __name__ == "__main__":
    print("🚀 Iniciando remoção da coluna CPF...")
    remove_cpf_column()
    print("\n✅ Migração concluída com sucesso!")