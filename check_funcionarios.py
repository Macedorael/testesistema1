#!/usr/bin/env python3

import sys
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def check_funcionarios():
    try:
        # Verificar se estamos usando SQLite ou PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        
        if database_url and 'postgres' in database_url:
            print("Usando PostgreSQL - não é possível verificar localmente")
            return
        
        # Usar SQLite local
        db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
        
        if not os.path.exists(db_path):
            print(f"Banco de dados não encontrado em: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar funcionários
        cursor.execute("SELECT COUNT(*) FROM funcionarios")
        total_funcionarios = cursor.fetchone()[0]
        print(f"Total de funcionários: {total_funcionarios}")
        
        if total_funcionarios > 0:
            cursor.execute("""
                SELECT f.id, f.nome, e.nome as especialidade_nome 
                FROM funcionarios f 
                LEFT JOIN especialidades e ON f.especialidade_id = e.id
            """)
            funcionarios = cursor.fetchall()
            
            for funcionario in funcionarios:
                id_func, nome, especialidade = funcionario
                especialidade = especialidade or "Sem especialidade"
                print(f"ID: {id_func}, Nome: {nome}, Especialidade: {especialidade}")
        else:
            print("Nenhum funcionário encontrado no banco de dados")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao consultar funcionários: {e}")

if __name__ == "__main__":
    check_funcionarios()