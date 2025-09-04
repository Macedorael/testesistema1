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

print("=== LIMPANDO DADOS ÓRFÃOS ===")

# Remover pagamentos órfãos (sem user_id)
print("Removendo pagamentos órfãos...")
cursor.execute("DELETE FROM payments WHERE user_id IS NULL")
orphan_payments = cursor.rowcount
print(f"Removidos {orphan_payments} pagamentos órfãos")

# Remover agendamentos órfãos (sem user_id)
print("Removendo agendamentos órfãos...")
cursor.execute("DELETE FROM appointments WHERE user_id IS NULL")
orphan_appointments = cursor.rowcount
print(f"Removidos {orphan_appointments} agendamentos órfãos")

# Remover pacientes órfãos (sem user_id)
print("Removendo pacientes órfãos...")
cursor.execute("DELETE FROM patients WHERE user_id IS NULL")
orphan_patients = cursor.rowcount
print(f"Removidos {orphan_patients} pacientes órfãos")

# Confirmar as mudanças
conn.commit()

print("\n=== DADOS APÓS LIMPEZA ===")
print("\n=== USUÁRIOS ===")
cursor.execute("SELECT id, username FROM user")
users = cursor.fetchall()
for user in users:
    print(f"User ID: {user[0]}, Username: {user[1]}")

print("\n=== PACIENTES ===")
cursor.execute("SELECT id, nome_completo, user_id FROM patients")
patients = cursor.fetchall()
for patient in patients:
    print(f"Patient ID: {patient[0]}, Nome: {patient[1]}, User_ID: {patient[2]}")

print("\n=== AGENDAMENTOS ===")
cursor.execute("SELECT id, patient_id, user_id FROM appointments")
appointments = cursor.fetchall()
for appointment in appointments:
    print(f"Appointment ID: {appointment[0]}, Patient_ID: {appointment[1]}, User_ID: {appointment[2]}")

print("\n=== PAGAMENTOS ===")
cursor.execute("SELECT id, patient_id, user_id FROM payments")
payments = cursor.fetchall()
for payment in payments:
    print(f"Payment ID: {payment[0]}, Patient_ID: {payment[1]}, User_ID: {payment[2]}")

conn.close()
print("\nLimpeza concluída!")