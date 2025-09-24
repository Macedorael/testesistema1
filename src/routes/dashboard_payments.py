from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.pagamento import Payment, PaymentMethod
from src.models.consulta import Session, PaymentStatus, Appointment
from src.models.paciente import Patient
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_

dashboard_payments_bp = Blueprint('dashboard_payments', __name__)

@dashboard_payments_bp.route('/dashboard/payments/stats', methods=['GET'])
@login_and_subscription_required
def get_payments_stats():
    """Retorna estatísticas gerais de pagamentos"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
            'success': False,
            'message': 'Usuário não encontrado'
        }), 401
            
        # Parâmetros de filtro de data
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Query base para pagamentos
        payments_query = Payment.query.filter_by(user_id=current_user.id)
        sessions_query = Session.query.join(Appointment).filter(Appointment.user_id == current_user.id)
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            payments_query = payments_query.filter(Payment.data_pagamento >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            payments_query = payments_query.filter(Payment.data_pagamento <= date_to_obj)
        
        # Total recebido (soma de todos os pagamentos confirmados)
        total_recebido = payments_query.with_entities(
            func.coalesce(func.sum(Payment.valor_pago), 0)
        ).scalar() or 0
        
        # Total a receber (soma dos pagamentos pendentes)
        total_a_receber = sessions_query.filter(
            Session.status_pagamento == PaymentStatus.PENDENTE
        ).with_entities(
            func.coalesce(func.sum(Session.valor), 0)
        ).scalar() or 0
        
        # Contadores gerais
        total_pagamentos = payments_query.count()
        total_sessoes_pendentes = sessions_query.filter(
            Session.status_pagamento == PaymentStatus.PENDENTE
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_recebido': float(total_recebido),
                'total_a_receber': float(total_a_receber),
                'total_pagamentos': total_pagamentos,
                'total_sessoes_pendentes': total_sessoes_pendentes
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar estatísticas de pagamentos: {str(e)}'
        }), 500

@dashboard_payments_bp.route('/dashboard/payments/by-modality', methods=['GET'])
@login_and_subscription_required
def get_payments_by_modality():
    """Retorna pagamentos agrupados por modalidade"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Parâmetros de filtro de data
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Query base com filtro de usuário
        query = db.session.query(
            Payment.modalidade_pagamento,
            func.count(Payment.id).label('quantidade'),
            func.coalesce(func.sum(Payment.valor_pago), 0).label('total_valor')
        ).filter(Payment.user_id == current_user.id)
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Payment.data_pagamento >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Payment.data_pagamento <= date_to_obj)
        
        # Agrupar por modalidade
        results = query.group_by(Payment.modalidade_pagamento).all()
        
        # Processar resultados
        modalidades = []
        total_geral = 0
        
        for result in results:
            # Acessar o valor do Enum corretamente
            modalidade = result.modalidade_pagamento.value if result.modalidade_pagamento else 'Não informado'
            quantidade = result.quantidade
            total_valor = float(result.total_valor)
            total_geral += total_valor
            
            modalidades.append({
                'modalidade': modalidade,
                'quantidade': quantidade,
                'total_valor': total_valor
            })
        
        # Ordenar por valor total (maior primeiro)
        modalidades.sort(key=lambda x: x['total_valor'], reverse=True)
        
        # Identificar modalidade com maior volume
        modalidade_maior_volume = modalidades[0] if modalidades else None
        
        return jsonify({
            'success': True,
            'data': {
                'modalidades': modalidades,
                'modalidade_maior_volume': modalidade_maior_volume,
                'total_geral': total_geral
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar pagamentos por modalidade: {str(e)}'
        }), 500

@dashboard_payments_bp.route('/dashboard/payments/monthly-revenue', methods=['GET'])
@login_and_subscription_required
def get_monthly_revenue():
    """Retorna receita mensal dos últimos 12 meses"""
    try:
        # Query para receita mensal
        monthly_data = db.session.query(
            func.extract('year', Payment.data_pagamento).label('ano'),
            func.extract('month', Payment.data_pagamento).label('mes'),
            func.coalesce(func.sum(Payment.valor_pago), 0).label('total')
        ).group_by(
            func.extract('year', Payment.data_pagamento),
            func.extract('month', Payment.data_pagamento)
        ).order_by(
            func.extract('year', Payment.data_pagamento),
            func.extract('month', Payment.data_pagamento)
        ).limit(12).all()
        
        # Processar dados
        revenue_data = []
        for data in monthly_data:
            revenue_data.append({
                'ano': int(data.ano),
                'mes': int(data.mes),
                'total': float(data.total),
                'periodo': f"{int(data.mes):02d}/{int(data.ano)}"
            })
        
        return jsonify({
            'success': True,
            'data': revenue_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar receita mensal: {str(e)}'
        }), 500

@dashboard_payments_bp.route('/dashboard/payments/recent', methods=['GET'])
@login_and_subscription_required
def get_recent_payments():
    """Retorna os pagamentos mais recentes"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        limit = request.args.get('limit', 10, type=int)
        
        payments = Payment.query.join(Patient).filter(
            Payment.user_id == current_user.id
        ).order_by(
            Payment.data_pagamento.desc(),
            Payment.created_at.desc()
        ).limit(limit).all()
        
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

@dashboard_payments_bp.route('/dashboard/payments/pending-sessions', methods=['GET'])
@login_and_subscription_required
def get_pending_sessions():
    """Retorna sessões pendentes de pagamento"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        limit = request.args.get('limit', 10, type=int)
        
        sessions = Session.query.join(
            Session.appointment
        ).join(
            Session.appointment.property.mapper.class_.patient
        ).filter(
            Session.status_pagamento == PaymentStatus.PENDENTE,
            Session.appointment.has(Appointment.user_id == current_user.id)
        ).order_by(
            Session.data_sessao.asc()
        ).limit(limit).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['patient_name'] = session.appointment.patient.nome_completo
            session_dict['patient_id'] = session.appointment.patient.id
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões pendentes: {str(e)}'
        }), 500

@dashboard_payments_bp.route('/dashboard/payments/daily-revenue', methods=['GET'])
@login_and_subscription_required
def get_daily_revenue():
    """Retorna receita diária dos últimos 30 dias"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Query para receita diária dos últimos 30 dias
        data_limite = date.today() - timedelta(days=30)
        daily_data = db.session.query(
            Payment.data_pagamento,
            func.coalesce(func.sum(Payment.valor_pago), 0).label('total')
        ).filter(
            Payment.user_id == current_user.id,
            Payment.data_pagamento >= data_limite
        ).group_by(
            Payment.data_pagamento
        ).order_by(
            Payment.data_pagamento
        ).all()
        
        # Processar dados
        revenue_data = []
        for data in daily_data:
            revenue_data.append({
                'data': data.data_pagamento.isoformat(),
                'total': float(data.total)
            })
        
        return jsonify({
            'success': True,
            'data': revenue_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar receita diária: {str(e)}'
        }), 500



