from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session, SessionStatus, PaymentStatus
from src.models.pagamento import Payment
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@login_and_subscription_required
def get_dashboard_stats():
    """Retorna estatísticas gerais do consultório"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        # Estatísticas gerais
        total_patients = Patient.query.filter_by(user_id=current_user.id).count()
        total_appointments = Appointment.query.filter_by(user_id=current_user.id).count()
        total_sessions = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id).count()
        total_payments = Payment.query.filter_by(user_id=current_user.id).count()
        
        # Estatísticas financeiras
        total_recebido = db.session.query(func.sum(Payment.valor_pago)).filter(
            Payment.user_id == current_user.id
        ).scalar() or 0
        total_a_receber = db.session.query(func.sum(Session.valor)).join(Appointment).filter(
            Appointment.user_id == current_user.id,
            Session.status_pagamento == PaymentStatus.PENDENTE
        ).scalar() or 0
        
        # Estatísticas de sessões
        sessions_realizadas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.REALIZADA).count()
        sessions_agendadas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.AGENDADA).count()
        sessions_canceladas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.CANCELADA).count()
        sessions_faltou = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status == SessionStatus.FALTOU).count()
        
        sessions_pagas = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status_pagamento == PaymentStatus.PAGO).count()
        sessions_pendentes = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id, Session.status_pagamento == PaymentStatus.PENDENTE).count()
        
        # Próximas sessões (próximos 7 dias)
        next_week = datetime.now() + timedelta(days=7)
        proximas_sessoes = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,
            Session.data_sessao >= datetime.now(),
            Session.data_sessao <= next_week,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).count()
        
        # Sessões hoje
        today = date.today()
        sessoes_hoje = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) == today,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).count()
        
        # Sessões realizadas hoje
        sessoes_realizadas_hoje = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) == today,
            Session.status == SessionStatus.REALIZADA
        ).count()
        
        # Total de sessões agendadas para hoje (incluindo realizadas)
        total_sessoes_hoje = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) == today,
            (Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])) | (Session.status == SessionStatus.REALIZADA)
        ).count()
        
        # Sessões restantes hoje (agendadas - realizadas)
        sessoes_restantes_hoje = total_sessoes_hoje - sessoes_realizadas_hoje
        
        return jsonify({
            'success': True,
            'data': {
                'general': {
                    'total_patients': total_patients,
                    'total_appointments': total_appointments,
                    'total_sessions': total_sessions,
                    'total_payments': total_payments
                },
                'financial': {
                    'total_recebido': float(total_recebido),
                    'total_a_receber': float(total_a_receber),
                    'total_geral': float(total_recebido + total_a_receber)
                },
                'sessions': {
                    'realizadas': sessions_realizadas,
                    'agendadas': sessions_agendadas,
                    'canceladas': sessions_canceladas,
                    'faltou': sessions_faltou,
                    'pagas': sessions_pagas,
                    'pendentes': sessions_pendentes,
                    'proximas_7_dias': proximas_sessoes,
                    'hoje': sessoes_hoje,
                    'hoje_realizadas': sessoes_realizadas_hoje,
                    'hoje_total': total_sessoes_hoje,
                    'hoje_restantes': sessoes_restantes_hoje
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar estatísticas: {str(e)}'
        }), 500

@dashboard_bp.route('/dashboard/patients-summary', methods=['GET'])
@login_and_subscription_required
def get_patients_summary():
    """Retorna resumo detalhado por paciente"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        patients = Patient.query.filter_by(user_id=current_user.id).all()
        patients_summary = []
        
        for patient in patients:
            # Estatísticas do paciente
            total_appointments = Appointment.query.filter_by(patient_id=patient.id, user_id=current_user.id).count()
            total_sessions = Session.query.join(Appointment).filter(Appointment.patient_id == patient.id, Appointment.user_id == current_user.id).count()
            
            sessions_realizadas = Session.query.join(Appointment).filter(
                Appointment.patient_id == patient.id,
                Appointment.user_id == current_user.id,
                Session.status == SessionStatus.REALIZADA
            ).count()
            
            sessions_pagas = Session.query.join(Appointment).filter(
                Appointment.patient_id == patient.id,
                Appointment.user_id == current_user.id,
                Session.status_pagamento == PaymentStatus.PAGO
            ).count()
            
            total_pago = db.session.query(func.sum(Payment.valor_pago)).filter(
                Payment.patient_id == patient.id,
                Payment.user_id == current_user.id
            ).scalar() or 0
            total_a_receber = db.session.query(func.sum(Session.valor)).join(Appointment).filter(
                Appointment.patient_id == patient.id,
                Appointment.user_id == current_user.id,
                Session.status_pagamento == PaymentStatus.PENDENTE
            ).scalar() or 0
            
            # Próxima sessão
            proxima_sessao = Session.query.join(Appointment).filter(
                Appointment.patient_id == patient.id,
                Appointment.user_id == current_user.id,
                Session.data_sessao >= datetime.now(),
                Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
            ).order_by(Session.data_sessao).first()
            
            patients_summary.append({
                'patient': patient.to_dict(),
                'statistics': {
                    'total_appointments': total_appointments,
                    'total_sessions': total_sessions,
                    'sessions_realizadas': sessions_realizadas,
                    'sessions_pagas': sessions_pagas,
                    'sessions_pendentes': total_sessions - sessions_realizadas,
                    'sessions_em_aberto': total_sessions - sessions_pagas,
                    'total_pago': float(total_pago),
                    'total_a_receber': float(total_a_receber),
                    'proxima_sessao': proxima_sessao.to_dict() if proxima_sessao else None
                }
            })
        
        return jsonify({
            'success': True,
            'data': patients_summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar resumo de pacientes: {str(e)}'
        }), 500

