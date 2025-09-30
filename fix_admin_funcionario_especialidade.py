#!/usr/bin/env python3
"""
Script para corrigir a especialidade do funcionário Dr. Admin Silva
"""

import sqlite3
import os

def main():
    print("=== CORRIGINDO ESPECIALIDADE DO DR. ADMIN SILVA ===")
    
    # Caminho do banco de dados
    database_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    if not os.path.exists(database_path):
        print(f"Banco de dados não encontrado em: {database_path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Verificar funcionário Dr. Admin Silva
        cursor.execute("SELECT id, nome, especialidade_id FROM funcionarios WHERE nome = 'Dr. Admin Silva'")
        funcionario = cursor.fetchone()
        
        if not funcionario:
            print("Funcionário Dr. Admin Silva não encontrado!")
            return
        
        print(f"Funcionário encontrado: ID {funcionario[0]}, Nome: {funcionario[1]}, Especialidade_ID atual: {funcionario[2]}")
        
        # Atualizar especialidade para "medico" (ID: 1)
        cursor.execute("""
            UPDATE funcionarios 
            SET especialidade_id = 1 
            WHERE id = ?
        """, (funcionario[0],))
        
        conn.commit()
        print("✅ Especialidade atualizada para 'medico' (ID: 1)")
        
        # Verificar a mudança
        cursor.execute("SELECT id, nome, especialidade_id FROM funcionarios WHERE id = ?", (funcionario[0],))
        updated_funcionario = cursor.fetchone()
        print(f"Funcionário após atualização: ID {updated_funcionario[0]}, Nome: {updated_funcionario[1]}, Especialidade_ID: {updated_funcionario[2]}")
        
        # Verificar com JOIN
        cursor.execute("""
            SELECT f.id, f.nome, e.nome as especialidade_nome
            FROM funcionarios f
            LEFT JOIN especialidades e ON f.especialidade_id = e.id
            WHERE f.id = ?
        """, (funcionario[0],))
        
        func_with_esp = cursor.fetchone()
        print(f"Verificação final: {func_with_esp[1]} - Especialidade: {func_with_esp[2]}")
            
    except Exception as e:
        print(f"Erro: {e}")
        conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()