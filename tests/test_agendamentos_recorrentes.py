#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para o sistema de agendamentos recorrentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from src.models.consulta import Appointment, Session, FrequencyType
from src.models.usuario import db

def test_weekly_recurrence():
    """Testa recorrência semanal"""
    print("\n=== TESTE: Recorrência Semanal ===")
    
    # Data inicial: segunda-feira, 5 de fevereiro de 2024, 10:00
    start_date = datetime(2024, 2, 5, 10, 0)
    
    # Criar agendamento semanal com 4 sessões
    appointment = Appointment(
        user_id=1,
        patient_id=1,
        funcionario_id=1,
        data_primeira_sessao=start_date,
        quantidade_sessoes=4,
        frequencia=FrequencyType.SEMANAL,
        valor_por_sessao=100.00
    )
    
    # Salvar no banco para obter ID
    db.session.add(appointment)
    db.session.commit()
    
    # Gerar sessões
    appointment.generate_sessions()
    db.session.commit()
    
    # Datas esperadas (toda segunda-feira)
    expected_dates = [
        datetime(2024, 2, 5, 10, 0),   # Primeira sessão
        datetime(2024, 2, 12, 10, 0),  # Segunda sessão (+7 dias)
        datetime(2024, 2, 19, 10, 0),  # Terceira sessão (+14 dias)
        datetime(2024, 2, 26, 10, 0),  # Quarta sessão (+21 dias)
    ]
    
    print(f"Sessões geradas: {len(appointment.sessions)}")
    success = True
    for i, session in enumerate(appointment.sessions):
        expected = expected_dates[i]
        actual = session.data_sessao
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            success = False
        print(f"Sessão {i+1}: {actual.strftime('%d/%m/%Y %H:%M')} (esperado: {expected.strftime('%d/%m/%Y %H:%M')}) {status}")
    
    # Limpar dados de teste
    for session in appointment.sessions:
        db.session.delete(session)
    db.session.delete(appointment)
    db.session.commit()
    
    return success and len(appointment.sessions) == 4

def test_biweekly_recurrence():
    """Testa recorrência quinzenal"""
    print("\n=== TESTE: Recorrência Quinzenal ===")
    
    # Data inicial: terça-feira, 6 de fevereiro de 2024, 14:00
    start_date = datetime(2024, 2, 6, 14, 0)
    
    # Criar agendamento quinzenal com 3 sessões
    appointment = Appointment(
        user_id=1,
        patient_id=1,
        funcionario_id=1,
        data_primeira_sessao=start_date,
        quantidade_sessoes=3,
        frequencia=FrequencyType.QUINZENAL,
        valor_por_sessao=120.00
    )
    
    # Salvar no banco para obter ID
    db.session.add(appointment)
    db.session.commit()
    
    # Gerar sessões
    appointment.generate_sessions()
    db.session.commit()
    
    # Datas esperadas (a cada 14 dias)
    expected_dates = [
        datetime(2024, 2, 6, 14, 0),   # Primeira sessão
        datetime(2024, 2, 20, 14, 0),  # Segunda sessão (+14 dias)
        datetime(2024, 3, 5, 14, 0),   # Terceira sessão (+28 dias)
    ]
    
    print(f"Sessões geradas: {len(appointment.sessions)}")
    success = True
    for i, session in enumerate(appointment.sessions):
        expected = expected_dates[i]
        actual = session.data_sessao
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            success = False
        print(f"Sessão {i+1}: {actual.strftime('%d/%m/%Y %H:%M')} (esperado: {expected.strftime('%d/%m/%Y %H:%M')}) {status}")
    
    # Limpar dados de teste
    for session in appointment.sessions:
        db.session.delete(session)
    db.session.delete(appointment)
    db.session.commit()
    
    return success and len(appointment.sessions) == 3

