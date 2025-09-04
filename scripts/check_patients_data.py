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

print("=== DADOS DOS USUÁRIOS ===")
cursor.execute("SELECT id, username FROM user")
users = cursor.fetchall()
for user in users:
    print(f"User ID: {user[0]}, Username: {user[1]}")

print("\n=== DADOS DOS PACIENTES ===")
cursor.execute("SELECT id, nome_completo, user_id FROM patients")
patients = cursor.fetchall()
for patient in patients:
    print(f"Patient ID: {patient[0]}, Nome: {patient[1]}, User_ID: {patient[2]}")

print("\n=== DADOS DOS AGENDAMENTOS ===")
cursor.execute("SELECT id, patient_id, user_id FROM appointments")
appointments = cursor.fetchall()
for appointment in appointments:
    print(f"Appointment ID: {appointment[0]}, Patient_ID: {appointment[1]}, User_ID: {appointment[2]}")

print("\n=== DADOS DOS PAGAMENTOS ===")
cursor.execute("SELECT id, patient_id, user_id FROM payments")
payments = cursor.fetchall()
for payment in payments:
    print(f"Payment ID: {payment[0]}, Patient_ID: {payment[1]}, User_ID: {payment[2]}")

conn.close()
print("\nVerificação concluída!")