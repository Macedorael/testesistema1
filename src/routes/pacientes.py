from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session, PaymentStatus
from src.models.pagamento import Payment
from src.models.diario import DiaryEntry
from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from datetime import datetime
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
import logging

# Configurar logger específico para pacientes
logger = logging.getLogger('pacientes')
logger.setLevel(logging.DEBUG)

patients_bp = Blueprint("patients", __name__)

@patients_bp.route("/patients", methods=["GET"])
@login_and_subscription_required
def get_patients():
    """Lista todos os pacientes do usuário logado"""
    logger.info("[GET /patients] Iniciando busca de pacientes")
    try:
        current_user = get_current_user()
        logger.debug(f"[GET /patients] Usuário atual: {current_user.id if current_user else 'None'}")
        
        if not current_user:
            logger.warning("[GET /patients] Usuário não encontrado")
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 401
            
        only_active = request.args.get('only_active') in ['1', 'true', 'True']
        logger.debug(f"[GET /patients] Buscando pacientes para user_id: {current_user.id} | only_active={only_active}")
        query = Patient.query.filter_by(user_id=current_user.id)
        if only_active:
            query = query.filter(Patient.ativo == True)
        patients = query.order_by(Patient.nome_completo).all()
        logger.info(f"[GET /patients] Encontrados {len(patients)} pacientes")
        
        patients_data = [patient.to_dict() for patient in patients]
        logger.info(f"[GET /patients] Retornando {len(patients_data)} pacientes processados")
        return jsonify({
            "success": True,
            "data": patients_data
        })
    except Exception as e:
        logger.error(f"[GET /patients] Erro ao buscar pacientes: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar pacientes: {str(e)}"
        }), 500

@patients_bp.route("/patients/<int:patient_id>", methods=["GET"])
@login_and_subscription_required
def get_patient(patient_id):
    """Busca um paciente específico com detalhes completos"""
    logger.info(f"[GET /patients/{patient_id}] Iniciando busca de paciente específico")
    try:
        current_user = get_current_user()
        logger.debug(f"[GET /patients/{patient_id}] Usuário atual: {current_user.id if current_user else 'None'}")
        
        if not current_user:
            logger.warning(f"[GET /patients/{patient_id}] Usuário não encontrado")
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 401
            
        logger.debug(f"[GET /patients/{patient_id}] Buscando paciente para user_id: {current_user.id}")
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        
        if not patient:
            logger.warning(f"[GET /patients/{patient_id}] Paciente não encontrado ou não autorizado")
            return jsonify({
                "success": False,
                "message": "Paciente não encontrado ou não autorizado"
            }), 404
        
        logger.info(f"[GET /patients/{patient_id}] Paciente encontrado: {patient.nome_completo}")
        
        # Buscar estatísticas do paciente
        logger.debug(f"[GET /patients/{patient_id}] Calculando estatísticas do paciente")
        total_appointments = Appointment.query.filter_by(patient_id=patient_id, user_id=current_user.id).count()
        total_sessions = Session.query.join(Appointment).filter(Appointment.patient_id == patient_id, Appointment.user_id == current_user.id).count()
        sessions_realizadas = Session.query.join(Appointment).filter(
            Appointment.patient_id == patient_id,
            Session.status == "realizada"
        ).count()
        sessions_pagas = Session.query.join(Appointment).filter(
            Appointment.patient_id == patient_id,
            Session.status_pagamento == "pago"
        ).count()
        
        patient_data = patient.to_dict()
        patient_data["statistics"] = {
            "total_appointments": total_appointments,
            "total_sessions": total_sessions,
            "sessions_realizadas": sessions_realizadas,
            "sessions_pagas": sessions_pagas,
            "sessions_pendentes": total_sessions - sessions_realizadas,
            "sessions_em_aberto": total_sessions - sessions_pagas
        }
        
        logger.info(f"[GET /patients/{patient_id}] Retornando dados do paciente com estatísticas")
        return jsonify({
            "success": True,
            "data": patient_data
        })
    except Exception as e:
        logger.error(f"[GET /patients/{patient_id}] Erro ao buscar paciente: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar paciente: {str(e)}"
        }), 500

