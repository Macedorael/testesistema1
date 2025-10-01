#!/usr/bin/env python3
"""
Script para debugar o problema de especialidades não sendo recuperadas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar diretamente o app do main.py
from src.main import app
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from src.models.consulta import Session, Appointment
from src.models.usuario import db
from datetime import date

def debug_especialidades():
    with app.app_context():
        print("=== DEBUG ESPECIALIDADES ===")
        
        # 1. Verificar funcionários
        print("\n1. FUNCIONÁRIOS:")
        funcionarios = Funcionario.query.all()
        for func in funcionarios:
            print(f"  ID: {func.id}, Nome: {func.nome}, Especialidade_ID: {func.especialidade_id}")
            if func.especialidade_id:
                try:
                    especialidade = Especialidade.query.get(func.especialidade_id)
                    if especialidade:
                        print(f"    -> Especialidade: {especialidade.nome}")
                    else:
                        print(f"    -> ERRO: Especialidade ID {func.especialidade_id} não encontrada!")
                except Exception as e:
                    print(f"    -> ERRO ao buscar especialidade: {e}")
        
        # 2. Verificar especialidades
        print("\n2. ESPECIALIDADES:")
        especialidades = Especialidade.query.all()
        for esp in especialidades:
            print(f"  ID: {esp.id}, Nome: {esp.nome}, User_ID: {esp.user_id}")
        
        # 3. Verificar relacionamento
        print("\n3. RELACIONAMENTO FUNCIONÁRIO-ESPECIALIDADE:")
        for func in funcionarios:
            print(f"  Funcionário: {func.nome}")
            try:
                if hasattr(func, 'especialidade'):
                    if func.especialidade:
                        print(f"    -> Especialidade via relacionamento: {func.especialidade.nome}")
                    else:
                        print(f"    -> Especialidade via relacionamento: None")
                else:
                    print(f"    -> Atributo 'especialidade' não existe")
            except Exception as e:
                print(f"    -> ERRO no relacionamento: {e}")
        
        # 4. Verificar sessões de hoje
        print("\n4. SESSÕES DE HOJE:")
        today = date.today()
        from sqlalchemy import func
        sessions = db.session.query(Session).join(Appointment).filter(
            func.date(Session.data_sessao) == today
        ).all()
        
        for session in sessions:
            print(f"  Sessão ID: {session.id}")
            print(f"    Appointment ID: {session.appointment.id}")
            print(f"    Funcionário ID: {session.appointment.funcionario_id}")
            if session.appointment.funcionario_id:
                func_obj = Funcionario.query.get(session.appointment.funcionario_id)
                if func_obj:
                    print(f"    Funcionário: {func_obj.nome}")
                    print(f"    Especialidade ID: {func_obj.especialidade_id}")
                    if func_obj.especialidade:
                        print(f"    Especialidade: {func_obj.especialidade.nome}")
                    else:
                        print(f"    Especialidade: None")

if __name__ == "__main__":
    debug_especialidades()