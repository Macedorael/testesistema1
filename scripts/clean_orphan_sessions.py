import sqlite3
import os

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')

if not os.path.exists(db_path):
    print(f"Banco de dados {db_path} não encontrado")
    exit(1)

# Conectar ao banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== LIMPANDO SESSÕES ÓRFÃS ===")

# Verificar sessões que referenciam agendamentos inexistentes
print("Verificando sessões órfãs...")
cursor.execute("""
    SELECT s.id, s.appointment_id 
    FROM sessions s 
    LEFT JOIN appointments a ON s.appointment_id = a.id 
    WHERE a.id IS NULL
""")
orphan_sessions = cursor.fetchall()

if orphan_sessions:
    print(f"Encontradas {len(orphan_sessions)} sessões órfãs:")
    for session in orphan_sessions:
        print(f"  Session ID: {session[0]}, Appointment ID: {session[1]}")
    
    # Remover sessões órfãs
    cursor.execute("""
        DELETE FROM sessions 
        WHERE appointment_id NOT IN (SELECT id FROM appointments)
    """)
    removed_sessions = cursor.rowcount
    print(f"Removidas {removed_sessions} sessões órfãs")
else:
    print("Nenhuma sessão órfã encontrada")

# Verificar payment_sessions órfãos
print("\nVerificando payment_sessions órfãos...")
cursor.execute("""
    SELECT ps.id, ps.session_id, ps.payment_id
    FROM payment_sessions ps 
    LEFT JOIN sessions s ON ps.session_id = s.id 
    LEFT JOIN payments p ON ps.payment_id = p.id 
    WHERE s.id IS NULL OR p.id IS NULL
""")
orphan_payment_sessions = cursor.fetchall()

if orphan_payment_sessions:
    print(f"Encontrados {len(orphan_payment_sessions)} payment_sessions órfãos")
    cursor.execute("""
        DELETE FROM payment_sessions 
        WHERE session_id NOT IN (SELECT id FROM sessions) 
           OR payment_id NOT IN (SELECT id FROM payments)
    """)
    removed_payment_sessions = cursor.rowcount
    print(f"Removidos {removed_payment_sessions} payment_sessions órfãos")
else:
    print("Nenhum payment_session órfão encontrado")

# Confirmar as mudanças
conn.commit()

print("\n=== DADOS APÓS LIMPEZA ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Tabela {table_name}: {count} registros")

conn.close()
print("\nLimpeza de sessões concluída!")