# Toggle do Diário TCC (ativar/desativar)
@patients_bp.route("/patients/<int:patient_id>/toggle-cbt-diary", methods=["POST"])
@login_and_subscription_required
def toggle_cbt_diary(patient_id):
    """Ativa/Desativa o Diário de TCC para um paciente do profissional atual.
    Body: { "ativo": true|false }
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401

        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({"success": False, "message": "Paciente não encontrado ou não autorizado"}), 404

        payload = request.get_json() or {}
        novo_estado = bool(payload.get('ativo'))
        patient.diario_tcc_ativo = novo_estado
        db.session.commit()

        return jsonify({"success": True, "data": patient.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao atualizar Diário TCC: {str(e)}"}), 500

@patients_bp.route("/patients", methods=["POST"])
@login_and_subscription_required
def create_patient():
    """Cria um novo paciente e uma conta de usuário com senha padrão.
    Idempotente: múltiplas requisições iguais (ex.: duplo clique) retornam sucesso com o mesmo recurso.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 401
            
        data = request.get_json()
        
        # Validações básicas
        required_fields = ["nome_completo", "telefone", "email", "data_nascimento"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório: {field}"
                }), 400
        
        # Converter data de nascimento
        try:
            data_nascimento = datetime.strptime(data["data_nascimento"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Formato de data inválido. Use YYYY-MM-DD"
            }), 400
        
        # Se o paciente já existe para este usuário, tratar como idempotente
        existing_patient = Patient.query.filter_by(
            user_id=current_user.id,
            email=data["email"]
        ).first()
        if existing_patient:
            return jsonify({
                "success": True,
                "message": "Paciente já criado anteriormente",
                "data": {
                    "patient": existing_patient.to_dict()
                }
            }), 200
            
        # Verificar se já existe um usuário com este email (global)
        from src.models.usuario import User
        existing_user = User.query.filter_by(email=data["email"]).first()
        
        patient_user = None
        if not existing_user:
            # Criar usuário para o paciente com senha padrão
            username = data["email"].split("@")[0]  # Usar parte do email como username
            
            # Verificar se o username já existe e adicionar número se necessário
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
                
            # Criar o usuário
            patient_user = User(
                username=username,
                email=data["email"],
                telefone=data["telefone"],
                data_nascimento=data_nascimento,
                role="patient",
                first_login=True
            )
            patient_user.set_password("123456")  # Senha padrão
            
            db.session.add(patient_user)
            db.session.flush()  # Para obter o ID do usuário
        
        # Criar paciente vinculado ao usuário
        patient = Patient(
            user_id=current_user.id,  # Vinculado ao médico/psicólogo
            nome_completo=data["nome_completo"],
            telefone=data["telefone"],
            email=data["email"],
            data_nascimento=data_nascimento,
            observacoes=data.get("observacoes", ""),
            nome_contato_emergencia=data.get("nome_contato_emergencia"),
            telefone_contato_emergencia=data.get("telefone_contato_emergencia"),
            grau_parentesco_emergencia=data.get("grau_parentesco_emergencia")
        )
        
        db.session.add(patient)
        db.session.commit()

        if patient_user:
            return jsonify({
                "success": True,
                "message": "Paciente criado com sucesso e conta de acesso gerada",
                "data": {
                    "patient": patient.to_dict(),
                    "user": {
                        "username": patient_user.username,
                        "email": patient_user.email,
                        "password": "123456"
                    }
                }
            }), 201
        else:
            # Email já existe globalmente em outro usuário; cria apenas o registro de paciente para este usuário
            return jsonify({
                "success": True,
                "message": "Paciente criado com sucesso",
                "data": {
                    "patient": patient.to_dict()
                }
            }), 201

    except IntegrityError:
        # Tratar corrida de duplo clique: retornar o recurso existente
        db.session.rollback()
        try:
            from src.models.usuario import User
            existing_patient = Patient.query.filter_by(user_id=get_current_user().id, email=request.get_json().get("email")).first()
            if existing_patient:
                return jsonify({
                    "success": True,
                    "message": "Paciente já criado anteriormente",
                    "data": {"patient": existing_patient.to_dict()}
                }), 200
        except Exception:
            pass
        return jsonify({
            "success": False,
            "message": "Conflito de dados ao criar paciente. Tente novamente."
        }), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao criar paciente: {str(e)}"
        }), 500

