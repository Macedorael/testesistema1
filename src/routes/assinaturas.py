from flask import Blueprint, request, jsonify, session
from src.models.usuario import db, User
from src.models.assinatura import Subscription
from src.models.historico_assinatura import SubscriptionHistory
from src.utils.auth import login_required

# Importações do Mercado Pago com tratamento de erro melhorado
get_mercadopago_config = None
subscription_payment_handler = None

try:
    from src.utils.mercadopago_config import get_mercadopago_config
    from src.utils.subscription_payment_handler import subscription_payment_handler
    print("[DEBUG] Mercado Pago importado com sucesso")
except ImportError as e:
    print(f"[WARNING] Mercado Pago não disponível: {e}")
except Exception as e:
    print(f"[WARNING] Erro ao configurar Mercado Pago: {e}")

from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

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
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, anual'
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
        print(f"[DEBUG] Iniciando create_subscription")
        user_id = session.get('user_id')
        print(f"[DEBUG] user_id da sessão: {user_id}")
        
        user = User.query.get(user_id)
        print(f"[DEBUG] Usuário encontrado: {user is not None}")
        
        if not user:
            print(f"[DEBUG] Usuário não encontrado para ID: {user_id}")
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se já tem assinatura ativa
        print(f"[DEBUG] Verificando assinatura ativa...")
        has_active = user.has_active_subscription()
        print(f"[DEBUG] Tem assinatura ativa: {has_active}")
        
        if has_active:
            print(f"[DEBUG] Usuário já possui assinatura ativa")
            return jsonify({
                'error': 'Usuário já possui uma assinatura ativa'
            }), 400
        
        data = request.json
        print(f"[DEBUG] Dados recebidos: {data}")
        
        plan_type = data.get('plan_type')
        auto_renew = data.get('auto_renew', True)
        print(f"[DEBUG] plan_type: {plan_type}, auto_renew: {auto_renew}")
        
        # Validar tipo de plano
        print(f"[DEBUG] Validando tipo de plano...")
        print(f"[DEBUG] PLAN_PRICES disponíveis: {Subscription.PLAN_PRICES}")
        
        if plan_type not in Subscription.PLAN_PRICES:
            print(f"[DEBUG] Tipo de plano inválido: {plan_type}")
            return jsonify({
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, anual'
            }), 400
        
        # Usar transação para evitar condições de corrida
        print(f"[DEBUG] Iniciando operações de banco...")
        try:
            print(f"[DEBUG] Dentro da transação")
            # Cancelar todas as assinaturas ativas anteriores com lock
            active_subscriptions = db.session.query(Subscription).filter_by(
                user_id=user_id,
                status='active'
            ).filter(Subscription.end_date > datetime.utcnow()).with_for_update().all()
            
            print(f"[DEBUG] Assinaturas ativas encontradas: {len(active_subscriptions)}")
            
            for sub in active_subscriptions:
                print(f"[DEBUG] Cancelando assinatura ID: {sub.id}")
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
            print(f"[DEBUG] Criando nova assinatura...")
            subscription = Subscription(
                user_id=user_id,
                plan_type=plan_type,
                auto_renew=auto_renew
            )
            
            print(f"[DEBUG] Assinatura criada em memória")
            db.session.add(subscription)
            print(f"[DEBUG] Assinatura adicionada à sessão")
            db.session.flush()  # Para obter o ID da assinatura
            print(f"[DEBUG] Flush executado, ID da assinatura: {subscription.id}")
            
            # Verificar se foi criada corretamente
            if not subscription.id:
                print(f"[DEBUG] ERRO: Falha ao criar assinatura - ID não gerado")
                raise Exception("Falha ao criar assinatura")
            
            # Registrar criação no histórico
            print(f"[DEBUG] Registrando no histórico...")
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
            print(f"[DEBUG] Histórico registrado com sucesso")
            
            # Commit das alterações
            db.session.commit()
            print(f"[DEBUG] Commit realizado com sucesso")
            
        except Exception as e:
            print(f"[DEBUG] ERRO durante operações de banco: {str(e)}")
            db.session.rollback()
            raise e
        
        print(f"[DEBUG] Operações de banco concluídas com sucesso")
        return jsonify({
            'success': True,
            'message': 'Assinatura criada com sucesso',
            'subscription_id': subscription.id
        })
    except Exception as e:
        print(f"[DEBUG] ERRO na create_subscription: {str(e)}")
        print(f"[DEBUG] Tipo do erro: {type(e)}")
        import traceback
        print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor. Tente novamente.'}), 500

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
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, anual'
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
                'error': 'Tipo de plano inválido. Opções: monthly, quarterly, biannual, anual'
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

