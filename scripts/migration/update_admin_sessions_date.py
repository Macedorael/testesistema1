#!/usr/bin/env python3
"""
Script para atualizar as datas das sessões do admin para a data atual
"""

import sqlite3
import os
from datetime import datetime, date, time

def main():
    print("=== ATUALIZANDO DATAS DAS SESSÕES DO ADMIN ===")
    
    # Caminho do banco de dados
    database_path = os.path.join(os.path.dirname(__file__), 'instance', 'consultorio.db')
    
    if not os.path.exists(database_path):
        print(f"Banco de dados não encontrado em: {database_path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Encontrar o usuário admin
        cursor.execute("SELECT id, email FROM users WHERE email = 'admin@test.com'")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("Usuário admin não encontrado!")
            return
        
        admin_id = admin_user[0]
        print(f"Admin encontrado: ID {admin_id}, Email: {admin_user[1]}")
        
        # Encontrar sessões do admin
        cursor.execute("""
            SELECT s.id, s.data_sessao, a.id as appointment_id
            FROM sessions s
            JOIN appointments a ON s.appointment_id = a.id
            WHERE a.user_id = ?
        """, (admin_id,))
        
        admin_sessions = cursor.fetchall()
        print(f"Encontradas {len(admin_sessions)} sessões do admin")
        
        if not admin_sessions:
            print("Nenhuma sessão encontrada para o admin!")
            return
        
        # Data atual
        today = date.today()
        print(f"Data atual: {today}")
        
        # Atualizar as sessões
        for i, (session_id, old_date, appointment_id) in enumerate(admin_sessions):
            if i == 0:
                # Primeira sessão: hoje às 10:00
                new_datetime = datetime.combine(today, time(10, 0))
            else:
                # Segunda sessão: hoje às 14:00
                new_datetime = datetime.combine(today, time(14, 0))
            
            # Atualizar no banco
            cursor.execute("""
                UPDATE sessions 
                SET data_sessao = ? 
                WHERE id = ?
            """, (new_datetime.strftime('%Y-%m-%d %H:%M:%S'), session_id))
            
            print(f"Sessão ID {session_id}: {old_date} -> {new_datetime}")
        
        # Salvar mudanças
        conn.commit()
        print("\nSessões atualizadas com sucesso!")
        
        # Verificar as mudanças
        print("\n=== VERIFICANDO SESSÕES ATUALIZADAS ===")
        cursor.execute("""
            SELECT s.id, s.data_sessao
            FROM sessions s
            JOIN appointments a ON s.appointment_id = a.id
            WHERE a.user_id = ?
        """, (admin_id,))
        
        updated_sessions = cursor.fetchall()
        for session_id, session_date in updated_sessions:
            print(f"Sessão ID {session_id}: {session_date}")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()