@patients_bp.route("/patients/<int:patient_id>", methods=["PUT"])
@login_and_subscription_required
def update_patient(patient_id):
    """Atualiza um paciente existente"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 401
            
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({
                "success": False,
                "message": "Paciente não encontrado ou não autorizado"
            }), 404
            
        data = request.get_json()
        
        # Validações básicas
        required_fields = ["nome_completo", "telefone", "email", "data_nascimento"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório: {field}"
                }), 400
        
        # Converter data de nascimento
        try:
            data_nascimento = datetime.strptime(data["data_nascimento"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Formato de data inválido. Use YYYY-MM-DD"
            }), 400
        
        # Verificar se já existe outro paciente com o mesmo email para este usuário
        existing_patient = Patient.query.filter_by(
            user_id=current_user.id,
            email=data["email"]
        ).filter(Patient.id != patient_id).first()
        
        if existing_patient:
            return jsonify({
                "success": False,
                "message": "Este email já está cadastrado para outro paciente. Por favor, use um email diferente."
            }), 400
        
        # Atualizar dados
        patient.nome_completo = data["nome_completo"]
        patient.telefone = data["telefone"]
        patient.email = data["email"]
        patient.data_nascimento = data_nascimento
        patient.observacoes = data.get("observacoes", "")
        if 'ativo' in data:
            patient.ativo = bool(data.get('ativo'))
        patient.nome_contato_emergencia = data.get("nome_contato_emergencia")
        patient.telefone_contato_emergencia = data.get("telefone_contato_emergencia")
        patient.grau_parentesco_emergencia = data.get("grau_parentesco_emergencia")
        patient.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Paciente atualizado com sucesso",
            "data": patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao atualizar paciente: {str(e)}"
        }), 500

@patients_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
@login_and_subscription_required
def delete_patient(patient_id):
    """Remove um paciente (e todos os dados relacionados)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 401
            
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({
                "success": False,
                "message": "Paciente não encontrado ou não autorizado"
            }), 404
        
        # Verificar se há agendamentos
        appointments_count = Appointment.query.filter_by(patient_id=patient_id, user_id=current_user.id).count()
        if appointments_count > 0:
            return jsonify({
                "success": False,
                "message": f"Não é possível excluir paciente com {appointments_count} agendamento(s). Exclua os agendamentos primeiro."
            }), 400
        
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Paciente excluído com sucesso"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao excluir paciente: {str(e)}"
        }), 500

@patients_bp.route("/patients/<int:patient_id>/status", methods=["PATCH"])
@login_and_subscription_required
def toggle_patient_status(patient_id):
    """Ativa ou desativa um paciente"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401

        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({"success": False, "message": "Paciente não encontrado ou não autorizado"}), 404

        data = request.get_json() or {}
        if 'ativo' not in data:
            return jsonify({"success": False, "message": "Campo 'ativo' é obrigatório"}), 400

        patient.ativo = bool(data.get('ativo'))
        patient.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"success": True, "message": "Status atualizado com sucesso", "data": patient.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao atualizar status: {str(e)}"}), 500

@patients_bp.route("/patients/<int:patient_id>/appointments", methods=["GET"])
@login_and_subscription_required
def get_patient_appointments(patient_id):
    """Lista todos os agendamentos de um paciente específico"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 401
        
        # Verificar se o usuário é um paciente ou um profissional
        if current_user.role == 'patient':
            # Se for paciente, verificar se está tentando acessar seus próprios agendamentos
            patient = Patient.query.filter_by(id=patient_id).first()
            if not patient or patient.email != current_user.email:
                return jsonify({
                    "success": False,
                    "message": "Acesso não autorizado"
                }), 403
            
            # Para paciente, não filtrar por user_id (pois os agendamentos estão vinculados ao profissional)
            appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.data_primeira_sessao.desc()).all()
        else:
            # Se for profissional, verificar se o paciente pertence a ele
            patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
            if not patient:
                return jsonify({
                    "success": False,
                    "message": "Paciente não encontrado ou não autorizado"
                }), 404
            
            appointments = Appointment.query.filter_by(patient_id=patient_id, user_id=current_user.id).order_by(Appointment.data_primeira_sessao.desc()).all()
        
        return jsonify({
            "success": True,
            "data": [appointment.to_dict() for appointment in appointments]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar agendamentos: {str(e)}"
        }), 500

