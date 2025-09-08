from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session, PaymentStatus
from src.models.pagamento import Payment, PaymentSession
from datetime import datetime, date
from sqlalchemy import func
import logging

# Configurar logger específico para pagamentos
logger = logging.getLogger('pagamentos')
logger.setLevel(logging.DEBUG)

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payments', methods=['GET'])
@login_and_subscription_required
def get_payments():
    """Lista todos os pagamentos do usuário logado"""
    logger.info("[GET /payments] Iniciando busca de pagamentos")
    try:
        current_user = get_current_user()
        logger.debug(f"[GET /payments] Usuário atual: {current_user.id if current_user else 'None'}")
        
        if not current_user:
            logger.warning("[GET /payments] Usuário não encontrado")
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        logger.debug(f"[GET /payments] Buscando pagamentos para user_id: {current_user.id}")
        payments = Payment.query.filter_by(user_id=current_user.id).join(Patient).order_by(Payment.data_pagamento.desc()).all()
        logger.info(f"[GET /payments] Encontrados {len(payments)} pagamentos")
        
        payments_data = []
        for payment in payments:
            payment_dict = payment.to_dict()
            payment_dict['patient_name'] = payment.patient.nome_completo
            payments_data.append(payment_dict)
        
        logger.info(f"[GET /payments] Retornando {len(payments_data)} pagamentos processados")
        return jsonify({
            'success': True,
            'data': payments_data
        })
    except Exception as e:
        logger.error(f"[GET /payments] Erro ao buscar pagamentos: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar pagamentos: {str(e)}'
        }), 500

@payments_bp.route('/payments/<int:payment_id>', methods=['GET'])
@login_and_subscription_required
def get_payment(payment_id):
    """Busca um pagamento específico com detalhes"""
    logger.info(f"[GET /payments/{payment_id}] Iniciando busca de pagamento específico")
    try:
        current_user = get_current_user()
        logger.debug(f"[GET /payments/{payment_id}] Usuário atual: {current_user.id if current_user else 'None'}")
        
        if not current_user:
            logger.warning(f"[GET /payments/{payment_id}] Usuário não encontrado")
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        logger.debug(f"[GET /payments/{payment_id}] Buscando pagamento para user_id: {current_user.id}")
        payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()
        
        if not payment:
            logger.warning(f"[GET /payments/{payment_id}] Pagamento não encontrado ou não autorizado")
            return jsonify({
                'success': False,
                'message': 'Pagamento não encontrado ou não autorizado'
            }), 404
        
        logger.info(f"[GET /payments/{payment_id}] Pagamento encontrado: {payment.id}")
        
        payment_data = payment.to_dict()
        payment_data['patient_name'] = payment.patient.nome_completo
        payment_data['patient'] = payment.patient.to_dict()
        
        logger.info(f"[GET /payments/{payment_id}] Retornando dados do pagamento processado")
        return jsonify({
            'success': True,
            'data': payment_data
        })
    except Exception as e:
        logger.error(f"[GET /payments/{payment_id}] Erro ao buscar pagamento: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar pagamento: {str(e)}'
        }), 500

