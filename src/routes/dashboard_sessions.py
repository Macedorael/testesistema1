from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.consulta import Session, SessionStatus, Appointment
from src.models.paciente import Patient
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, case

dashboard_sessions_bp = Blueprint('dashboard_sessions', __name__)

@dashboard_sessions_bp.route('/dashboard/sessions/stats', methods=['GET'])
@login_and_subscription_required
def get_sessions_stats():
    """Retorna estatísticas gerais de sessões"""
    try:
        # Parâmetros de filtro de data
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Query base com filtro por usuário
        sessions_query = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id)
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            sessions_query = sessions_query.filter(func.date(Session.data_sessao) >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            sessions_query = sessions_query.filter(func.date(Session.data_sessao) <= date_to_obj)
        
        # Contadores por status
        total_sessoes = sessions_query.count()
        
        sessoes_agendadas = sessions_query.filter(
            Session.status == SessionStatus.AGENDADA
        ).count()
        
        sessoes_realizadas = sessions_query.filter(
            Session.status == SessionStatus.REALIZADA
        ).count()
        
        sessoes_canceladas = sessions_query.filter(
            Session.status == SessionStatus.CANCELADA
        ).count()
        
        sessoes_faltou = sessions_query.filter(
            Session.status == SessionStatus.FALTOU
        ).count()
        
        sessoes_reagendadas = sessions_query.filter(
            Session.status == SessionStatus.REAGENDADA
        ).count()
        
        # Sessões de hoje
        hoje = date.today()
        sessoes_hoje = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) == hoje,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).count()
        
        # Próximas sessões (próximos 7 dias)
        data_limite = hoje + timedelta(days=7)
        proximas_sessoes = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) > hoje,
            func.date(Session.data_sessao) <= data_limite,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_sessoes': total_sessoes,
                'sessoes_agendadas': sessoes_agendadas,
                'sessoes_realizadas': sessoes_realizadas,
                'sessoes_canceladas': sessoes_canceladas,
                'sessoes_faltou': sessoes_faltou,
                'sessoes_reagendadas': sessoes_reagendadas,
                'sessoes_hoje': sessoes_hoje,
                'proximas_sessoes': proximas_sessoes
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar estatísticas de sessões: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/rescheduled', methods=['GET'])
@login_and_subscription_required
def get_rescheduled_sessions():
    """Retorna lista de sessões reagendadas"""
    try:
        # Parâmetros de filtro de data
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 20, type=int)
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Query base para sessões reagendadas com filtro por usuário
        query = Session.query.join(Appointment).join(Patient).filter(
            Appointment.user_id == current_user.id,
            Session.status == SessionStatus.REAGENDADA
        )
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(func.date(Session.data_sessao) >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(func.date(Session.data_sessao) <= date_to_obj)
        
        # Ordenar por data de reagendamento mais recente
        sessions = query.order_by(Session.updated_at.desc()).limit(limit).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            # Adicionar nome do funcionário/psicólogo
            if session.appointment.funcionario:
                session_dict['funcionario_nome'] = session.appointment.funcionario.nome
            else:
                session_dict['funcionario_nome'] = 'Responsável pelo Atendimento'
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões reagendadas: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/missed', methods=['GET'])
@login_and_subscription_required
def get_missed_sessions():
    """Retorna lista de sessões com faltas"""
    try:
        # Parâmetros de filtro de data
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 20, type=int)
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Query base para sessões com falta com filtro por usuário
        query = Session.query.join(Appointment).join(Patient).filter(
            Appointment.user_id == current_user.id,
            Session.status == SessionStatus.FALTOU
        )
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(func.date(Session.data_sessao) >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(func.date(Session.data_sessao) <= date_to_obj)
        
        # Ordenar por data da sessão mais recente
        sessions = query.order_by(Session.data_sessao.desc()).limit(limit).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            # Adicionar nome do funcionário/psicólogo
            if session.appointment.funcionario:
                session_dict['funcionario_nome'] = session.appointment.funcionario.nome
            else:
                session_dict['funcionario_nome'] = 'Responsável pelo Atendimento'
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões com falta: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/today', methods=['GET'])
@login_and_subscription_required
def get_today_sessions():
    """Retorna sessões de hoje do psicólogo logado"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        hoje = date.today()
        
        sessions = Session.query.join(Appointment).join(Patient).filter(
            func.date(Session.data_sessao) == hoje,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA]),
            Appointment.user_id == current_user.id
        ).order_by(Session.data_sessao.asc()).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            
            # Adicionar nome do funcionário
            if session.appointment.funcionario:
                session_dict['funcionario_nome'] = session.appointment.funcionario.nome
                session_dict['psychologist_name'] = session.appointment.funcionario.nome
            else:
                session_dict['funcionario_nome'] = 'Responsável pelo Atendimento'
                session_dict['psychologist_name'] = 'Responsável pelo Atendimento'
            
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões de hoje: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/upcoming', methods=['GET'])
@login_and_subscription_required
def get_upcoming_sessions():
    """Retorna próximas sessões do psicólogo logado"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        limit = request.args.get('limit', 10, type=int)
        hoje = date.today()
        
        sessions = Session.query.join(Appointment).join(Patient).filter(
            func.date(Session.data_sessao) > hoje,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA]),
            Appointment.user_id == current_user.id
        ).order_by(Session.data_sessao.asc()).limit(limit).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            
            # Adicionar nome do funcionário
            if session.appointment.funcionario:
                session_dict['funcionario_nome'] = session.appointment.funcionario.nome
            else:
                session_dict['funcionario_nome'] = 'Responsável pelo Atendimento'
            
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar próximas sessões: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/by-status', methods=['GET'])
@login_and_subscription_required
def get_sessions_by_status():
    """Retorna sessões agrupadas por status"""
    try:
        # Parâmetros de filtro de data
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Query base
        query = db.session.query(
            Session.status,
            func.count(Session.id).label('quantidade')
        )
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(func.date(Session.data_sessao) >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(func.date(Session.data_sessao) <= date_to_obj)
        
        # Agrupar por status
        results = query.group_by(Session.status).all()
        
        # Processar resultados
        status_data = []
        for result in results:
            status_data.append({
                'status': result.status.value if result.status else 'Não informado',
                'quantidade': result.quantidade
            })
        
        return jsonify({
            'success': True,
            'data': status_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões por status: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/monthly-stats', methods=['GET'])
@login_and_subscription_required
def get_monthly_sessions_stats():
    """Retorna estatísticas mensais de sessões"""
    try:
        # Query para estatísticas mensais
        monthly_data = db.session.query(
            func.extract('year', Session.data_sessao).label('ano'),
            func.extract('month', Session.data_sessao).label('mes'),
            Session.status,
            func.count(Session.id).label('quantidade')
        ).group_by(
            func.extract('year', Session.data_sessao),
            func.extract('month', Session.data_sessao),
            Session.status
        ).order_by(
            func.extract('year', Session.data_sessao),
            func.extract('month', Session.data_sessao)
        ).limit(60).all()  # 12 meses * 5 status máximo
        
        # Processar dados
        stats_data = {}
        for data in monthly_data:
            periodo = f"{int(data.mes):02d}/{int(data.ano)}"
            if periodo not in stats_data:
                stats_data[periodo] = {
                    'ano': int(data.ano),
                    'mes': int(data.mes),
                    'periodo': periodo,
                    'agendadas': 0,
                    'realizadas': 0,
                    'canceladas': 0,
                    'faltou': 0,
                    'reagendadas': 0
                }
            
            status_key = data.status.value if data.status else 'outros'
            if status_key in stats_data[periodo]:
                stats_data[periodo][status_key] = data.quantidade
        
        # Converter para lista
        result = list(stats_data.values())
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar estatísticas mensais: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/patients/stats', methods=['GET'])
@login_and_subscription_required
def get_patients_stats():
    """Retorna estatísticas de pacientes do psicólogo"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
        
        # Total de pacientes únicos do psicólogo
        total_pacientes = db.session.query(Patient.id).join(
            Appointment, Patient.id == Appointment.patient_id
        ).filter(
            Appointment.user_id == current_user.id
        ).distinct().count()
        
        # Pacientes ativos (com sessões nos últimos 30 dias)
        from datetime import timedelta
        data_limite = date.today() - timedelta(days=30)
        
        pacientes_ativos = db.session.query(Patient.id).join(
            Appointment, Patient.id == Appointment.patient_id
        ).join(
            Session, Appointment.id == Session.appointment_id
        ).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) >= data_limite,
            Session.status.in_([SessionStatus.REALIZADA, SessionStatus.AGENDADA])
        ).distinct().count()
        
        # Pacientes com sessões hoje
        hoje = date.today()
        pacientes_hoje = db.session.query(Patient.id).join(
            Appointment, Patient.id == Appointment.patient_id
        ).join(
            Session, Appointment.id == Session.appointment_id
        ).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) == hoje,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).distinct().count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_pacientes': total_pacientes,
                'pacientes_ativos': pacientes_ativos,
                'pacientes_hoje': pacientes_hoje
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar estatísticas de pacientes: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/by-psychologist', methods=['GET'])
@login_and_subscription_required
def get_sessions_by_psychologist():
    """Retorna atendimentos agrupados por psicólogo"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
        
        # Buscar todos os funcionários/psicólogos que têm sessões
        from src.models.funcionario import Funcionario
        from src.models.especialidade import Especialidade
        
        # Buscar sessões agrupadas por funcionário
        funcionarios_query = db.session.query(
            Funcionario.id,
            Funcionario.nome,
            Especialidade.nome.label('especialidade_nome'),
            func.count(Session.id).label('total_sessoes'),
            func.sum(case((Session.status == SessionStatus.REALIZADA, 1), else_=0)).label('sessoes_realizadas'),
            func.sum(case((Session.status == SessionStatus.AGENDADA, 1), else_=0)).label('sessoes_agendadas'),
            func.sum(case((Session.status == SessionStatus.REAGENDADA, 1), else_=0)).label('sessoes_reagendadas'),
            func.sum(case((Session.status == SessionStatus.FALTOU, 1), else_=0)).label('sessoes_faltou'),
            func.sum(case((Session.status == SessionStatus.CANCELADA, 1), else_=0)).label('sessoes_canceladas')
        ).join(
            Appointment, Funcionario.id == Appointment.funcionario_id
        ).join(
            Session, Appointment.id == Session.appointment_id
        ).outerjoin(
            Especialidade, Funcionario.especialidade_id == Especialidade.id
        ).filter(
            Appointment.user_id == current_user.id
        ).group_by(
            Funcionario.id, Funcionario.nome, Especialidade.nome
        ).order_by(Funcionario.nome)
        
        funcionarios = funcionarios_query.all()
        
        # Também incluir sessões do próprio usuário (quando não há funcionário específico)
        user_sessions_query = db.session.query(
            func.count(Session.id).label('total_sessoes'),
            func.sum(case((Session.status == SessionStatus.REALIZADA, 1), else_=0)).label('sessoes_realizadas'),
            func.sum(case((Session.status == SessionStatus.AGENDADA, 1), else_=0)).label('sessoes_agendadas'),
            func.sum(case((Session.status == SessionStatus.REAGENDADA, 1), else_=0)).label('sessoes_reagendadas'),
            func.sum(case((Session.status == SessionStatus.FALTOU, 1), else_=0)).label('sessoes_faltou'),
            func.sum(case((Session.status == SessionStatus.CANCELADA, 1), else_=0)).label('sessoes_canceladas')
        ).join(
            Appointment, Session.appointment_id == Appointment.id
        ).filter(
            Appointment.user_id == current_user.id,
            Appointment.funcionario_id.is_(None)
        ).first()
        
        # Formatar dados dos funcionários
        funcionarios_data = []
        for funcionario in funcionarios:
            funcionarios_data.append({
                'id': funcionario.id,
                'nome': funcionario.nome,
                'especialidade': funcionario.especialidade_nome or 'Não informado',
                'total_sessoes': funcionario.total_sessoes or 0,
                'sessoes_realizadas': funcionario.sessoes_realizadas or 0,
                'sessoes_agendadas': funcionario.sessoes_agendadas or 0,
                'sessoes_reagendadas': funcionario.sessoes_reagendadas or 0,
                'sessoes_faltou': funcionario.sessoes_faltou or 0,
                'sessoes_canceladas': funcionario.sessoes_canceladas or 0
            })
        
        # Verificar se existem funcionários no sistema
        from src.models.funcionario import Funcionario
        has_funcionarios = Funcionario.query.filter_by(user_id=current_user.id).count() > 0
        
        # Adicionar dados do usuário principal apenas se houver sessões sem funcionário específico E não houver funcionários criados
        if (user_sessions_query and user_sessions_query.total_sessoes and user_sessions_query.total_sessoes > 0 and not has_funcionarios):
            funcionarios_data.append({
                'id': 'user_' + str(current_user.id),
                'nome': current_user.username,
                'especialidade': 'Responsável',
                'total_sessoes': user_sessions_query.total_sessoes or 0,
                'sessoes_realizadas': user_sessions_query.sessoes_realizadas or 0,
                'sessoes_agendadas': user_sessions_query.sessoes_agendadas or 0,
                'sessoes_reagendadas': user_sessions_query.sessoes_reagendadas or 0,
                'sessoes_faltou': user_sessions_query.sessoes_faltou or 0,
                'sessoes_canceladas': user_sessions_query.sessoes_canceladas or 0
            })
        
        return jsonify({
            'success': True,
            'data': funcionarios_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar atendimentos por psicólogo: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/sessions/upcoming-by-psychologist', methods=['GET'])
@login_and_subscription_required
def get_upcoming_sessions_by_psychologist():
    """Buscar sessões dos próximos 10 dias agrupadas por psicólogo"""
    try:
        current_user = get_current_user()
        
        # Data de hoje e próximos 10 dias
        today = date.today()
        end_date = today + timedelta(days=10)
        
        # Buscar todos os funcionários/psicólogos que têm sessões nos próximos 10 dias
        from src.models.funcionario import Funcionario
        from src.models.especialidade import Especialidade
        
        # Buscar sessões dos funcionários nos próximos 10 dias
        funcionarios_query = db.session.query(
            Funcionario.id,
            Funcionario.nome,
            Especialidade.nome.label('especialidade_nome'),
            Session.id.label('session_id'),
            Session.data_sessao,
            Session.status,
            Patient.nome_completo.label('paciente_nome'),
            Patient.telefone.label('paciente_telefone')
        ).join(
            Appointment, Funcionario.id == Appointment.funcionario_id
        ).join(
            Session, Appointment.id == Session.appointment_id
        ).join(
            Patient, Appointment.patient_id == Patient.id
        ).outerjoin(
            Especialidade, Funcionario.especialidade_id == Especialidade.id
        ).filter(
            Appointment.user_id == current_user.id,
            Session.data_sessao >= today,
            Session.data_sessao <= end_date,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).order_by(Funcionario.nome, Session.data_sessao)
        
        funcionarios_sessions = funcionarios_query.all()
        
        # Também incluir sessões do próprio usuário (quando não há funcionário específico)
        user_sessions_query = db.session.query(
            Session.id.label('session_id'),
            Session.data_sessao,
            Session.status,
            Patient.nome_completo.label('paciente_nome'),
            Patient.telefone.label('paciente_telefone')
        ).join(
            Appointment, Session.appointment_id == Appointment.id
        ).join(
            Patient, Appointment.patient_id == Patient.id
        ).filter(
            Appointment.user_id == current_user.id,
            Appointment.funcionario_id.is_(None),
            Session.data_sessao >= today,
            Session.data_sessao <= end_date,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).order_by(Session.data_sessao)
        
        user_sessions = user_sessions_query.all()
        
        # Agrupar sessões por funcionário
        funcionarios_data = {}
        for session in funcionarios_sessions:
            func_id = session.id
            if func_id not in funcionarios_data:
                funcionarios_data[func_id] = {
                    'id': session.id,
                    'nome': session.nome,
                    'especialidade': session.especialidade_nome or 'Não informado',
                    'sessoes': []
                }
            
            funcionarios_data[func_id]['sessoes'].append({
                'id': session.session_id,
                'data_sessao': session.data_sessao.strftime('%Y-%m-%d'),
                'horario': session.data_sessao.strftime('%H:%M') if session.data_sessao else None,
                'status': session.status.value,
                'paciente_nome': session.paciente_nome,
                'paciente_telefone': session.paciente_telefone
            })
        
        # Dados do usuário (sessões sem funcionário específico)
        # Só incluir se houver funcionários criados ou se o usuário tiver sessões
        user_sessions_count = len(user_sessions)
        
        # Verificar se existem funcionários no sistema
        from src.models.funcionario import Funcionario
        has_funcionarios = Funcionario.query.filter_by(user_id=current_user.id).count() > 0
        
        user_data = None
        if user_sessions_count > 0 and not has_funcionarios:
            # Só mostrar dados do usuário se não houver funcionários e houver sessões
            user_data = {
                'nome': 'Responsável pelo Atendimento',
                'especialidade': 'Responsável',
                'sessoes': []
            }
        
        if user_data:
            for session in user_sessions:
                user_data['sessoes'].append({
                    'id': session.session_id,
                    'data_sessao': session.data_sessao.strftime('%Y-%m-%d'),
                    'horario': session.data_sessao.strftime('%H:%M') if session.data_sessao else None,
                    'status': session.status.value,
                    'paciente_nome': session.paciente_nome,
                    'paciente_telefone': session.paciente_telefone
                })
        
        # Preparar dados finais
        result_data = []
        
        # Adicionar funcionários
        for funcionario in funcionarios_data.values():
            if funcionario['sessoes']:  # Só incluir se tiver sessões
                agendadas = len([s for s in funcionario['sessoes'] if s['status'] == 'agendada'])
                reagendadas = len([s for s in funcionario['sessoes'] if s['status'] == 'reagendada'])
                total = len(funcionario['sessoes'])
                
                result_data.append({
                    'nome': funcionario['nome'],
                    'especialidade': funcionario['especialidade'],
                    'total_sessoes': total,
                    'sessoes_agendadas': agendadas,
                    'sessoes_reagendadas': reagendadas,
                    'sessoes_detalhes': funcionario['sessoes']
                })
        
        # Adicionar sessões do usuário se houver
        if user_data and user_data['sessoes']:
            agendadas = len([s for s in user_data['sessoes'] if s['status'] == 'agendada'])
            reagendadas = len([s for s in user_data['sessoes'] if s['status'] == 'reagendada'])
            total = len(user_data['sessoes'])
            
            result_data.append({
                'nome': user_data['nome'],
                'especialidade': user_data['especialidade'],
                'total_sessoes': total,
                'sessoes_agendadas': agendadas,
                'sessoes_reagendadas': reagendadas,
                'sessoes_detalhes': user_data['sessoes']
            })
        
        return jsonify({
            'success': True,
            'data': result_data
        })
    except Exception as e:
        print(f"Erro ao buscar sessões futuras por psicólogo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_sessions_bp.route('/dashboard/patients/list', methods=['GET'])
@login_and_subscription_required
def get_patients_list():
    """Retorna lista de pacientes do psicólogo com informações de atendimentos"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
        
        # Buscar pacientes únicos do psicólogo com estatísticas
        pacientes_query = db.session.query(
            Patient.id,
            Patient.nome_completo,
            Patient.email,
            Patient.telefone,
            func.count(Session.id).label('total_sessoes'),
            func.sum(case((Session.status == SessionStatus.REALIZADA, 1), else_=0)).label('sessoes_realizadas'),
            func.sum(case((Session.status == SessionStatus.AGENDADA, 1), else_=0)).label('sessoes_agendadas'),
            func.max(Session.data_sessao).label('ultima_sessao')
        ).join(
            Appointment, Patient.id == Appointment.patient_id
        ).outerjoin(
            Session, Appointment.id == Session.appointment_id
        ).filter(
            Appointment.user_id == current_user.id
        ).group_by(
            Patient.id, Patient.nome_completo, Patient.email, Patient.telefone
        ).order_by(Patient.nome_completo)
        
        pacientes = pacientes_query.all()
        
        # Formatar dados
        pacientes_data = []
        for paciente in pacientes:
            pacientes_data.append({
                'id': paciente.id,
                'nome': paciente.nome_completo,
                'email': paciente.email,
                'telefone': paciente.telefone,
                'total_sessoes': paciente.total_sessoes or 0,
                'sessoes_realizadas': paciente.sessoes_realizadas or 0,
                'sessoes_agendadas': paciente.sessoes_agendadas or 0,
                'ultima_sessao': paciente.ultima_sessao.strftime('%Y-%m-%d') if paciente.ultima_sessao else None
            })
        
        return jsonify({
            'success': True,
            'data': pacientes_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar lista de pacientes: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/patients/by-psychologist', methods=['GET'])
@login_and_subscription_required
def get_patients_by_psychologist():
    """Retorna pacientes agrupados por psicólogo com sessões dos últimos 10 dias"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
        
        # Parâmetros de filtro
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        psychologist_id = request.args.get('psychologist_id')
        
        # Determinar qual psicólogo usar (filtrado ou atual)
        target_user_id = int(psychologist_id) if psychologist_id else current_user.id
        
        # Data limite para os últimos 10 dias
        data_limite = date.today() - timedelta(days=10)
        
        # Buscar todos os pacientes do psicólogo atual com estatísticas
        pacientes_query = db.session.query(
            Patient.id,
            Patient.nome_completo,
            Patient.email,
            Patient.telefone,
            Patient.data_nascimento,
            func.count(Session.id).label('total_sessoes'),
            func.sum(case((Session.status == SessionStatus.REALIZADA, 1), else_=0)).label('sessoes_realizadas'),
            func.sum(case((Session.status == SessionStatus.AGENDADA, 1), else_=0)).label('sessoes_agendadas'),
            func.max(Session.data_sessao).label('ultima_sessao')
        ).join(
            Appointment, Patient.id == Appointment.patient_id
        ).outerjoin(
            Session, Appointment.id == Session.appointment_id
        ).filter(
            Appointment.user_id == target_user_id
        ).group_by(
            Patient.id, Patient.nome_completo, Patient.email, Patient.telefone, Patient.data_nascimento
        ).order_by(Patient.nome_completo)
        
        pacientes = pacientes_query.all()
        
        # Buscar dados do psicólogo selecionado
        from src.models.usuario import User
        from src.models.funcionario import Funcionario
        target_user = User.query.get(target_user_id)
        if not target_user:
            return jsonify({'success': False, 'message': 'Psicólogo não encontrado'}), 404
        
        # Buscar funcionário associado ao usuário
        funcionario = Funcionario.query.filter_by(user_id=target_user_id).first()
        
        # Dados do psicólogo selecionado
        psicologo_data = {
            'id': target_user.id,
            'nome': funcionario.nome if funcionario else target_user.username,
            'especialidade': 'Psicólogo(a)',
            'total_pacientes': len(pacientes),
            'pacientes': []
        }
        
        for paciente in pacientes:
            # Buscar sessões dos últimos 10 dias para este paciente
            sessoes_recentes = Session.query.join(Appointment).filter(
                Appointment.patient_id == paciente.id,
                Appointment.user_id == target_user_id,
                func.date(Session.data_sessao) >= data_limite
            ).order_by(Session.data_sessao.desc()).all()
            
            # Converter sessões para dicionário
            sessoes_data = []
            for sessao in sessoes_recentes:
                sessao_dict = {
                    'id': sessao.id,
                    'data_sessao': sessao.data_sessao.strftime('%Y-%m-%d %H:%M') if sessao.data_sessao else None,
                    'status': sessao.status.value if sessao.status else None,
                    'observacoes': sessao.observacoes,
                    'valor': float(sessao.valor) if sessao.valor else None,
                    'numero_sessao': sessao.numero_sessao
                }
                sessoes_data.append(sessao_dict)
            
            psicologo_data['pacientes'].append({
                'id': paciente.id,
                'nome_completo': paciente.nome_completo,
                'email': paciente.email,
                'telefone': paciente.telefone,
                'data_nascimento': paciente.data_nascimento.strftime('%Y-%m-%d') if paciente.data_nascimento else None,
                'total_sessoes': paciente.total_sessoes or 0,
                'sessoes_realizadas': paciente.sessoes_realizadas or 0,
                'sessoes_agendadas': paciente.sessoes_agendadas or 0,
                'ultima_sessao': paciente.ultima_sessao.strftime('%Y-%m-%d') if paciente.ultima_sessao else None,
                'sessoes_ultimos_10_dias': sessoes_data
            })
        
        return jsonify({
            'success': True,
            'data': [psicologo_data]  # Retorna como array para manter consistência
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar pacientes por psicólogo: {str(e)}'
        }), 500

@dashboard_sessions_bp.route('/dashboard/psychologists/list', methods=['GET'])
@login_and_subscription_required
def get_psychologists_list():
    """Retorna lista de todos os psicólogos disponíveis"""
    try:
        from src.models.usuario import User
        from src.models.funcionario import Funcionario
        
        # Buscar todos os usuários que têm sessões ou pacientes
        psychologists = db.session.query(
            User.id,
            User.username,
            User.email
        ).join(
            Appointment, User.id == Appointment.user_id
        ).distinct().order_by(User.username).all()
        
        psychologists_data = []
        for psychologist in psychologists:
            # Buscar funcionário associado ao usuário
            funcionario = Funcionario.query.filter_by(user_id=psychologist.id).first()
            
            psychologists_data.append({
                'id': psychologist.id,
                'nome': funcionario.nome if funcionario else psychologist.username,
                'email': psychologist.email
            })
        
        return jsonify({
            'success': True,
            'data': psychologists_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar lista de psicólogos: {str(e)}'
        }), 500

