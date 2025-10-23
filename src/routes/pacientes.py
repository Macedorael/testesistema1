from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session
from src.models.pagamento import Payment
from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from datetime import datetime
from sqlalchemy import func
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
            
        logger.debug(f"[GET /patients] Buscando pacientes para user_id: {current_user.id}")
        patients = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.nome_completo).all()
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
        
        total_pago = db.session.query(func.sum(Payment.valor_pago)).filter_by(patient_id=patient_id).scalar() or 0
        total_a_receber = db.session.query(func.sum(Session.valor)).join(Appointment).filter(
            Appointment.patient_id == patient_id,
            Session.status_pagamento == "pendente"
        ).scalar() or 0
        
        patient_data = patient.to_dict()
        patient_data["statistics"] = {
            "total_appointments": total_appointments,
            "total_sessions": total_sessions,
            "sessions_realizadas": sessions_realizadas,
            "sessions_pagas": sessions_pagas,
            "sessions_pendentes": total_sessions - sessions_realizadas,
            "sessions_em_aberto": total_sessions - sessions_pagas,
            "total_pago": float(total_pago),
            "total_a_receber": float(total_a_receber)
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

@patients_bp.route("/patients", methods=["POST"])
@login_and_subscription_required
def create_patient():
    """Cria um novo paciente e uma conta de usuário com senha padrão"""
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
        
        # Verificar se já existe um paciente com o mesmo email para este usuário
        existing_patient = Patient.query.filter_by(
            user_id=current_user.id,
            email=data["email"]
        ).first()
        
        if existing_patient:
            return jsonify({
                "success": False,
                "message": "Este email já está cadastrado para outro paciente. Por favor, use um email diferente."
            }), 400
            
        # Verificar se já existe um usuário com este email
        from src.models.usuario import User
        existing_user = User.query.filter_by(email=data["email"]).first()
        
        if existing_user:
            return jsonify({
                "success": False,
                "message": "Este email já está cadastrado no sistema. Por favor, use um email diferente."
            }), 400
            
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
        
        return jsonify({
            "success": True,
            "message": "Paciente criado com sucesso e conta de acesso gerada",
            "data": {
                "patient": patient.to_dict(),
                "user": {
                    "username": patient_user.username,
                    "email": patient_user.email,
                    "password": "123456"  # Informar a senha padrão na resposta
                }
            }
        }), 201
        
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
    """Retorna o perfil do paciente autenticado (role=patient)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401
        if current_user.role != 'patient':
            return jsonify({"success": False, "message": "Acesso não autorizado"}), 403
        
        patient = Patient.query.filter_by(email=current_user.email).first()
        if not patient:
            return jsonify({"success": False, "message": "Paciente não encontrado"}), 404
        
        return jsonify({"success": True, "data": patient.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar perfil do paciente: {str(e)}"}), 500

@patients_bp.route("/patients/me/appointments", methods=["GET"])
@login_required
def get_my_patient_appointments():
    """Lista todos os agendamentos do paciente autenticado (role=patient)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 401
        if current_user.role != 'patient':
            return jsonify({"success": False, "message": "Acesso não autorizado"}), 403
        
        patient = Patient.query.filter_by(email=current_user.email).first()
        if not patient:
            return jsonify({"success": False, "message": "Paciente não encontrado"}), 404
        
        appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.data_primeira_sessao.desc()).all()
        return jsonify({"success": True, "data": [a.to_dict() for a in appointments]})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao buscar agendamentos do paciente: {str(e)}"}), 500



