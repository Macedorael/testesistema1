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

print("=== DADOS DAS SESSÕES ===")
try:
    cursor.execute("SELECT * FROM sessions")
    sessions = cursor.fetchall()
    if sessions:
        cursor.execute("PRAGMA table_info(sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colunas: {columns}")
        for session in sessions:
            print(f"Session: {session}")
    else:
        print("Nenhuma sessão encontrada")
except Exception as e:
    print(f"Erro ao consultar sessions: {e}")

print("\n=== DADOS DOS PAYMENT_SESSIONS ===")
try:
    cursor.execute("SELECT * FROM payment_sessions")
    payment_sessions = cursor.fetchall()
    if payment_sessions:
        cursor.execute("PRAGMA table_info(payment_sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colunas: {columns}")
        for ps in payment_sessions:
            print(f"Payment Session: {ps}")
    else:
        print("Nenhum payment_session encontrado")
except Exception as e:
    print(f"Erro ao consultar payment_sessions: {e}")

print("\n=== VERIFICANDO TODAS AS TABELAS ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Tabela {table_name}: {count} registros")

conn.close()
print("\nVerificação concluída!")