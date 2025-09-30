#!/usr/bin/env python3
"""
Script para debugar a relação funcionário-especialidade
"""

import sqlite3
import os

def main():
    print("=== DEBUGANDO FUNCIONÁRIO-ESPECIALIDADE ===")
    
    # Caminho do banco de dados
    database_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    if not os.path.exists(database_path):
        print(f"Banco de dados não encontrado em: {database_path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tabelas: {[t[0] for t in tables]}")
        
        # Verificar funcionários
        print("\n=== FUNCIONÁRIOS ===")
        cursor.execute("SELECT id, nome, especialidade_id, user_id FROM funcionarios;")
        funcionarios = cursor.fetchall()
        for func in funcionarios:
            print(f"ID: {func[0]}, Nome: {func[1]}, Especialidade_ID: {func[2]}, User_ID: {func[3]}")
        
        # Verificar especialidades
        print("\n=== ESPECIALIDADES ===")
        cursor.execute("SELECT id, nome FROM especialidades;")
        especialidades = cursor.fetchall()
        for esp in especialidades:
            print(f"ID: {esp[0]}, Nome: {esp[1]}")
        
        # Verificar relação funcionário-especialidade
        print("\n=== FUNCIONÁRIOS COM ESPECIALIDADES ===")
        cursor.execute("""
            SELECT f.id, f.nome, e.nome as especialidade_nome, f.user_id
            FROM funcionarios f
            LEFT JOIN especialidades e ON f.especialidade_id = e.id
        """)
        func_esp = cursor.fetchall()
        for fe in func_esp:
            print(f"Funcionário: {fe[1]} (ID: {fe[0]}) - Especialidade: {fe[2]} - User_ID: {fe[3]}")
        
        # Verificar sessões do admin
        print("\n=== SESSÕES DO ADMIN ===")
        cursor.execute("""
            SELECT s.id, s.data_sessao, a.funcionario_id, f.nome as funcionario_nome, e.nome as especialidade_nome
            FROM sessions s
            JOIN appointments a ON s.appointment_id = a.id
            LEFT JOIN funcionarios f ON a.funcionario_id = f.id
            LEFT JOIN especialidades e ON f.especialidade_id = e.id
            WHERE a.user_id = 4
        """)
        sessions = cursor.fetchall()
        for session in sessions:
            print(f"Sessão ID: {session[0]}, Data: {session[1]}, Funcionário: {session[3]} (ID: {session[2]}), Especialidade: {session[4]}")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()