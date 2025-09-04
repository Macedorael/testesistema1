#!/usr/bin/env python3
"""
Script para corrigir o isolamento de dados por usuário nas rotas de dashboard
"""

import os
import re

def fix_dashboard_routes():
    """Corrige as rotas de dashboard para incluir filtro por user_id"""
    file_path = os.path.join(os.path.dirname(__file__), 'routes', 'dashboard.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup do arquivo original
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Adicionar import do get_current_user se não existir
    if 'get_current_user' not in content:
        content = content.replace(
            'from src.utils.auth import login_required',
            'from src.utils.auth import login_required, get_current_user'
        )
    
    # Substituições necessárias
    replacements = [
        # get_dashboard_stats - adicionar verificação de usuário e filtros
        (
            r'def get_dashboard_stats\(\):\s+"""Retorna estatísticas gerais do dashboard"""\s+try:',
            '''def get_dashboard_stats():
    """Retorna estatísticas gerais do dashboard"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401'''
        ),
        
        # Corrigir todas as queries de Session para incluir join com Appointment e filtro por user_id
        (
            r'sessions_realizadas = Session\.query\.filter\(Session\.status == SessionStatus\.REALIZADA\)\.count\(\)',
            'sessions_realizadas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.REALIZADA).count()'
        ),
        (
            r'sessions_agendadas = Session\.query\.filter\(Session\.status == SessionStatus\.AGENDADA\)\.count\(\)',
            'sessions_agendadas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.AGENDADA).count()'
        ),
        (
            r'sessions_canceladas = Session\.query\.filter\(Session\.status == SessionStatus\.CANCELADA\)\.count\(\)',
            'sessions_canceladas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.CANCELADA).count()'
        ),
        (
            r'sessions_faltou = Session\.query\.filter\(Session\.status == SessionStatus\.FALTOU\)\.count\(\)',
            'sessions_faltou = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.FALTOU).count()'
        ),
        (
            r'sessions_pagas = Session\.query\.filter\(Session\.status_pagamento == PaymentStatus\.PAGO\)\.count\(\)',
            'sessions_pagas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status_pagamento == PaymentStatus.PAGO).count()'
        ),
        (
            r'sessions_pendentes = Session\.query\.filter\(Session\.status_pagamento == PaymentStatus\.PENDENTE\)\.count\(\)',
            'sessions_pendentes = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status_pagamento == PaymentStatus.PENDENTE).count()'
        ),
        
        # Corrigir próximas sessões
        (
            r'proximas_sessoes = Session\.query\.filter\(',
            'proximas_sessoes = Session.query.join(Appointment).filter(\n            Appointment.user_id == current_user.id,'
        ),
        
        # Corrigir sessões hoje
        (
            r'sessoes_hoje = Session\.query\.filter\(',
            'sessoes_hoje = Session.query.join(Appointment).filter(\n            Appointment.user_id == current_user.id,'
        ),
        
        # Corrigir sessões realizadas hoje
        (
            r'sessoes_realizadas_hoje = Session\.query\.filter\(',
            'sessoes_realizadas_hoje = Session.query.join(Appointment).filter(\n            Appointment.user_id == current_user.id,'
        ),
        
        # Corrigir total sessões hoje
        (
            r'total_sessoes_hoje = Session\.query\.filter\(',
            'total_sessoes_hoje = Session.query.join(Appointment).filter(\n            Appointment.user_id == current_user.id,'
        ),
        
        # Corrigir query de pacientes
        (
            r'patients = Patient\.query\.all\(\)',
            'patients = Patient.query.filter_by(user_id=current_user.id).all()'
        ),
        
        # Corrigir query de appointments por paciente
        (
            r'total_appointments = Appointment\.query\.filter_by\(patient_id=patient\.id\)\.count\(\)',
            'total_appointments = Appointment.query.filter_by(patient_id=patient.id, user_id=current_user.id).count()'
        ),
        
        # get_monthly_stats - adicionar verificação de usuário
        (
            r'def get_monthly_stats\(\):\s+"""Retorna estatísticas mensais"""\s+try:',
            '''def get_monthly_stats():
    """Retorna estatísticas mensais"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401'''
        ),
        
        # Corrigir monthly_sessions
        (
            r'monthly_sessions = Session\.query\.filter\(',
            'monthly_sessions = Session.query.join(Appointment).filter(\n            Appointment.user_id == current_user.id,'
        )
    ]
    
    # Aplicar substituições
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {file_path} corrigido com isolamento por usuário")

def fix_dashboard_payments_routes():
    """Corrige as rotas de dashboard_payments para incluir filtro por user_id"""
    file_path = os.path.join(os.path.dirname(__file__), 'routes', 'dashboard_payments.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup do arquivo original
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Adicionar import do get_current_user se não existir
    if 'get_current_user' not in content:
        content = content.replace(
            'from src.utils.auth import login_required',
            'from src.utils.auth import login_required, get_current_user'
        )
    
    # Substituições necessárias
    replacements = [
        # get_payments_stats - adicionar verificação de usuário
        (
            r'def get_payments_stats\(\):\s+"""Retorna estatísticas de pagamentos"""\s+try:',
            '''def get_payments_stats():
    """Retorna estatísticas de pagamentos"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401'''
        ),
        
        # Corrigir query base de payments
        (
            r'# Query base\s+payments_query = Payment\.query',
            '''# Query base com filtro por usuário
        payments_query = Payment.query.filter_by(user_id=current_user.id)'''
        ),
        
        # Corrigir query base de sessions
        (
            r'sessions_query = Session\.query',
            'sessions_query = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id)'
        ),
        
        # get_recent_payments - adicionar verificação de usuário
        (
            r'def get_recent_payments\(\):\s+"""Retorna lista de pagamentos recentes"""\s+try:',
            '''def get_recent_payments():
    """Retorna lista de pagamentos recentes"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401'''
        ),
        
        # Corrigir query de recent payments
        (
            r'# Query base para pagamentos recentes\s+query = Payment\.query\.join\(Patient\)',
            '''# Query base para pagamentos recentes com filtro por usuário
        query = Payment.query.filter_by(user_id=current_user.id).join(Patient)'''
        )
    ]
    
    # Aplicar substituições
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {file_path} corrigido com isolamento por usuário")

def fix_patients_routes():
    """Corrige as rotas de patients que ainda não têm isolamento completo"""
    file_path = os.path.join(os.path.dirname(__file__), 'routes', 'patients.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup do arquivo original
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Substituições necessárias
    replacements = [
        # Corrigir query de appointments por paciente na função get_patient
        (
            r'total_appointments = Appointment\.query\.filter_by\(patient_id=patient_id\)\.count\(\)',
            'total_appointments = Appointment.query.filter_by(patient_id=patient_id, user_id=current_user.id).count()'
        ),
        
        # Corrigir verificação de paciente existente no update_patient
        (
            r'existing_patient = Patient\.query\.filter\(',
            'existing_patient = Patient.query.filter(\n            Patient.user_id == current_user.id,'
        )
    ]
    
    # Aplicar substituições
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {file_path} corrigido com isolamento por usuário")

def main():
    """Executa todas as correções de isolamento por usuário nos dashboards"""
    print("Iniciando correção de isolamento por usuário nos dashboards...")
    
    try:
        fix_dashboard_routes()
        fix_dashboard_payments_routes()
        fix_patients_routes()
        
        print("\n✅ Todas as correções de isolamento por usuário foram aplicadas com sucesso!")
        print("\n📋 Arquivos corrigidos:")
        print("- src/routes/dashboard.py")
        print("- src/routes/dashboard_payments.py")
        print("- src/routes/patients.py")
        print("\n💾 Backups criados:")
        print("- src/routes/dashboard.py.backup")
        print("- src/routes/dashboard_payments.py.backup")
        print("- src/routes/patients.py.backup")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()