@dashboard_bp.route('/dashboard/monthly-revenue', methods=['GET'])
@login_and_subscription_required
def get_monthly_revenue():
    """Retorna receita mensal dos últimos 12 meses"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        # Calcular últimos 12 meses
        current_date = date.today()
        monthly_data = []
        
        for i in range(12):
            # Calcular mês e ano
            month = current_date.month - i
            year = current_date.year
            
            if month <= 0:
                month += 12
                year -= 1
            
            # Buscar pagamentos do mês
            monthly_payments = db.session.query(func.sum(Payment.valor_pago)).filter(
                Payment.user_id == current_user.id,
                extract('month', Payment.data_pagamento) == month,
                extract('year', Payment.data_pagamento) == year
            ).scalar() or 0
            
            # Buscar sessões realizadas do mês
            monthly_sessions = Session.query.join(Appointment).filter(
            Appointment.user_id == current_user.id,
                extract('month', Session.data_sessao) == month,
                extract('year', Session.data_sessao) == year,
                Session.status == SessionStatus.REALIZADA
            ).count()
            
            monthly_data.append({
                'month': month,
                'year': year,
                'month_name': datetime(year, month, 1).strftime('%B'),
                'revenue': float(monthly_payments),
                'sessions': monthly_sessions
            })
        
        # Reverter para ordem cronológica
        monthly_data.reverse()
        
        return jsonify({
            'success': True,
            'data': monthly_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar receita mensal: {str(e)}'
        }), 500

@dashboard_bp.route('/dashboard/upcoming-sessions', methods=['GET'])
@login_and_subscription_required
def get_upcoming_sessions():
    """Retorna próximas sessões agendadas"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        limit = request.args.get('limit', 10, type=int)
        days_ahead = request.args.get('days', 30, type=int)
        
        end_date = datetime.now() + timedelta(days=days_ahead)
        
        sessions = Session.query.join(Appointment).join(Patient).filter(
            Appointment.user_id == current_user.id,
            Session.data_sessao >= datetime.now(),
            Session.data_sessao <= end_date,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).order_by(Session.data_sessao).limit(limit).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            session_dict['appointment_id'] = session.appointment.id
            
            # Adicionar informações do psicólogo responsável
            if session.appointment.funcionario_id:
                funcionario = session.appointment.funcionario
                session_dict['funcionario_nome'] = funcionario.nome if funcionario else 'Não definido'
                session_dict['funcionario_id'] = session.appointment.funcionario_id
            else:
                session_dict['funcionario_nome'] = 'Não definido'
                session_dict['funcionario_id'] = None
                
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

@dashboard_bp.route('/dashboard/today-sessions', methods=['GET'])
@login_and_subscription_required
def get_today_sessions():
    """Retorna sessões do dia com informações do psicólogo responsável"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        # Buscar sessões de hoje
        today = date.today()
        sessions = Session.query.join(Appointment).join(Patient).filter(
            Appointment.user_id == current_user.id,
            func.date(Session.data_sessao) == today,
            Session.status.in_([SessionStatus.AGENDADA, SessionStatus.REAGENDADA])
        ).order_by(Session.data_sessao).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            session_dict['appointment_id'] = session.appointment.id
            
            # Adicionar informações do psicólogo se disponível
            if hasattr(session.appointment, 'funcionario_id') and session.appointment.funcionario_id:
                from src.models.funcionario import Funcionario
                funcionario = Funcionario.query.get(session.appointment.funcionario_id)
                if funcionario:
                    session_dict['funcionario_nome'] = funcionario.nome
                    session_dict['funcionario_id'] = funcionario.id
                else:
                    session_dict['funcionario_nome'] = 'Não definido'
                    session_dict['funcionario_id'] = None
            else:
                session_dict['funcionario_nome'] = 'Não definido'
                session_dict['funcionario_id'] = None
                
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões do dia: {str(e)}'
        }), 500

@dashboard_bp.route('/dashboard/recent-payments', methods=['GET'])
@login_and_subscription_required
def get_recent_payments():
    """Retorna pagamentos recentes"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        limit = request.args.get('limit', 10, type=int)
        
        payments = Payment.query.join(Patient).filter(
            Payment.user_id == current_user.id
        ).order_by(Payment.data_pagamento.desc()).limit(limit).all()
        
        payments_data = []
        for payment in payments:
            payment_dict = payment.to_dict()
            payment_dict['patient_name'] = payment.patient.nome_completo
            payments_data.append(payment_dict)
        
        return jsonify({
            'success': True,
            'data': payments_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar pagamentos recentes: {str(e)}'
        }), 500

@dashboard_bp.route('/dashboard/overdue-sessions', methods=['GET'])
@login_and_subscription_required
def get_overdue_sessions():
    """Retorna sessões em atraso (não pagas)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401
            
        # Sessões realizadas mas não pagas há mais de 30 dias
        cutoff_date = datetime.now() - timedelta(days=30)
        
        sessions = Session.query.join(Appointment).join(Patient).filter(
            Appointment.user_id == current_user.id,
            Session.data_sessao <= cutoff_date,
            Session.status == SessionStatus.REALIZADA,
            Session.status_pagamento == PaymentStatus.PENDENTE
        ).order_by(Session.data_sessao).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            session_dict['days_overdue'] = (datetime.now() - session.data_sessao).days
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões em atraso: {str(e)}'
        }), 500