@payments_bp.route('/payments', methods=['POST'])
@login_and_subscription_required
def create_payment():
    """Cria um novo pagamento e associa às sessões"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['patient_id', 'data_pagamento', 'valor_pago', 'session_ids']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório: {field}'
                }), 400
        
        # Verificar se paciente existe e pertence ao usuário
        patient = Patient.query.filter_by(id=data['patient_id'], user_id=current_user.id).first()
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Paciente não encontrado ou não autorizado'
            }), 404
        
        # Converter data do pagamento
        try:
            if isinstance(data['data_pagamento'], str):
                data_pagamento = datetime.strptime(data['data_pagamento'], '%Y-%m-%d').date()
            else:
                data_pagamento = data['data_pagamento']
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de data inválido. Use YYYY-MM-DD'
            }), 400
        
        # Validar valor
        if data['valor_pago'] <= 0:
            return jsonify({
                'success': False,
                'message': 'Valor pago deve ser maior que zero'
            }), 400
        
        # Validar sessões
        session_ids = data['session_ids']
        if not session_ids or not isinstance(session_ids, list):
            return jsonify({
                'success': False,
                'message': 'Deve ser fornecida pelo menos uma sessão'
            }), 400
        
        # Verificar se todas as sessões existem e pertencem ao paciente
        sessions = Session.query.join(Appointment).filter(
            Session.id.in_(session_ids),
            Appointment.patient_id == data['patient_id']
        ).all()
        
        if len(sessions) != len(session_ids):
            return jsonify({
                'success': False,
                'message': 'Uma ou mais sessões não foram encontradas ou não pertencem ao paciente'
            }), 400
        
        # Verificar se alguma sessão já está paga
        sessions_pagas = [s for s in sessions if s.status_pagamento == PaymentStatus.PAGO]
        if sessions_pagas:
            return jsonify({
                'success': False,
                'message': f'Sessão(ões) {[s.numero_sessao for s in sessions_pagas]} já estão pagas'
            }), 400
        
        # Criar pagamento
        payment = Payment(
            patient_id=data['patient_id'],
            user_id=current_user.id,
            data_pagamento=data_pagamento,
            valor_pago=data['valor_pago'],
            modalidade_pagamento=data.get('modalidade_pagamento'), # Novo campo
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(payment)
        db.session.flush()  # Para obter o ID do pagamento
        
        # Associar sessões ao pagamento
        for session in sessions:
            payment_session = PaymentSession(
                payment_id=payment.id,
                session_id=session.id
            )
            db.session.add(payment_session)
            
            # Marcar sessão como paga
            session.status_pagamento = PaymentStatus.PAGO
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento registrado com sucesso',
            'data': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar pagamento: {str(e)}'
        }), 500

@payments_bp.route('/payments/<int:payment_id>', methods=['PUT'])
@login_and_subscription_required
def update_payment(payment_id):
    """Atualiza um pagamento existente"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()
        if not payment:
            return jsonify({
                'success': False,
                'message': 'Pagamento não encontrado ou não autorizado'
            }), 404
            
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['patient_id', 'data_pagamento', 'valor_pago']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório: {field}'
                }), 400
        
        # Verificar se paciente existe e pertence ao usuário
        patient = Patient.query.filter_by(id=data['patient_id'], user_id=current_user.id).first()
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Paciente não encontrado ou não autorizado'
            }), 404
        
        # Converter data do pagamento
        try:
            if isinstance(data['data_pagamento'], str):
                data_pagamento = datetime.strptime(data['data_pagamento'], '%Y-%m-%d').date()
            else:
                data_pagamento = data['data_pagamento']
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de data inválido. Use YYYY-MM-DD'
            }), 400
        
        # Atualizar dados básicos
        payment.patient_id = data['patient_id']
        payment.data_pagamento = data_pagamento
        payment.valor_pago = data['valor_pago']
        payment.modalidade_pagamento = data.get('modalidade_pagamento', payment.modalidade_pagamento) # Novo campo
        payment.observacoes = data.get('observacoes', '')
        payment.updated_at = datetime.utcnow()
        
        # Se foram fornecidas novas sessões, atualizar associações
        if 'session_ids' in data:
            session_ids = data['session_ids']
            
            # Remover associações antigas e marcar sessões como pendentes
            for ps in payment.payment_sessions:
                ps.session.status_pagamento = PaymentStatus.PENDENTE
                db.session.delete(ps)
            
            # Verificar se todas as novas sessões existem e pertencem ao paciente
            sessions = Session.query.join(Appointment).filter(
                Session.id.in_(session_ids),
                Appointment.patient_id == data['patient_id']
            ).all()
            
            if len(sessions) != len(session_ids):
                return jsonify({
                    'success': False,
                    'message': 'Uma ou mais sessões não foram encontradas ou não pertencem ao paciente'
                }), 400
            
            # Criar novas associações
            for session in sessions:
                payment_session = PaymentSession(
                    payment_id=payment.id,
                    session_id=session.id
                )
                db.session.add(payment_session)
                
                # Marcar sessão como paga
                session.status_pagamento = PaymentStatus.PAGO
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento atualizado com sucesso',
            'data': payment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar pagamento: {str(e)}'
        }), 500