def test_monthly_recurrence():
    """Testa recorrência mensal (primeira segunda-feira do mês)"""
    print("\n=== TESTE: Recorrência Mensal (Primeira Segunda-feira do Mês) ===")
    
    # Data inicial: primeira segunda-feira de fevereiro de 2024
    start_date = datetime(2024, 2, 5, 9, 0)  # Segunda-feira, 5 de fevereiro de 2024, 09:00
    
    # Criar agendamento mensal com 4 sessões
    appointment = Appointment(
        user_id=1,
        patient_id=1,
        funcionario_id=1,
        data_primeira_sessao=start_date,
        quantidade_sessoes=4,
        frequencia=FrequencyType.MENSAL,
        valor_por_sessao=150.00
    )
    
    # Salvar no banco para obter ID
    db.session.add(appointment)
    db.session.commit()
    
    # Gerar sessões
    appointment.generate_sessions()
    db.session.commit()
    
    # Calcular as datas esperadas manualmente
    def get_first_monday_of_month(year, month):
        """Retorna a primeira segunda-feira do mês"""
        # Primeiro dia do mês
        first_day = datetime(year, month, 1)
        # Encontrar a primeira segunda-feira (weekday 0 = segunda-feira)
        days_until_monday = (0 - first_day.weekday()) % 7
        first_monday = first_day + timedelta(days=days_until_monday)
        return first_monday.replace(hour=9, minute=0, second=0, microsecond=0)
    
    expected_dates = [
        datetime(2024, 2, 5, 9, 0),    # Primeira sessão (primeira segunda-feira de fevereiro)
        get_first_monday_of_month(2024, 3),  # Primeira segunda-feira de março
        get_first_monday_of_month(2024, 4),  # Primeira segunda-feira de abril
        get_first_monday_of_month(2024, 5),  # Primeira segunda-feira de maio
    ]
    
    print(f"Sessões geradas: {len(appointment.sessions)}")
    success = True
    for i, session in enumerate(appointment.sessions):
        expected = expected_dates[i]
        actual = session.data_sessao
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            success = False
        print(f"Sessão {i+1}: {actual.strftime('%d/%m/%Y %H:%M')} (esperado: {expected.strftime('%d/%m/%Y %H:%M')}) {status}")
        print(f"  -> {actual.strftime('%A, %d de %B')} vs {expected.strftime('%A, %d de %B')}")
    
    # Limpar dados de teste
    for session in appointment.sessions:
        db.session.delete(session)
    db.session.delete(appointment)
    db.session.commit()
    
    return success and len(appointment.sessions) == 4

def run_tests_with_flask():
    """Executa todos os testes dentro do contexto da aplicação Flask"""
    print("🧪 INICIANDO TESTES DO SISTEMA DE AGENDAMENTOS RECORRENTES")
    print("=" * 60)
    
    # Importar e configurar a aplicação Flask
    from src.main import app
    
    with app.app_context():
        # Executar os testes
        results = {}
        
        try:
            results['semanal'] = test_weekly_recurrence()
        except Exception as e:
            print(f"❌ Erro no teste semanal: {e}")
            results['semanal'] = False
        
        try:
            results['quinzenal'] = test_biweekly_recurrence()
        except Exception as e:
            print(f"❌ Erro no teste quinzenal: {e}")
            results['quinzenal'] = False
        
        try:
            results['mensal'] = test_monthly_recurrence()
        except Exception as e:
            print(f"❌ Erro no teste mensal: {e}")
            results['mensal'] = False
        
        # Resumo dos resultados
        print("\n📊 RESUMO DOS TESTES")
        print("=" * 60)
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            test_display = {
                'semanal': 'Recorrência Semanal',
                'quinzenal': 'Recorrência Quinzenal', 
                'mensal': 'Recorrência Mensal'
            }
            print(f"{test_display[test_name]}: {status}")
            if result:
                passed += 1
        
        print(f"\nResultado Final: {passed}/{total} testes passaram")
        if passed == total:
            print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        else:
            print("⚠️  Alguns testes falharam. Verifique a implementação.")

if __name__ == "__main__":
    run_tests_with_flask()