#!/usr/bin/env python3
"""
Script para verificar sessões no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app
from src.models.consulta import Session, Appointment
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from src.models.paciente import Patient
from src.models.usuario import User
from datetime import datetime, date

def check_sessions_in_db():
    with app.app_context():
        print("=== VERIFICANDO SESSÕES NO BANCO DE DADOS ===\n")
        
        # Verificar usuário admin
        admin_user = User.query.filter_by(email="admin@consultorio.com").first()
        if not admin_user:
            print("❌ Usuário admin não encontrado!")
            return
        
        print(f"✅ Usuário admin encontrado: ID {admin_user.id}\n")
        
        # Verificar todas as sessões
        all_sessions = Session.query.all()
        print(f"Total de sessões no banco: {len(all_sessions)}\n")
        
        if not all_sessions:
            print("❌ Nenhuma sessão encontrada no banco de dados!")
            return
        
        # Verificar sessões de hoje
        today = date.today()
        today_sessions = Session.query.filter(
            Session.data_sessao == today
        ).all()
        
        print(f"Sessões para hoje ({today}): {len(today_sessions)}\n")
        
        # Verificar todas as sessões com detalhes
        print("=== DETALHES DE TODAS AS SESSÕES ===")
        for session in all_sessions:
            print(f"Sessão ID: {session.id}")
            print(f"Data: {session.data_sessao}")
            print(f"Status: {session.status}")
            
            # Verificar appointment
            if session.appointment:
                print(f"Appointment ID: {session.appointment.id}")
                print(f"User ID do appointment: {session.appointment.user_id}")
                
                # Verificar funcionário
                if session.appointment.funcionario:
                    funcionario = session.appointment.funcionario
                    print(f"Funcionário: {funcionario.nome}")
                    print(f"Funcionário User ID: {funcionario.user_id}")
                    
                    # Verificar especialidade
                    if funcionario.especialidade:
                        print(f"Especialidade: {funcionario.especialidade.nome}")
                    else:
                        print("❌ Funcionário sem especialidade!")
                else:
                    print("❌ Sessão sem funcionário!")
                
                # Verificar paciente
                if session.appointment.patient:
                    print(f"Paciente: {session.appointment.patient.nome_completo}")
                else:
                    print("❌ Sessão sem paciente!")
            else:
                print("❌ Sessão sem appointment!")
            
            print("-" * 50)
        
        # Verificar isolamento de dados
        print("\n=== VERIFICANDO ISOLAMENTO DE DADOS ===")
        admin_sessions = Session.query.join(Appointment).filter(
            Appointment.user_id == admin_user.id
        ).all()
        
        print(f"Sessões do usuário admin: {len(admin_sessions)}")
        
        if admin_sessions:
            print("Sessões do admin:")
            for session in admin_sessions:
                print(f"  - ID: {session.id}, Data: {session.data_sessao}, Status: {session.status}")

if __name__ == "__main__":
    check_sessions_in_db()