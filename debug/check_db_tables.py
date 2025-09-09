#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database_structure():
    """Verifica a estrutura do banco de dados"""
    
    db_path = 'consultorio.db'
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== ESTRUTURA DO BANCO DE DADOS ===")
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📋 Tabelas encontradas: {len(tables)}")
    for table in tables:
        table_name = table[0]
        print(f"\n🔹 Tabela: {table_name}")
        
        # Mostrar estrutura da tabela
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            nullable = "NOT NULL" if not_null else "NULL"
            primary = "PRIMARY KEY" if pk else ""
            print(f"   - {col_name}: {col_type} {nullable} {primary}")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"   📊 Registros: {count}")
        
        # Se for especialidade ou funcionario, mostrar alguns registros
        if table_name in ['especialidade', 'funcionario', 'especialidades', 'funcionarios']:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample_records = cursor.fetchall()
            if sample_records:
                print(f"   📝 Exemplos:")
                for record in sample_records:
                    print(f"      {record}")
    
    conn.close()

if __name__ == '__main__':
    check_database_structure()