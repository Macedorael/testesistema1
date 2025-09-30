#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar o relacionamento SQLAlchemy entre Funcionário e Especialidade
após as correções aplicadas no dashboard.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import app
from src.models.base import db
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from src.models.consulta import Session, Appointment
from src.models.paciente import Patient
from sqlalchemy.orm import joinedload
from datetime import datetime, date

def test_especialidade_relationship():
    """Testa o relacionamento entre funcionário e especialidade"""
    with app.app_context():
        print("=== TESTE DO RELACIONAMENTO FUNCIONÁRIO-ESPECIALIDADE ===\n")
        
        # 1. Testar funcionários com especialidades
        print("1. Testando funcionários com especialidades:")
        funcionarios = Funcionario.query.options(joinedload(Funcionario.especialidade)).all()
        
        for funcionario in funcionarios:
            print(f"   Funcionário: {funcionario.nome} (ID: {funcionario.id})")
            print(f"   Especialidade ID: {funcionario.especialidade_id}")
            
            if hasattr(funcionario, 'especialidade') and funcionario.especialidade:
                print(f"   Especialidade Nome: {funcionario.especialidade.nome}")
                print(f"   ✅ Relacionamento funcionando")
            else:
                print(f"   ❌ Especialidade não carregada")
            print()
        
        # 2. Testar query similar à do dashboard
        print("2. Testando query similar ao dashboard (today-sessions):")
        today = date.today()
        
        sessions_query = db.session.query(Session).join(
            Appointment, Session.appointment_id == Appointment.id
        ).join(
            Patient, Appointment.patient_id == Patient.id
        ).join(
            Funcionario, Appointment.funcionario_id == Funcionario.id
        ).outerjoin(
            Especialidade, Funcionario.especialidade_id == Especialidade.id
        ).options(
            joinedload(Session.appointment).joinedload(Appointment.funcionario).joinedload(Funcionario.especialidade)
        ).filter(
            db.func.date(Appointment.data_primeira_sessao) == today
        )
        
        sessions = sessions_query.all()
        print(f"   Sessões encontradas para hoje: {len(sessions)}")
        
        for session in sessions:
            funcionario = session.appointment.funcionario
            print(f"   Sessão ID: {session.id}")
            print(f"   Funcionário: {funcionario.nome}")
            print(f"   Especialidade ID: {funcionario.especialidade_id}")
            
            if hasattr(funcionario, 'especialidade') and funcionario.especialidade:
                especialidade_nome = funcionario.especialidade.nome
                print(f"   Especialidade: {especialidade_nome}")
                print(f"   ✅ Relacionamento funcionando na query")
            else:
                print(f"   ❌ Especialidade não carregada na query")
            print()
        
        # 3. Testar acesso direto ao relacionamento
        print("3. Testando acesso direto ao relacionamento:")
        funcionario_test = Funcionario.query.first()
        if funcionario_test:
            print(f"   Funcionário teste: {funcionario_test.nome}")
            print(f"   Especialidade ID: {funcionario_test.especialidade_id}")
            
            try:
                # Tentar acessar a especialidade diretamente
                especialidade = funcionario_test.especialidade
                if especialidade:
                    print(f"   Especialidade: {especialidade.nome}")
                    print(f"   ✅ Acesso direto funcionando")
                else:
                    print(f"   ❌ Especialidade é None")
            except Exception as e:
                print(f"   ❌ Erro ao acessar especialidade: {e}")
        
        print("\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    test_especialidade_relationship()