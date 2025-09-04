#!/usr/bin/env python3
"""
Script para migrar o banco de dados e adicionar o campo 'role' aos usuários existentes
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.usuario import db, User
from src.main import app

def migrate_database():
    """Migra o banco de dados"""
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("Migração do banco de dados concluída.")
                
        except Exception as e:
            print(f"Erro durante a migração: {str(e)}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    print("Iniciando migração do banco de dados...")
    success = migrate_database()
    if success:
        print("Migração concluída com sucesso!")
    else:
        print("Falha na migração!")
        sys.exit(1)