@payments_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
@login_and_subscription_required
def delete_payment(payment_id):
    """Remove um pagamento e marca sessões como pendentes"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        payment = Payment.query.filter_by(id=payment_id, user_id=current_user.id).first()
        if not payment:
            return jsonify({
                'success': False,
                'message': 'Pagamento não encontrado ou não autorizado'
            }), 404
        
        # Marcar todas as sessões associadas como pendentes
        for ps in payment.payment_sessions:
            ps.session.status_pagamento = PaymentStatus.PENDENTE
        
        db.session.delete(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir pagamento: {str(e)}'
        }), 500

@payments_bp.route('/patients/<int:patient_id>/sessions/unpaid', methods=['GET'])
@login_and_subscription_required
def get_unpaid_sessions(patient_id):
    """Lista sessões não pagas de um paciente"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Paciente não encontrado ou não autorizado'
            }), 404
        
        sessions = Session.query.join(Appointment).filter(
            Appointment.patient_id == patient_id,
            Session.status_pagamento == PaymentStatus.PENDENTE
        ).order_by(Session.data_sessao).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['appointment_id'] = session.appointment.id
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões não pagas: {str(e)}'
        }), 500

@payments_bp.route('/payments/quick', methods=['POST'])
@login_and_subscription_required
def create_quick_payment():
    """Cria um pagamento rápido para uma sessão específica"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['session_id', 'valor_pago']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório: {field}'
                }), 400
        
        # Buscar sessão e verificar se pertence ao usuário
        session = Session.query.join(Appointment).join(Patient).filter(
            Session.id == data['session_id'],
            Patient.user_id == current_user.id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Sessão não encontrada ou não autorizada'
            }), 404
        
        # Verificar se sessão já está paga
        if session.status_pagamento == PaymentStatus.PAGO:
            return jsonify({
                'success': False,
                'message': 'Sessão já está paga'
            }), 400
        
        # Usar data atual se não fornecida
        data_pagamento = date.today()
        if 'data_pagamento' in data:
            try:
                data_pagamento = datetime.strptime(data['data_pagamento'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de data inválido. Use YYYY-MM-DD'
                }), 400
        
        # Criar pagamento
        payment = Payment(
            patient_id=session.appointment.patient_id,
            user_id=current_user.id,
            data_pagamento=data_pagamento,
            valor_pago=data['valor_pago'],
            modalidade_pagamento=data.get('modalidade_pagamento'), # Novo campo
            observacoes=data.get('observacoes', f'Pagamento da sessão {session.numero_sessao}')
        )
        
        db.session.add(payment)
        db.session.flush()
        
        # Associar sessão ao pagamento
        payment_session = PaymentSession(
            payment_id=payment.id,
            session_id=session.id
        )
        db.session.add(payment_session)
        
        # Marcar sessão como paga
        session.status_pagamento = PaymentStatus.PAGO
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento registrado com sucesso',
            'data': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar pagamento: {str(e)}'
        }), 500



@payments_bp.route('/patients/<int:patient_id>/sessions/all', methods=['GET'])
@login_and_subscription_required
def get_all_sessions(patient_id):
    """Lista todas as sessões de um paciente (pagas e não pagas)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Paciente não encontrado ou não autorizado'
            }), 404
        
        sessions = Session.query.join(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Session.data_sessao).all()
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['appointment_id'] = session.appointment.id
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar sessões: {str(e)}'
        }), 500

