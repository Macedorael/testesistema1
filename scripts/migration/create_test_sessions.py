#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar sessões de teste para hoje
para verificar se o dashboard exibe as especialidades corretamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app
from src.models.base import db
from src.models.funcionario import Funcionario
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session, SessionStatus, FrequencyType
from datetime import datetime, date

def create_test_sessions():
    """Cria sessões de teste para hoje"""
    with app.app_context():
        print("=== CRIANDO SESSÕES DE TESTE PARA HOJE ===\n")
        
        # Verificar se já existem pacientes
        patients = Patient.query.limit(3).all()
        if not patients:
            print("❌ Nenhum paciente encontrado. Criando pacientes de teste...")
            
            # Criar pacientes de teste
            patient1 = Patient(
                user_id=1,
                nome_completo="João Silva Teste",
                telefone="11987654321",
                email="joao.teste@example.com",
                data_nascimento=date(1985, 10, 20),
                observacoes="Paciente de teste"
            )
            patient2 = Patient(
                user_id=1,
                nome_completo="Carlos Souza",
                telefone="11987654322",
                email="carlos.teste@example.com",
                data_nascimento=date(1978, 1, 30),
                observacoes="Paciente de teste"
            )
            
            db.session.add_all([patient1, patient2])
            db.session.commit()
            patients = [patient1, patient2]
            print(f"✅ Criados {len(patients)} pacientes de teste")
        
        # Verificar funcionários
        funcionarios = Funcionario.query.all()
        print(f"Funcionários disponíveis: {len(funcionarios)}")
        for func in funcionarios:
            print(f"  - {func.nome} (ID: {func.id}, Especialidade ID: {func.especialidade_id})")
        
        # Criar agendamentos para hoje
        today = datetime.now()
        today_10am = today.replace(hour=10, minute=0, second=0, microsecond=0)
        today_2pm = today.replace(hour=14, minute=0, second=0, microsecond=0)
        
        # Agendamento 1: João Silva com Dr. João Silva
        appointment1 = Appointment(
            user_id=1,
            patient_id=patients[0].id,
            funcionario_id=funcionarios[0].id if funcionarios else None,
            data_primeira_sessao=today_10am,
            quantidade_sessoes=1,
            frequencia=FrequencyType.SEMANAL,
            valor_por_sessao=150.00,
            observacoes="Sessão de teste para hoje"
        )
        
        db.session.add(appointment1)
        db.session.commit()
        
        # Gerar sessão
        appointment1.generate_sessions()
        db.session.commit()
        
        # Agendamento 2: Carlos Souza com tadeu (se houver segundo funcionário)
        if len(funcionarios) > 1 and len(patients) > 1:
            appointment2 = Appointment(
                user_id=1,
                patient_id=patients[1].id,
                funcionario_id=funcionarios[1].id,
                data_primeira_sessao=today_2pm,
                quantidade_sessoes=1,
                frequencia=FrequencyType.SEMANAL,
                valor_por_sessao=150.00,
                observacoes="Sessão de teste para hoje"
            )
            
            db.session.add(appointment2)
            db.session.commit()
            
            # Gerar sessão
            appointment2.generate_sessions()
            db.session.commit()
        
        # Verificar sessões criadas
        sessions_today = Session.query.join(
            Appointment, Session.appointment_id == Appointment.id
        ).filter(
            db.func.date(Session.data_sessao) == date.today()
        ).all()
        
        print(f"\n✅ Sessões criadas para hoje: {len(sessions_today)}")
        for session in sessions_today:
            appointment = session.appointment
            funcionario = appointment.funcionario
            patient = appointment.patient
            
            print(f"  - Sessão ID: {session.id}")
            print(f"    Paciente: {patient.nome_completo}")
            print(f"    Funcionário: {funcionario.nome if funcionario else 'Não definido'}")
            print(f"    Horário: {session.data_sessao.strftime('%H:%M')}")
            print(f"    Status: {session.status.value}")
            print()
        
        print("=== SESSÕES DE TESTE CRIADAS COM SUCESSO ===")

if __name__ == "__main__":
    create_test_sessions()