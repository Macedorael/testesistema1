from src.models.usuario import db
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session, SessionStatus, FrequencyType
from src.models.pagamento import Payment, PaymentMethod
from datetime import datetime, timedelta


def populate_db():
    print("Populando o banco de dados com dados de teste...")

    # Limpar dados existentes (opcional, para testes)
    # db.drop_all()
    # db.create_all()

    # Pacientes
    patient1 = Patient(
        nome_completo="João Silva",
        data_nascimento=datetime(1985, 10, 20),
        telefone="11987654321",
        cpf="12345678900",
        email="joao.silva@example.com",
        nome_contato_emergencia="Maria Silva",
        telefone_contato_emergencia="11999998888",
        grau_parentesco_emergencia="Mãe"
    )
    patient2 = Patient(
        nome_completo="Maria Oliveira",
        data_nascimento=datetime(1992, 5, 12),
        telefone="21987651234",
        cpf="09876543210",
        email="maria.oliveira@example.com",
        nome_contato_emergencia="Pedro Oliveira",
        telefone_contato_emergencia="21999997777",
        grau_parentesco_emergencia="Pai"
    )
    patient3 = Patient(
        nome_completo="Carlos Souza",
        data_nascimento=datetime(1978, 1, 30),
        telefone="31987655678",
        cpf="11223344556",
        email="carlos.souza@example.com"
    )
    db.session.add_all([patient1, patient2, patient3])
    db.session.commit()

    print(f"Adicionados {Patient.query.count()} pacientes.")

    # Agendamentos
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    # Agendamento para João Silva (semanal, 4 sessões)
    app1 = Appointment(
        patient_id=patient1.id,
        data_primeira_sessao=datetime.combine(today, datetime.min.time().replace(hour=10, minute=0)),
        quantidade_sessoes=4,
        frequencia=FrequencyType.SEMANAL,
        valor_por_sessao=150.00,
        observacoes="Agendamento semanal para João"
    )
    db.session.add(app1)
    db.session.commit()
    app1.generate_sessions()
    db.session.commit()

    # Agendamento para Maria Oliveira (quinzenal, 2 sessões)
    app2 = Appointment(
        patient_id=patient2.id,
        data_primeira_sessao=datetime.combine(today, datetime.min.time().replace(hour=14, minute=0)),
        quantidade_sessoes=2,
        frequencia=FrequencyType.QUINZENAL,
        valor_por_sessao=180.00,
        observacoes="Agendamento quinzenal para Maria"
    )
    db.session.add(app2)
    db.session.commit()
    app2.generate_sessions()
    db.session.commit()

    # Agendamento para Carlos Souza (mensal, 1 sessão)
    app3 = Appointment(
        patient_id=patient3.id,
        data_primeira_sessao=datetime.combine(today, datetime.min.time().replace(hour=16, minute=0)),
        quantidade_sessoes=1,
        frequencia=FrequencyType.MENSAL,
        valor_por_sessao=160.00,
        observacoes="Agendamento mensal para Carlos"
    )
    db.session.add(app3)
    db.session.commit()
    app3.generate_sessions()
    db.session.commit()

    print(f"Adicionados {Appointment.query.count()} agendamentos e {Session.query.count()} sessões.")

    # Atualizar status de algumas sessões para teste de dashboards
    # Sessão realizada
    session_realizada = Session.query.filter_by(appointment_id=app1.id, numero_sessao=1).first()
    if session_realizada:
        session_realizada.status = SessionStatus.REALIZADA
        db.session.add(session_realizada)

    # Sessão reagendada
    session_reagendada = Session.query.filter_by(appointment_id=app1.id, numero_sessao=2).first()
    if session_reagendada:
        session_reagendada.status = SessionStatus.REAGENDADA
        session_reagendada.data_original = session_reagendada.data_sessao
        session_reagendada.data_sessao = datetime.combine(tomorrow, datetime.min.time().replace(hour=11, minute=0))
        db.session.add(session_reagendada)

    # Sessão com falta
    session_faltou = Session.query.filter_by(appointment_id=app2.id, numero_sessao=1).first()
    if session_faltou:
        session_faltou.status = SessionStatus.FALTOU
        db.session.add(session_faltou)
    db.session.commit()

    # Pagamentos
    pay1 = Payment(
        patient_id=patient1.id,
        data_pagamento=datetime.now().date(),
        valor_pago=150.00,
        modalidade_pagamento=PaymentMethod.PIX,
        observacoes="Pagamento da sessão 1 do João"
    )
    db.session.add(pay1)
    db.session.commit()
    # Associar pagamento à sessão
    if session_realizada:
        from src.models.pagamento import PaymentSession
        ps1 = PaymentSession(payment_id=pay1.id, session_id=session_realizada.id)
        db.session.add(ps1)
        db.session.commit()

    pay2 = Payment(
        patient_id=patient2.id,
        data_pagamento=datetime.now().date(),
        valor_pago=180.00,
        modalidade_pagamento=PaymentMethod.CARTAO_CREDITO,
        observacoes="Pagamento da sessão 1 da Maria"
    )
    db.session.add(pay2)
    db.session.commit()

    pay3 = Payment(
        patient_id=patient1.id,
        data_pagamento=datetime.now().date() - timedelta(days=5),
        valor_pago=300.00,
        modalidade_pagamento=PaymentMethod.DINHEIRO,
        observacoes="Pagamento de 2 sessões antigas do João"
    )
    db.session.add(pay3)
    db.session.commit()

    print(f"Adicionados {Payment.query.count()} pagamentos.")

    print("População do banco de dados concluída.")

if __name__ == '__main__':
    from src.main import app
    with app.app_context():
        populate_db()


