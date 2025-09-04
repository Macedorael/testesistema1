from flask import Blueprint, request, jsonify, session
from src.models.usuario import db, User
from src.models.assinatura import Subscription
from src.models.historico_assinatura import SubscriptionHistory
from src.utils.auth import login_required
from datetime import datetime

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('/plans', methods=['GET'])
def get_plans():
    """Retorna informações sobre todos os planos disponíveis"""
    try:
        plans = Subscription.get_plan_info()
        return jsonify({
            'success': True,
            'plans': plans
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/subscribe-guest', methods=['POST'])
def create_subscription_guest():
    """Permite que usuários não logados criem assinatura fornecendo credenciais"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        plan_type = data.get('plan_type')
        auto_renew = data.get('auto_renew', True)
        
        if not email or not password or not plan_type:
            return jsonify({'error': 'Email, senha e tipo de plano são obrigatórios'}), 400
        
        # Verificar se o usuário existe
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        # Validar tipo de plano
        if plan_type not in Subscription.PLAN_PRICES:
            return jsonify({
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, annual'
            }), 400
        
        # Verificar se já tem assinatura ativa
        if user.has_active_subscription():
            return jsonify({
                'error': 'Usuário já possui uma assinatura ativa'
            }), 400
        
        # Cancelar todas as assinaturas ativas anteriores se existirem
        active_subscriptions = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).all()
        
        for sub in active_subscriptions:
            sub.cancel()
        
        # Criar nova assinatura
        subscription = Subscription(
            user_id=user.id,
            plan_type=plan_type,
            auto_renew=auto_renew
        )
        
        db.session.add(subscription)
        db.session.flush()  # Para obter o ID da assinatura
        
        # Registrar no histórico
        SubscriptionHistory.create_history_entry(
            user_id=user.id,
            action='created',
            plan_type=plan_type,
            price=subscription.price,
            subscription_id=subscription.id,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            details=f'Assinatura {plan_type} criada via guest'
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assinatura criada com sucesso! Agora você pode fazer login.',
            'subscription': subscription.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/my-subscription', methods=['GET'])
@login_required
def get_my_subscription():
    """Retorna a assinatura atual do usuário logado"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Buscar a assinatura ativa mais recente diretamente do banco
        active_subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).order_by(Subscription.created_at.desc()).first()
        
        if active_subscription:
            return jsonify({
                'success': True,
                'subscription': active_subscription.to_dict()
            }), 200
        else:
            return jsonify({
                'success': True,
                'subscription': None,
                'message': 'Usuário não possui assinatura ativa'
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/subscribe', methods=['POST'])
@login_required
def create_subscription():
    """Cria uma nova assinatura para o usuário"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se já tem assinatura ativa
        if user.has_active_subscription():
            return jsonify({
                'error': 'Usuário já possui uma assinatura ativa'
            }), 400
        
        data = request.json
        plan_type = data.get('plan_type')
        auto_renew = data.get('auto_renew', True)
        
        # Validar tipo de plano
        if plan_type not in Subscription.PLAN_PRICES:
            return jsonify({
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, annual'
            }), 400
        
        # Cancelar todas as assinaturas ativas anteriores
        active_subscriptions = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).all()
        
        for sub in active_subscriptions:
            sub.cancel()
            # Registrar cancelamento no histórico
            SubscriptionHistory.create_history_entry(
                user_id=user_id,
                action='cancelled',
                plan_type=sub.plan_type,
                price=sub.price,
                subscription_id=sub.id,
                details='Assinatura cancelada para criação de nova assinatura'
            )
        
        # Criar nova assinatura
        subscription = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            auto_renew=auto_renew
        )
        
        db.session.add(subscription)
        db.session.flush()  # Para obter o ID da assinatura
        
        # Registrar criação no histórico
        SubscriptionHistory.create_history_entry(
            user_id=user_id,
            action='created',
            plan_type=plan_type,
            price=subscription.price,
            subscription_id=subscription.id,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            details=f'Assinatura {plan_type} criada'
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assinatura criada com sucesso',
            'subscription': subscription.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/update', methods=['PUT'])
@login_required
def update_subscription():
    """Atualiza a assinatura do usuário (mudança de plano)"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user or not user.subscription:
            return jsonify({'error': 'Usuário não possui assinatura'}), 404
        
        data = request.json
        new_plan_type = data.get('plan_type')
        auto_renew = data.get('auto_renew')
        
        # Validar tipo de plano
        if new_plan_type and new_plan_type not in Subscription.PLAN_PRICES:
            return jsonify({
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, annual'
            }), 400
        
        subscription = user.subscription
        old_plan_type = subscription.plan_type
        old_price = subscription.price
        
        # Atualizar plano se fornecido
        if new_plan_type and new_plan_type != subscription.plan_type:
            subscription.plan_type = new_plan_type
            subscription.price = Subscription.PLAN_PRICES[new_plan_type]
            subscription.end_date = subscription.calculate_end_date()
        
        # Atualizar auto_renew se fornecido
        if auto_renew is not None:
            subscription.auto_renew = auto_renew
        
        subscription.updated_at = datetime.utcnow()
        
        # Registrar atualização no histórico
        details = []
        if new_plan_type and new_plan_type != old_plan_type:
            details.append(f'Plano alterado de {old_plan_type} para {new_plan_type}')
        if auto_renew is not None:
            details.append(f'Auto-renovação alterada para {auto_renew}')
        
        SubscriptionHistory.create_history_entry(
            user_id=user_id,
            action='updated',
            plan_type=subscription.plan_type,
            price=subscription.price,
            subscription_id=subscription.id,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            details='; '.join(details) if details else 'Assinatura atualizada'
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assinatura atualizada com sucesso',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancela a assinatura do usuário"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Cancelar todas as assinaturas ativas
        active_subscriptions = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).all()
        
        if not active_subscriptions:
            return jsonify({'error': 'Usuário não possui assinatura ativa'}), 404
        
        for subscription in active_subscriptions:
            subscription.cancel()
            
            # Registrar cancelamento no histórico
            SubscriptionHistory.create_history_entry(
                user_id=user_id,
                action='cancelled',
                plan_type=subscription.plan_type,
                price=subscription.price,
                subscription_id=subscription.id,
                details='Assinatura cancelada pelo usuário'
            )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assinatura cancelada com sucesso.',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/cancel-with-logout', methods=['POST'])
@login_required
def cancel_subscription_with_logout():
    """Cancela a assinatura do usuário e faz logout automático"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Cancelar todas as assinaturas ativas
        active_subscriptions = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).all()
        
        if not active_subscriptions:
            return jsonify({'error': 'Usuário não possui assinatura ativa'}), 404
        
        for subscription in active_subscriptions:
            subscription.cancel()
            
            # Registrar cancelamento no histórico
            SubscriptionHistory.create_history_entry(
                user_id=user_id,
                action='cancelled',
                plan_type=subscription.plan_type,
                price=subscription.price,
                subscription_id=subscription.id,
                details='Assinatura cancelada pelo usuário com logout'
            )
        
        db.session.commit()
        
        # Fazer logout automático após cancelar a assinatura
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Assinatura cancelada com sucesso. Você foi desconectado do sistema.',
            'logout': True,
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/renew', methods=['POST'])
@login_required
def renew_subscription():
    """Renova a assinatura do usuário"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user or not user.subscription:
            return jsonify({'error': 'Usuário não possui assinatura'}), 404
        
        subscription = user.subscription
        
        if subscription.renew():
            # Registrar renovação no histórico
            SubscriptionHistory.create_history_entry(
                user_id=user_id,
                action='renewed',
                plan_type=subscription.plan_type,
                price=subscription.price,
                subscription_id=subscription.id,
                start_date=subscription.start_date,
                end_date=subscription.end_date,
                details=f'Assinatura {subscription.plan_type} renovada automaticamente'
            )
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Assinatura renovada com sucesso',
                'subscription': subscription.to_dict()
            }), 200
        else:
            return jsonify({
                'error': 'Não foi possível renovar a assinatura. Verifique se a renovação automática está habilitada.'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/renew-with-plan', methods=['POST'])
@login_required
def renew_subscription_with_plan():
    """Renova a assinatura do usuário com um novo plano"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.json
        new_plan_type = data.get('plan_type')
        auto_renew = data.get('auto_renew', True)
        
        # Validar tipo de plano
        if new_plan_type not in Subscription.PLAN_PRICES:
            return jsonify({
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, annual'
            }), 400
        
        # Capturar informações do plano anterior para o histórico
        previous_plan_type = None
        previous_price = None
        
        # Cancelar todas as assinaturas ativas anteriores
        active_subscriptions = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).all()
        
        for sub in active_subscriptions:
            # Capturar dados do primeiro plano ativo (mais recente)
            if previous_plan_type is None:
                previous_plan_type = sub.plan_type
                previous_price = sub.price
            
            sub.cancel()
            # Registrar cancelamento no histórico
            SubscriptionHistory.create_history_entry(
                user_id=user_id,
                action='cancelled',
                plan_type=sub.plan_type,
                price=sub.price,
                subscription_id=sub.id,
                details='Assinatura cancelada para renovação com novo plano'
            )
        
        # Criar nova assinatura
        subscription = Subscription(
            user_id=user_id,
            plan_type=new_plan_type,
            auto_renew=auto_renew
        )
        
        db.session.add(subscription)
        db.session.flush()  # Para obter o ID da assinatura
        
        # Registrar criação no histórico com informações do plano anterior
        renewal_details = f'Assinatura renovada para plano {new_plan_type}'
        if previous_plan_type and previous_plan_type != new_plan_type:
            renewal_details = f'Assinatura renovada de {previous_plan_type} para {new_plan_type}'
        
        SubscriptionHistory.create_history_entry(
            user_id=user_id,
            action='renewed',
            plan_type=new_plan_type,
            price=subscription.price,
            subscription_id=subscription.id,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            details=renewal_details,
            previous_plan_type=previous_plan_type,
            previous_price=previous_price
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assinatura renovada com sucesso',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/status', methods=['GET'])
def get_subscription_status():
    """Retorna apenas o status da assinatura do usuário"""
    try:
        user_id = session.get('user_id')
        
        # Se não há usuário logado, retornar que não tem assinatura
        if not user_id:
            return jsonify({
                'success': True,
                'has_active_subscription': False,
                'subscription_status': 'no_user',
                'days_remaining': 0
            }), 200
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': True,
                'has_active_subscription': False,
                'subscription_status': 'user_not_found',
                'days_remaining': 0
            }), 200
        
        return jsonify({
            'success': True,
            'has_active_subscription': user.has_active_subscription(),
            'subscription_status': user.get_subscription_status(),
            'days_remaining': user.get_subscription_days_remaining()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_bp.route('/history', methods=['GET'])
@login_required
def get_subscription_history():
    """Retorna o histórico de assinaturas do usuário logado"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Buscar histórico do usuário
        history_query = SubscriptionHistory.query.filter_by(user_id=user_id).order_by(SubscriptionHistory.action_date.desc())
        
        # Aplicar paginação
        history_paginated = history_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Converter para dicionário e adicionar informações amigáveis
        history_items = []
        for item in history_paginated.items:
            item_dict = item.to_dict()
            item_dict['action_description'] = SubscriptionHistory.get_action_description(item.action)
            item_dict['plan_name'] = SubscriptionHistory.get_plan_name(item.plan_type)
            history_items.append(item_dict)
        
        return jsonify({
            'success': True,
            'history': history_items,
            'pagination': {
                'page': history_paginated.page,
                'pages': history_paginated.pages,
                'per_page': history_paginated.per_page,
                'total': history_paginated.total,
                'has_next': history_paginated.has_next,
                'has_prev': history_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500