@subscriptions_bp.route('/create-payment-preference', methods=['POST'])
def create_payment_preference():
    """Cria preferência de pagamento para assinatura - APENAS para usuários logados"""
    try:
        logger.info("[PAYMENT] ========== INICIANDO CRIAÇÃO DE PREFERÊNCIA DE PAGAMENTO ==========")
        logger.info(f"[PAYMENT] Método da requisição: {request.method}")
        logger.info(f"[PAYMENT] Headers da requisição: {dict(request.headers)}")
        logger.info(f"[PAYMENT] Sessão atual: {dict(session)}")
        
        # Verificar se o usuário está logado
        if 'user_id' not in session:
            logger.warning("[PAYMENT] ❌ ERRO: Tentativa de pagamento sem usuário logado")
            logger.warning(f"[PAYMENT] Chaves na sessão: {list(session.keys())}")
            return jsonify({
                'success': False,
                'error': 'Usuário deve estar logado para realizar pagamentos'
            }), 401
        
        user_id = session['user_id']
        logger.info(f"[PAYMENT] ✅ Usuário logado encontrado: {user_id}")
        
        # Buscar dados do usuário logado
        from src.models.usuario import User
        logger.info(f"[PAYMENT] Buscando usuário no banco de dados...")
        user = User.query.get(user_id)
        if not user:
            logger.error(f"[PAYMENT] ❌ ERRO CRÍTICO: Usuário não encontrado no banco: {user_id}")
            logger.error(f"[PAYMENT] Query executada: User.query.get({user_id})")
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
        
        logger.info(f"[PAYMENT] ✅ Usuário encontrado no banco: email={user.email}, username={user.username}, id={user.id}")
        
        # Obter dados da requisição
        logger.info(f"[PAYMENT] Obtendo dados JSON da requisição...")
        data = request.get_json()
        logger.info(f"[PAYMENT] ✅ Dados recebidos: {data}")
        logger.info(f"[PAYMENT] Tipo dos dados: {type(data)}")
        logger.info(f"[PAYMENT] Content-Type: {request.content_type}")
        
        # Validar dados obrigatórios
        logger.info(f"[PAYMENT] Validando campos obrigatórios...")
        required_fields = ['plan_type']
        for field in required_fields:
            if not data.get(field):
                logger.error(f"[PAYMENT] ❌ ERRO: Campo obrigatório ausente: {field}")
                logger.error(f"[PAYMENT] Campos disponíveis nos dados: {list(data.keys()) if data else 'None'}")
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400
        
        plan_type = data['plan_type']
        user_email = user.email
        user_name = user.username
        
        logger.info(f"[PAYMENT] ✅ Validação concluída")
        logger.info(f"[PAYMENT] 📋 Dados para processamento:")
        logger.info(f"[PAYMENT]    - Plan Type: {plan_type}")
        logger.info(f"[PAYMENT]    - User Email: {user_email}")
        logger.info(f"[PAYMENT]    - User Name: {user_name}")
        logger.info(f"[PAYMENT]    - User ID: {user_id}")
        
        # Verificar se o Mercado Pago está configurado
        logger.info(f"[PAYMENT] Verificando configuração do Mercado Pago...")
        logger.info(f"[PAYMENT] subscription_payment_handler: {subscription_payment_handler}")
        logger.info(f"[PAYMENT] get_mercadopago_config: {get_mercadopago_config}")
        
        if subscription_payment_handler is None or get_mercadopago_config is None:
            logger.warning("[PAYMENT] ⚠️ Mercado Pago não configurado - modo desenvolvimento")
            logger.warning(f"[PAYMENT] Handler é None: {subscription_payment_handler is None}")
            logger.warning(f"[PAYMENT] Config é None: {get_mercadopago_config is None}")
            # Modo de desenvolvimento - retornar URL mock
            return jsonify({
                'success': True,
                'preference_url': 'http://localhost:5000/payment/success?collection_id=mock&status=approved&payment_type=credit_card',
                'message': 'Modo de desenvolvimento - Mercado Pago não configurado'
            })
        
        logger.info("[PAYMENT] ✅ Mercado Pago configurado corretamente")
        logger.info("[PAYMENT] 🚀 Chamando handler de pagamento...")
        
        # Usar o handler para criar o pagamento
        try:
            result = subscription_payment_handler.create_subscription_payment(
                user_id=user_id,
                plan_type=plan_type,
                email=user_email,
                name=user_name
            )
            logger.info(f"[PAYMENT] ✅ Handler executado com sucesso")
        except Exception as handler_error:
            logger.error(f"[PAYMENT] ❌ ERRO no handler: {str(handler_error)}")
            logger.exception(f"[PAYMENT] Stack trace do handler:")
            raise handler_error
        
        logger.info(f"[PAYMENT] 📊 Resultado do handler:")
        logger.info(f"[PAYMENT]    - Success: {result.get('success')}")
        logger.info(f"[PAYMENT]    - Error: {result.get('error')}")
        logger.info(f"[PAYMENT]    - Resultado completo: {result}")
        
        if not result['success']:
            logger.error(f"[PAYMENT] ❌ ERRO: Falha ao criar pagamento")
            logger.error(f"[PAYMENT] Erro retornado: {result['error']}")
            logger.error(f"[PAYMENT] Resultado completo: {result}")
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        logger.info(f"[PAYMENT] 🎉 SUCESSO: Preferência de pagamento criada!")
        logger.info(f"[PAYMENT] Assinatura ID: {result['subscription']['id']}")
        logger.info(f"[PAYMENT] Preference ID: {result.get('preference_id')}")
        logger.info(f"[PAYMENT] Init Point: {result.get('init_point')}")
        
        response_data = {
            'success': True,
            'subscription': result['subscription'],
            'preference': {
                'id': result['preference_id'],
                'init_point': result['init_point'],
                'sandbox_init_point': result.get('sandbox_init_point')
            }
        }
        
        logger.info(f"[PAYMENT] 📤 Retornando resposta: {response_data}")
        logger.info("[PAYMENT] ========== FIM DA CRIAÇÃO DE PREFERÊNCIA ==========\n")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"[PAYMENT] ❌ ERRO CRÍTICO: Exceção não tratada")
        logger.error(f"[PAYMENT] Tipo da exceção: {type(e).__name__}")
        logger.error(f"[PAYMENT] Mensagem: {str(e)}")
        logger.exception("[PAYMENT] Stack trace completo:")
        logger.error("[PAYMENT] ========== FIM COM ERRO ==========\n")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500