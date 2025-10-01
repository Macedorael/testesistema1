#!/usr/bin/env python3
"""
Script para debugar a relação session-funcionario no banco de dados
"""

import sqlite3
import os
from datetime import date

def main():
    print("=== DEBUG SESSION-FUNCIONARIO NO BANCO ===")
    
    # Conectar ao banco
    database_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    if not os.path.exists(database_path):
        print(f"❌ Banco não encontrado: {database_path}")
        return
    
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Verificar sessões de hoje
        today = date.today().strftime('%Y-%m-%d')
        print(f"Buscando sessões para: {today}")
        
        # Query completa com joins
        query = """
        SELECT 
            s.id as session_id,
            s.data_sessao,
            s.status,
            a.id as appointment_id,
            a.funcionario_id,
            f.nome as funcionario_nome,
            f.especialidade_id,
            e.nome as especialidade_nome,
            p.nome_completo as patient_name
        FROM sessions s
        JOIN appointments a ON s.appointment_id = a.id
        JOIN patients p ON a.patient_id = p.id
        LEFT JOIN funcionarios f ON a.funcionario_id = f.id
        LEFT JOIN especialidades e ON f.especialidade_id = e.id
        WHERE DATE(s.data_sessao) = ?
        ORDER BY s.data_sessao
        """
        
        cursor.execute(query, (today,))
        sessions = cursor.fetchall()
        
        print(f"\nEncontradas {len(sessions)} sessões para hoje:")
        
        for session in sessions:
            print(f"\n--- Sessão ID: {session[0]} ---")
            print(f"Data: {session[1]}")
            print(f"Status: {session[2]}")
            print(f"Appointment ID: {session[3]}")
            print(f"Funcionário ID: {session[4]}")
            print(f"Funcionário Nome: {session[5]}")
            print(f"Especialidade ID: {session[6]}")
            print(f"Especialidade Nome: {session[7]}")
            print(f"Paciente: {session[8]}")
            
            if session[4] is None:
                print("❌ PROBLEMA: funcionario_id é NULL!")
            else:
                print("✅ funcionario_id está definido")
        
        # Verificar appointments sem funcionario_id
        print("\n=== VERIFICANDO APPOINTMENTS SEM FUNCIONARIO_ID ===")
        cursor.execute("""
        SELECT a.id, a.funcionario_id, p.nome_completo
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.funcionario_id IS NULL
        """)
        
        null_funcionario = cursor.fetchall()
        print(f"Appointments sem funcionario_id: {len(null_funcionario)}")
        
        for app in null_funcionario:
            print(f"  - Appointment ID: {app[0]}, Paciente: {app[2]}")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()