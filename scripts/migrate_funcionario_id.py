#!/usr/bin/env python3
"""
Script para migrar o banco de dados e adicionar a coluna funcionario_id à tabela appointments
"""

import os
import sys
import sqlite3

def migrate_funcionario_id():
    """Adiciona a coluna funcionario_id à tabela appointments"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(appointments)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Adicionar funcionario_id se não existir
        if 'funcionario_id' not in columns:
            print("Adicionando coluna funcionario_id à tabela appointments...")
            cursor.execute(
                "ALTER TABLE appointments ADD COLUMN funcionario_id INTEGER"
            )
            print("✓ Coluna funcionario_id adicionada")
        else:
            print("✓ Coluna funcionario_id já existe")
        
        conn.commit()
        conn.close()
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        if 'conn' in locals():
            conn.close()
        return False
    
    return True

if __name__ == '__main__':
    print("🔄 Iniciando migração para adicionar funcionario_id...")
    print("Adicionando coluna funcionario_id à tabela appointments\n")
    
    success = migrate_funcionario_id()
    
    if success:
        print("\n🎉 Migração concluída! Agora os agendamentos podem ter psicólogos associados.")
    else:
        print("\n💥 Falha na migração. Verifique os erros acima.")
        sys.exit(1)