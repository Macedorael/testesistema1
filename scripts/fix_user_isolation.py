#!/usr/bin/env python3
"""
Script para corrigir o isolamento de dados por usuário em todas as rotas
"""

import os
import re

def fix_appointments_routes():
    """Corrige as rotas de appointments para incluir filtro por user_id"""
    file_path = os.path.join(os.path.dirname(__file__), 'routes', 'appointments.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup do arquivo original
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Substituições necessárias
    replacements = [
        # get_appointments - adicionar filtro por user_id
        (
            r'appointments = Appointment\.query\.join\(Patient\)\.order_by\(Appointment\.data_primeira_sessao\.desc\(\)\)\.all\(\)',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        appointments = Appointment.query.filter_by(user_id=current_user.id).join(Patient).order_by(Appointment.data_primeira_sessao.desc()).all()'''
        ),
        
        # get_appointment - adicionar filtro por user_id
        (
            r'appointment = Appointment\.query\.get_or_404\(appointment_id\)',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=current_user.id).first()
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Agendamento não encontrado ou não autorizado'
            }), 404'''
        ),
        
        # create_appointment - adicionar user_id
        (
            r'# Verificar se paciente existe\s+patient = Patient\.query\.get\(data\[\'patient_id\'\]\)',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Verificar se paciente existe e pertence ao usuário
        patient = Patient.query.filter_by(id=data['patient_id'], user_id=current_user.id).first()'''
        ),
        
        # create_appointment - adicionar user_id no objeto
        (
            r'appointment = Appointment\(\s+patient_id=data\[\'patient_id\'\],',
            '''appointment = Appointment(
            user_id=current_user.id,
            patient_id=data['patient_id'],'''
        ),
        
        # update_appointment - adicionar filtro por user_id
        (
            r'appointment = Appointment\.query\.get_or_404\(appointment_id\)',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=current_user.id).first()
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Agendamento não encontrado ou não autorizado'
            }), 404'''
        ),
        
        # update_appointment - verificar paciente
        (
            r'# Verificar se paciente existe\s+patient = Patient\.query\.get\(data\[\'patient_id\'\]\)',
            '''# Verificar se paciente existe e pertence ao usuário
        patient = Patient.query.filter_by(id=data['patient_id'], user_id=current_user.id).first()'''
        ),
        
        # delete_appointment - adicionar filtro por user_id
        (
            r'appointment = Appointment\.query\.get_or_404\(appointment_id\)',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=current_user.id).first()
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Agendamento não encontrado ou não autorizado'
            }), 404'''
        ),
        
        # update_session - adicionar filtro por user_id
        (
            r'session = Session\.query\.get_or_404\(session_id\)',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        session = Session.query.join(Appointment).filter(
            Session.id == session_id,
            Appointment.user_id == current_user.id
        ).first()
        if not session:
            return jsonify({
                'success': False,
                'message': 'Sessão não encontrada ou não autorizada'
            }), 404'''
        )
    ]
    
    # Aplicar substituições
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Salvar arquivo corrigido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arquivo {file_path} corrigido com isolamento por usuário")

def fix_dashboard_sessions_routes():
    """Corrige as rotas de dashboard_sessions para incluir filtro por user_id"""
    file_path = os.path.join(os.path.dirname(__file__), 'routes', 'dashboard_sessions.py')
    
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
    
    # Substituições necessárias para adicionar filtro por user_id em todas as queries
    replacements = [
        # get_sessions_stats - adicionar filtro por user_id
        (
            r'# Query base\s+sessions_query = Session\.query',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Query base com filtro por usuário
        sessions_query = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id)'''
        ),
        
        # Corrigir sessões de hoje
        (
            r'sessoes_hoje = Session\.query\.filter\(',
            '''sessoes_hoje = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,'''
        ),
        
        # Corrigir próximas sessões
        (
            r'proximas_sessoes = Session\.query\.filter\(',
            '''proximas_sessoes = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,'''
        ),
        
        # get_rescheduled_sessions - adicionar filtro por user_id
        (
            r'# Query base para sessões reagendadas\s+query = Session\.query\.join\(Appointment\)\.join\(Patient\)\.filter\(',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Query base para sessões reagendadas com filtro por usuário
        query = Session.query.join(Appointment).join(Patient).filter(
            Appointment.user_id == current_user.id,'''
        ),
        
        # get_missed_sessions - adicionar filtro por user_id
        (
            r'# Query base para sessões com falta\s+query = Session\.query\.join\(Appointment\)\.join\(Patient\)\.filter\(',
            '''current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Query base para sessões com falta com filtro por usuário
        query = Session.query.join(Appointment).join(Patient).filter(
            Appointment.user_id == current_user.id,'''
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
    """Executa todas as correções de isolamento por usuário"""
    print("Iniciando correção de isolamento por usuário...")
    
    try:
        fix_appointments_routes()
        fix_dashboard_sessions_routes()
        
        print("\n✅ Todas as correções de isolamento por usuário foram aplicadas com sucesso!")
        print("\n📋 Arquivos corrigidos:")
        print("- src/routes/appointments.py")
        print("- src/routes/dashboard_sessions.py")
        print("\n💾 Backups criados:")
        print("- src/routes/appointments.py.backup")
        print("- src/routes/dashboard_sessions.py.backup")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()