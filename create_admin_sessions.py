#!/usr/bin/env python3
"""
Script para criar sessões de teste para o usuário admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app
from src.models.consulta import Session, Appointment, SessionStatus
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from src.models.paciente import Patient
from src.models.usuario import User
from datetime import datetime, date
from src.models.base import db

def create_admin_sessions():
    with app.app_context():
        print("=== CRIANDO SESSÕES PARA O USUÁRIO ADMIN ===\n")
        
        # Verificar usuário admin
        admin_user = User.query.filter_by(email="admin@consultorio.com").first()
        if not admin_user:
            print("❌ Usuário admin não encontrado!")
            return
        
        print(f"✅ Usuário admin encontrado: ID {admin_user.id}\n")
        
        # Verificar se já existem funcionários para este usuário
        funcionarios = Funcionario.query.filter_by(user_id=admin_user.id).all()
        
        if not funcionarios:
            print("Criando funcionários para o usuário admin...")
            
            # Buscar especialidades
            especialidade_medico = Especialidade.query.filter_by(nome="medico").first()
            especialidade_psicologia = Especialidade.query.filter_by(nome="Psicologia Clínica").first()
            
            if not especialidade_medico or not especialidade_psicologia:
                print("❌ Especialidades não encontradas!")
                return
            
            # Criar funcionários
            funcionario1 = Funcionario(
                nome="Dr. Admin Silva",
                user_id=admin_user.id,
                especialidade_id=especialidade_medico.id
            )
            
            funcionario2 = Funcionario(
                nome="Admin Psicólogo",
                user_id=admin_user.id,
                especialidade_id=especialidade_psicologia.id
            )
            
            db.session.add(funcionario1)
            db.session.add(funcionario2)
            db.session.commit()
            
            funcionarios = [funcionario1, funcionario2]
            print(f"✅ Funcionários criados: {len(funcionarios)}")
        else:
            print(f"✅ Funcionários já existem: {len(funcionarios)}")
        
        # Verificar se já existem pacientes para este usuário
        pacientes = Patient.query.filter_by(user_id=admin_user.id).all()
        
        if not pacientes:
            print("Criando pacientes para o usuário admin...")
            
            # Criar pacientes
            paciente1 = Patient(
                nome_completo="Carlos Admin Souza",
                telefone="(11) 99999-1111",
                email="carlos.admin@teste.com",
                data_nascimento=date(1990, 5, 15),
                user_id=admin_user.id
            )
            
            paciente2 = Patient(
                nome_completo="Maria Admin Silva",
                telefone="(11) 99999-2222",
                email="maria.admin@teste.com",
                data_nascimento=date(1985, 8, 20),
                user_id=admin_user.id
            )
            
            db.session.add(paciente1)
            db.session.add(paciente2)
            db.session.commit()
            
            pacientes = [paciente1, paciente2]
            print(f"✅ Pacientes criados: {len(pacientes)}")
        else:
            print(f"✅ Pacientes já existem: {len(pacientes)}")
        
        # Criar appointments
        today = date.today()
        
        # Appointment 1 - para hoje
        appointment1 = Appointment(
            user_id=admin_user.id,
            patient_id=pacientes[0].id,
            funcionario_id=funcionarios[0].id,
            data_primeira_sessao=datetime.combine(today, datetime.min.time().replace(hour=10)),
            quantidade_sessoes=1,
            valor_por_sessao=150.00
        )
        
        # Appointment 2 - para hoje
        appointment2 = Appointment(
            user_id=admin_user.id,
            patient_id=pacientes[1].id,
            funcionario_id=funcionarios[1].id,
            data_primeira_sessao=datetime.combine(today, datetime.min.time().replace(hour=14)),
            quantidade_sessoes=1,
            valor_por_sessao=120.00
        )
        
        db.session.add(appointment1)
        db.session.add(appointment2)
        db.session.commit()
        
        print(f"✅ Appointments criados")
        
        # Criar sessões para hoje
        session1 = Session(
            appointment_id=appointment1.id,
            data_sessao=datetime.combine(today, datetime.min.time().replace(hour=10)),
            numero_sessao=1,
            valor=150.00,  # Campo obrigatório
            status=SessionStatus.AGENDADA
        )
        
        session2 = Session(
            appointment_id=appointment2.id,
            data_sessao=datetime.combine(today, datetime.min.time().replace(hour=14)),
            numero_sessao=1,
            valor=150.00,  # Campo obrigatório
            status=SessionStatus.AGENDADA
        )
        
        db.session.add(session1)
        db.session.add(session2)
        db.session.commit()
        
        print(f"✅ Sessões criadas para hoje:")
        print(f"  - Sessão 1: {funcionarios[0].nome} ({funcionarios[0].especialidade.nome}) - {pacientes[0].nome_completo}")
        print(f"  - Sessão 2: {funcionarios[1].nome} ({funcionarios[1].especialidade.nome}) - {pacientes[1].nome_completo}")
        
        print("\n🎉 Sessões de teste criadas com sucesso para o usuário admin!")

if __name__ == "__main__":
    create_admin_sessions()