@patients_bp.route("/patients/<int:patient_id>/payments", methods=["GET"])
@login_and_subscription_required
def get_patient_payments(patient_id):
    """Lista todos os pagamentos de um paciente"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 401
            
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({
                "success": False,
                "message": "Paciente não encontrado ou não autorizado"
            }), 404
            
        payments = Payment.query.filter_by(patient_id=patient_id, user_id=current_user.id).order_by(Payment.data_pagamento.desc()).all()
        
        return jsonify({
            "success": True,
            "data": [payment.to_dict() for payment in payments]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao buscar pagamentos: {str(e)}"
        }), 500



@patients_bp.route("/patients/me", methods=["GET"])
@login_required
def get_my_patient_profile():
    """Retorna o perfil do paciente autenticado.
    Suporta modo paciente por sessão usando owner_id quando necessário.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401
        owner_id = request.args.get('owner_id', type=int)
        patient, owners = _resolve_patient_context_for_user(current_user, owner_id)
        if not patient:
            if owners:
                return jsonify({
                    "success": False,
                    "message": "Contexto de paciente necessário",
                    "code": "patient_context_required",
                    "data": {"owners": owners}
                }), 400
            return jsonify({"success": False, "message": "Paciente não encontrado"}), 404

        return jsonify({"success": True, "data": patient.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar perfil do paciente: {str(e)}"}), 500

@patients_bp.route("/patients/me/appointments", methods=["GET"])
@login_required
def get_my_patient_appointments():
    """Lista todos os agendamentos do paciente autenticado (suporta owner_id)."""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401
        owner_id = request.args.get('owner_id', type=int)
        patient, owners = _resolve_patient_context_for_user(current_user, owner_id)
        if not patient:
            if owners:
                return jsonify({
                    "success": False,
                    "message": "Contexto de paciente necessário",
                    "code": "patient_context_required",
                    "data": {"owners": owners}
                }), 400
            return jsonify({"success": False, "message": "Paciente não encontrado"}), 404
        
        appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.data_primeira_sessao.desc()).all()
        return jsonify({"success": True, "data": [a.to_dict() for a in appointments]})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar agendamentos do paciente: {str(e)}"}), 500

@patients_bp.route("/patients/me/payment-notices", methods=["GET"])
@login_required
def get_my_payment_notices():
    """Avisos de cobrança para o paciente autenticado.
    Regras:
    - Avisar 2 dias antes do vencimento (usa data da sessão como vencimento)
    - Avisar diariamente após o vencimento enquanto o pagamento estiver pendente
    - Quando houver mais de uma sessão pendente, informar quantidade e listar quais são
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401
        owner_id = request.args.get('owner_id', type=int)
        patient, owners = _resolve_patient_context_for_user(current_user, owner_id)
        if not patient:
            if owners:
                return jsonify({
                    "success": False,
                    "message": "Contexto de paciente necessário",
                    "code": "patient_context_required",
                    "data": {"owners": owners}
                }), 400
            return jsonify({"success": False, "message": "Paciente não encontrado"}), 404

        # Buscar sessões do paciente com pagamento pendente.
        # Critérios:
        # - status_pagamento PENDENTE
        # - OU sessão sem associação em PaymentSession (fallback para dados legados)
        unpaid_sessions = Session.query.join(Appointment).filter(
            Appointment.patient_id == patient.id
        ).filter(
            or_(
                Session.status_pagamento == PaymentStatus.PENDENTE,
                ~Session.payment_sessions.any()
            )
        ).order_by(Session.data_sessao.asc()).all()

        today = datetime.now().date()
        notices = []

        for s in unpaid_sessions:
            due_date = s.data_sessao.date() if hasattr(s.data_sessao, 'date') else s.data_sessao
            days_until_due = (due_date - today).days if due_date else None
            days_overdue = (today - due_date).days if (due_date and today > due_date) else 0

            alert_type = None
            if due_date:
                # Até 2 dias antes do vencimento
                if 0 <= days_until_due <= 2:
                    alert_type = 'due_soon'
                # Vencidas: alertar diariamente
                elif days_until_due is not None and days_until_due < 0:
                    alert_type = 'overdue'

            if alert_type:
                notices.append({
                    'session_id': s.id,
                    'appointment_id': s.appointment_id,
                    'numero_sessao': getattr(s, 'numero_sessao', None),
                    'valor': float(s.valor) if getattr(s, 'valor', None) is not None else 0,
                    'due_date': due_date.isoformat() if hasattr(due_date, 'isoformat') else str(due_date),
                    'alert_type': alert_type,
                    'days_until_due': days_until_due,
                    'days_overdue': days_overdue,
                    'status': getattr(s, 'status', None)
                })

        result = {
            'pending_count': len(unpaid_sessions),
            'notices': notices,
            'unpaid_sessions': [
                {
                    'session_id': s.id,
                    'numero_sessao': getattr(s, 'numero_sessao', None),
                    'valor': float(s.valor) if getattr(s, 'valor', None) is not None else 0,
                    'data_sessao': s.data_sessao.isoformat() if hasattr(s.data_sessao, 'isoformat') else str(s.data_sessao),
                    'status': getattr(s, 'status', None)
                } for s in unpaid_sessions
            ]
        }

        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar avisos de cobrança: {str(e)}"}), 500

@patients_bp.route("/patients/me/payments-summary", methods=["GET"])
@login_required
def get_my_payments_summary():
    """Resumo de pagamentos para o paciente autenticado.
    Retorna listas de sessões pendentes e pagas para exibição no dashboard.
    Critérios:
    - Pendentes: status_pagamento PENDENTE OU sem associação em PaymentSession
    - Pagas: status_pagamento PAGO OU com associação em PaymentSession
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401
        owner_id = request.args.get('owner_id', type=int)
        patient, owners = _resolve_patient_context_for_user(current_user, owner_id)
        if not patient:
            if owners:
                return jsonify({
                    "success": False,
                    "message": "Contexto de paciente necessário",
                    "code": "patient_context_required",
                    "data": {"owners": owners}
                }), 400
            return jsonify({"success": False, "message": "Paciente não encontrado"}), 404

        # Pendentes
        unpaid_sessions = Session.query.join(Appointment).filter(
            Appointment.patient_id == patient.id
        ).filter(
            or_(
                Session.status_pagamento == PaymentStatus.PENDENTE,
                ~Session.payment_sessions.any()
            )
        ).order_by(Session.data_sessao.asc()).all()

        # Pagas
        paid_sessions = Session.query.join(Appointment).filter(
            Appointment.patient_id == patient.id
        ).filter(
            or_(
                Session.status_pagamento == PaymentStatus.PAGO,
                Session.payment_sessions.any()
            )
        ).order_by(Session.data_sessao.asc()).all()

        def serialize_session(s):
            return {
                'session_id': s.id,
                'appointment_id': s.appointment_id,
                'numero_sessao': getattr(s, 'numero_sessao', None),
                'valor': float(getattr(s, 'valor', 0) or 0),
                'data_sessao': s.data_sessao.isoformat() if hasattr(s.data_sessao, 'isoformat') else str(s.data_sessao),
                'status_pagamento': getattr(getattr(s, 'status_pagamento', None), 'value', s.status_pagamento),
                'has_payment': bool(s.payment_sessions)
            }

        result = {
            'pending': [serialize_session(s) for s in unpaid_sessions],
            'paid': [serialize_session(s) for s in paid_sessions],
            'counts': {
                'pending': len(unpaid_sessions),
                'paid': len(paid_sessions)
            }
        }

        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar resumo de pagamentos: {str(e)}"}), 500

@patients_bp.route("/patients/<int:patient_id>/diary-entries/period", methods=["GET"])
def get_patient_diary_entries_period(patient_id):
    """
    Busca pensamentos/diários de um paciente em um período específico entre consultas
    Parâmetros: start_date, end_date (formato: YYYY-MM-DD)
    SEGURANÇA: Apenas funcionários/admins podem acessar, com isolamento rigoroso por tenant
    """
    logger.info(f"[GET /patients/{patient_id}/diary-entries/period] Iniciando busca de pensamentos do período (sem autenticação)")
    try:
        # Verificar se o paciente existe (sem isolamento por tenant, apenas existência)
        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
            logger.warning(f"[GET /patients/{patient_id}/diary-entries/period] Paciente não encontrado")
            return jsonify({
                "success": False,
                "message": "Paciente não encontrado"
            }), 404
        
        # VALIDAÇÃO 4: Obter e validar parâmetros de data
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            logger.warning(f"[GET /patients/{patient_id}/diary-entries/period] Parâmetros de data obrigatórios não fornecidos")
            return jsonify({
                "success": False,
                "message": "Parâmetros start_date e end_date são obrigatórios (formato: YYYY-MM-DD)"
            }), 400
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"[GET /patients/{patient_id}/diary-entries/period] Formato de data inválido: {start_date_str}, {end_date_str}")
            return jsonify({
                "success": False,
                "message": "Formato de data inválido. Use YYYY-MM-DD"
            }), 400
        
        if start_date > end_date:
            logger.warning(f"[GET /patients/{patient_id}/diary-entries/period] Data inicial maior que data final")
            return jsonify({
                "success": False,
                "message": "Data inicial não pode ser maior que data final"
            }), 400
        
        logger.debug(f"[GET /patients/{patient_id}/diary-entries/period] Buscando pensamentos entre {start_date} e {end_date}")
        
        # Buscar pensamentos do paciente no período (sem isolamento por tenant para testes)
        diary_entries = DiaryEntry.query.filter(
            and_(
                DiaryEntry.patient_id == patient_id,
                func.date(DiaryEntry.data_registro) >= start_date,
                func.date(DiaryEntry.data_registro) <= end_date
            )
        ).order_by(DiaryEntry.data_registro.desc()).all()
        
        logger.info(f"[GET /patients/{patient_id}/diary-entries/period] Encontrados {len(diary_entries)} pensamentos no período")
        
        # Converter para dict com informações seguras
        entries_data = []
        for entry in diary_entries:
            entry_dict = entry.to_dict()
            # Remover informações sensíveis desnecessárias
            entry_dict.pop('user_id', None)  # Não expor user_id no frontend
            entries_data.append(entry_dict)
        
        return jsonify({
            "success": True,
            "data": entries_data,
            "period": {
                "start_date": start_date_str,
                "end_date": end_date_str,
                "patient_name": patient.nome_completo,
                "total_entries": len(entries_data)
            }
        })
        
    except Exception as e:
        logger.error(f"[GET /patients/{patient_id}/diary-entries/period] Erro ao buscar pensamentos do período: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Erro interno do servidor"
        }), 500



def _resolve_patient_context_for_user(current_user, owner_id=None):
    """Resolve o paciente do usuário atual pelo email, opcionalmente com owner_id.
    Retorna (patient, owners_info) onde owners_info é uma lista de dicts com informações do dono
    incluindo user_id, patient_id e owner_name (quando disponível).
    """
    try:
        patients = Patient.query.filter_by(email=current_user.email).all()
        if owner_id is not None:
            chosen = next((p for p in patients if p.user_id == owner_id), None)
            return chosen, [{
                "user_id": p.user_id,
                "patient_id": p.id,
                "owner_name": getattr(getattr(p, 'user', None), 'username', None),
                "owner_email": getattr(getattr(p, 'user', None), 'email', None)
            } for p in patients]
        if len(patients) == 1:
            return patients[0], []
        elif len(patients) > 1:
            return None, [{
                "user_id": p.user_id,
                "patient_id": p.id,
                "owner_name": getattr(getattr(p, 'user', None), 'username', None),
                "owner_email": getattr(getattr(p, 'user', None), 'email', None)
            } for p in patients]
        else:
            return None, []
    except Exception:
        return None, []



