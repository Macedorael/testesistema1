from datetime import date
from src.main import app
from src.models.usuario import User, db
from src.models.paciente import Patient

PAIENT_EMAIL = "paciente@teste.com"
PAIENT_USERNAME = "paciente"
PAIENT_PASSWORD = "123456"  # Senha inicial (será exigida troca no primeiro login)
PAIENT_TELEFONE = "(21) 99999-9999"
PAIENT_NOME = "Paciente Demo"
PAIENT_DATA_NASC = date(2000, 1, 1)

with app.app_context():
    # Verificar/crear usuário paciente
    user = User.query.filter_by(email=PAIENT_EMAIL).first()
    if not user:
        print("[CREATE] Criando usuário paciente...")
        user = User(
            username=PAIENT_USERNAME,
            email=PAIENT_EMAIL,
            telefone=PAIENT_TELEFONE,
            data_nascimento=PAIENT_DATA_NASC,
            role="patient",
            first_login=True
        )
        user.set_password(PAIENT_PASSWORD)
        db.session.add(user)
        db.session.flush()
        print(f"[OK] User criado: id={user.id}, email={user.email}, role={user.role}")
    else:
        print(f"[SKIP] Usuário já existe: id={user.id}, email={user.email}, role={user.role}")
        # Garantir role, senha e first_login corretos
        updated = False
        if user.role != "patient":
            user.role = "patient"
            updated = True
        # Forçar redefinição da senha e exigir primeiro login
        user.set_password(PAIENT_PASSWORD)
        user.first_login = True
        updated = True
        if updated:
            db.session.add(user)
            print("[UPDATE] Ajustado role/senha/first_login do usuário para paciente, senha reiniciada e primeiro login")

    # Vincular Patient ao profissional (owner)
    patient = Patient.query.filter_by(email=PAIENT_EMAIL).first()
    if not patient:
        owner = User.query.filter(User.role != "patient").order_by(User.id.asc()).first()
        if not owner:
            owner = User.query.order_by(User.id.asc()).first()
        if not owner:
            raise RuntimeError("Nenhum usuário proprietário encontrado para vincular o paciente.")
        print(f"[CREATE] Criando perfil Patient vinculado ao owner id={owner.id}")
        patient = Patient(
            user_id=owner.id,
            nome_completo=PAIENT_NOME,
            telefone=PAIENT_TELEFONE,
            email=PAIENT_EMAIL,
            data_nascimento=PAIENT_DATA_NASC,
            observacoes="Paciente de demonstração"
        )
        db.session.add(patient)
    else:
        print(f"[SKIP] Perfil Patient já existe: id={patient.id}, email={patient.email}, user_id={patient.user_id}")

    db.session.commit()
    print("\n✅ Paciente de demonstração pronto para login:")
    print(f"   Email: {PAIENT_EMAIL}")
    print(f"   Senha: {PAIENT_PASSWORD}")
    print("   • No primeiro login, será solicitado alterar a senha.")
    print("   • Após alterar, você será redirecionado ao dashboard do paciente.")