from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session, FrequencyType, SessionStatus
from datetime import datetime
from sqlalchemy import func
import logging

# Configurar logger específico para consultas
logger = logging.getLogger('consultas')
logger.setLevel(logging.DEBUG)

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/appointments', methods=['GET'])
@login_and_subscription_required
def get_appointments():
    """Lista todos os agendamentos"""
    logger.info("[GET /appointments] Iniciando busca de agendamentos")
    try:
        current_user = get_current_user()
        logger.debug(f"[GET /appointments] Usuário atual: {current_user.id if current_user else 'None'}")
        
        if not current_user:
            logger.warning("[GET /appointments] Usuário não encontrado")
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        logger.debug(f"[GET /appointments] Buscando agendamentos para user_id: {current_user.id}")
        appointments = Appointment.query.filter_by(user_id=current_user.id).join(Patient).order_by(Appointment.data_primeira_sessao.desc()).all()
        logger.info(f"[GET /appointments] Encontrados {len(appointments)} agendamentos")
        
        appointments_data = []
        for appointment in appointments:
            appointment_dict = appointment.to_dict()
            appointment_dict['patient_name'] = appointment.patient.nome_completo
            
            # Adicionar nome do funcionário se disponível
            if appointment.funcionario:
                appointment_dict['funcionario_nome'] = appointment.funcionario.nome
            
            # Calcular sessões realizadas e restantes
            sessions_realizadas = len([s for s in appointment.sessions if s.status == SessionStatus.REALIZADA])
            sessions_restantes = appointment.quantidade_sessoes - sessions_realizadas
            
            appointment_dict['sessions_realizadas'] = sessions_realizadas
            appointment_dict['sessions_restantes'] = sessions_restantes
            
            appointments_data.append(appointment_dict)
        
        logger.info(f"[GET /appointments] Retornando {len(appointments_data)} agendamentos processados")
        return jsonify({
            'success': True,
            'data': appointments_data
        })
    except Exception as e:
        logger.error(f"[GET /appointments] Erro ao buscar agendamentos: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar agendamentos: {str(e)}'
        }), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@login_and_subscription_required
def get_appointment(appointment_id):
    """Busca um agendamento específico com todas as sessões"""
    logger.info(f"[GET /appointments/{appointment_id}] Iniciando busca de agendamento específico")
    try:
        current_user = get_current_user()
        logger.debug(f"[GET /appointments/{appointment_id}] Usuário atual: {current_user.id if current_user else 'None'}")
        
        if not current_user:
            logger.warning(f"[GET /appointments/{appointment_id}] Usuário não encontrado")
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        logger.debug(f"[GET /appointments/{appointment_id}] Buscando agendamento para user_id: {current_user.id}")
        appointment = Appointment.query.filter_by(id=appointment_id, user_id=current_user.id).first()
        
        if not appointment:
            logger.warning(f"[GET /appointments/{appointment_id}] Agendamento não encontrado ou não autorizado")
            return jsonify({
                'success': False,
                'message': 'Agendamento não encontrado ou não autorizado'
            }), 404
        
        logger.info(f"[GET /appointments/{appointment_id}] Agendamento encontrado: {appointment.id}")
        
        appointment_data = appointment.to_dict()
        appointment_data['patient_name'] = appointment.patient.nome_completo
        
        # Adicionar nome do funcionário se disponível
        if appointment.funcionario:
            appointment_data['funcionario_nome'] = appointment.funcionario.nome

        appointment_data['patient'] = appointment.patient.to_dict()
        
        # Estatísticas das sessões
        total_sessions = len(appointment.sessions)
        sessions_realizadas = len([s for s in appointment.sessions if s.status == SessionStatus.REALIZADA])
        total_valor = sum([float(s.valor) for s in appointment.sessions])
        
        appointment_data['statistics'] = {
            'total_sessions': total_sessions,
            'sessions_realizadas': sessions_realizadas,
            'sessions_pendentes': total_sessions - sessions_realizadas,
        }
        
        logger.info(f"[GET /appointments/{appointment_id}] Retornando dados do agendamento processado")
        return jsonify({
            'success': True,
            'data': appointment_data
        })
    except Exception as e:
        logger.error(f"[GET /appointments/{appointment_id}] Erro ao buscar agendamento: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar agendamento: {str(e)}'
        }), 500

@appointments_bp.route('/appointments', methods=['POST'])
@login_and_subscription_required
def create_appointment():
    """Cria um novo agendamento com múltiplas sessões"""
    try:
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['patient_id', 'data_primeira_sessao', 'quantidade_sessoes', 'frequencia', 'valor_por_sessao']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo obrigatório: {field}'
                }), 400
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        # Verificar se paciente existe e pertence ao usuário
        patient = Patient.query.filter_by(id=data['patient_id'], user_id=current_user.id).first()
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Paciente não encontrado'
            }), 404
        
        # Verificar funcionário se fornecido
        funcionario_id = data.get('funcionario_id')
        if funcionario_id:
            from src.models.funcionario import Funcionario
            funcionario = Funcionario.query.filter_by(id=funcionario_id, user_id=current_user.id).first()
            if not funcionario:
                return jsonify({
                    'success': False,
                    'message': 'Médico/Funcionário não encontrado'
                }), 404
        
        # Converter data da primeira sessão
        try:
            data_primeira_sessao = datetime.strptime(data['data_primeira_sessao'], '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                data_primeira_sessao = datetime.strptime(data['data_primeira_sessao'], '%Y-%m-%d %H:%M')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de data/hora inválido. Use YYYY-MM-DDTHH:MM ou YYYY-MM-DD HH:MM'
                }), 400
        
        # Validar frequência
        try:
            frequencia = FrequencyType(data['frequencia'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Frequência inválida. Use: semanal, quinzenal ou mensal'
            }), 400
        
        # Validar quantidade de sessões
        if data['quantidade_sessoes'] < 1 or data['quantidade_sessoes'] > 100:
            return jsonify({
                'success': False,
                'message': 'Quantidade de sessões deve ser entre 1 e 100'
            }), 400
        
        # Validar valor
        if data['valor_por_sessao'] <= 0:
            return jsonify({
                'success': False,
                'message': 'Valor por sessão deve ser maior que zero'
            }), 400
        
        # Criar agendamento
        appointment = Appointment(
            user_id=current_user.id,
            patient_id=data['patient_id'],
            funcionario_id=funcionario_id,
            data_primeira_sessao=data_primeira_sessao,
            quantidade_sessoes=data['quantidade_sessoes'],
            frequencia=frequencia,
            valor_por_sessao=data['valor_por_sessao'],
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Gerar sessões automaticamente
        appointment.generate_sessions()
        db.session.commit()
        
        # Enviar e-mail de confirmação com links do Google Calendar
        email_success = False
        try:
            from src.utils.notificacoes_email import enviar_email_confirmacao_agendamento
            email_success = enviar_email_confirmacao_agendamento(appointment.id)
            
        except Exception as e:
            print(f"[ERROR] Erro ao enviar e-mail de confirmação: {e}")
        
        # Construir mensagem de resposta baseada no resultado do e-mail
        if email_success:
            message = 'Agendamento criado com sucesso! E-mail de confirmação enviado com links para adicionar ao Google Calendar.'
        else:
            message = 'Agendamento criado com sucesso! Não foi possível enviar o e-mail de confirmação.'
        
        return jsonify({
            'success': True,
            'message': message,
            'data': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar agendamento: {str(e)}'
        }), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@login_and_subscription_required
def update_appointment(appointment_id):
    """Atualiza um agendamento existente"""
    try:
        current_user = get_current_user()
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
            }), 404
        data = request.get_json()
        
        # Validações básicas
        required_fields = ['patient_id', 'data_primeira_sessao', 'quantidade_sessoes', 'frequencia', 'valor_por_sessao']
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
                'message': 'Paciente não encontrado'
            }), 404
        
        # Verificar se funcionário existe (se fornecido)
        funcionario_id = data.get('funcionario_id')
        if funcionario_id:
            from src.models.funcionario import Funcionario
            funcionario = Funcionario.query.filter_by(id=funcionario_id, user_id=current_user.id).first()
            if not funcionario:
                return jsonify({
                    'success': False,
                    'message': 'Médico/Funcionário não encontrado'
                }), 404
        
        # Converter data da primeira sessão
        try:
            data_primeira_sessao = datetime.strptime(data['data_primeira_sessao'], '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                data_primeira_sessao = datetime.strptime(data['data_primeira_sessao'], '%Y-%m-%d %H:%M')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de data/hora inválido. Use YYYY-MM-DDTHH:MM ou YYYY-MM-DD HH:MM'
                }), 400
        
        # Validar frequência
        try:
            frequencia = FrequencyType(data['frequencia'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Frequência inválida. Use: semanal, quinzenal ou mensal'
            }), 400
        
        # Atualizar dados
        appointment.patient_id = data['patient_id']
        appointment.funcionario_id = funcionario_id  # Pode ser None
        appointment.data_primeira_sessao = data_primeira_sessao
        appointment.quantidade_sessoes = data['quantidade_sessoes']
        appointment.frequencia = frequencia
        appointment.valor_por_sessao = data['valor_por_sessao']
        appointment.observacoes = data.get('observacoes', '')
        appointment.updated_at = datetime.utcnow()
        
        # Regenerar sessões se necessário
        if (data.get('regenerate_sessions', False) or 
            len(appointment.sessions) != data['quantidade_sessoes']):
            appointment.generate_sessions()
        
        db.session.commit()
        
        # Enviar e-mail de atualização
        try:
            from src.utils.notificacoes_email import enviar_email_atualizacao_agendamento
            enviar_email_atualizacao_agendamento(appointment.id)
        except Exception as e:
            print(f"[WARNING] Erro ao enviar e-mail de atualização: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Agendamento atualizado com sucesso',
            'data': appointment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar agendamento: {str(e)}'
        }), 500

@appointments_bp.route('/appointments/<int:appointment_id>/resend-email', methods=['POST'])
@login_and_subscription_required
def resend_confirmation_email(appointment_id):
    """Reenvia o e-mail de confirmação de agendamento"""
    try:
        current_user = get_current_user()
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
            }), 404
        
        # Enviar e-mail de confirmação
        email_success = False
        try:
            from src.utils.notificacoes_email import enviar_email_confirmacao_agendamento
            email_success = enviar_email_confirmacao_agendamento(appointment.id)
            
        except Exception as e:
            print(f"[ERROR] Erro ao reenviar e-mail de confirmação: {e}")
        
        if email_success:
            return jsonify({
                'success': True,
                'message': 'E-mail de confirmação reenviado com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao reenviar e-mail de confirmação. Verifique as configurações de e-mail.'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao reenviar e-mail: {str(e)}'
        }), 500

@appointments_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@login_and_subscription_required
def delete_appointment(appointment_id):
    """Remove um agendamento e todas as sessões relacionadas"""
    try:
        current_user = get_current_user()
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
            }), 404
        
        # Coletar dados para o e-mail antes da exclusão
        from src.models.paciente import Patient
        from src.models.usuario import User
        from src.models.funcionario import Funcionario
        
        paciente = Patient.query.get(appointment.patient_id)
        usuario = User.query.get(appointment.user_id)
        
        # Buscar funcionário se disponível
        funcionario = None
        if appointment.funcionario_id:
            funcionario = Funcionario.query.get(appointment.funcionario_id)
        
        if funcionario:
            doctor_name = f"Dr(a). {funcionario.nome}"
        else:
            doctor_name = "Dr(a). Responsável pelo Atendimento" if usuario else 'Médico'
        
        agendamento_data = {
            'patient_name': paciente.nome_completo if paciente else 'Paciente',
            'patient_email': paciente.email if paciente else '',
            'doctor_name': doctor_name,
            'first_session_date': appointment.data_primeira_sessao.strftime('%d/%m/%Y às %H:%M'),
            'total_sessions': appointment.quantidade_sessoes,
            'frequency': {
                'semanal': 'Semanal',
                'quinzenal': 'Quinzenal',
                'mensal': 'Mensal'
            }.get(appointment.frequencia.value, appointment.frequencia.value)
        }
        
        db.session.delete(appointment)
        db.session.commit()
        
        # Enviar e-mail de cancelamento
        try:
            from src.utils.notificacoes_email import enviar_email_cancelamento_agendamento
            enviar_email_cancelamento_agendamento(agendamento_data)
        except Exception as e:
            print(f"[WARNING] Erro ao enviar e-mail de cancelamento: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Agendamento excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir agendamento: {str(e)}'
        }), 500

@appointments_bp.route("/sessions/<int:session_id>", methods=["PUT"])
@login_and_subscription_required
def update_session(session_id):
    try:
        current_user = get_current_user()
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
            }), 404
        data = request.get_json()
        
        # Verificar se é um reagendamento
        is_reagendamento = False
        
        # Atualizar status se fornecido
        if 'status' in data:
            new_status = SessionStatus(data['status'])
            
            if new_status == SessionStatus.REAGENDADA:
                is_reagendamento = True
                # Se a sessão está sendo reagendada, armazena a data original
                # apenas se ainda não tiver sido reagendada antes (data_original é None)
                if session.data_original is None:
                    session.data_original = session.data_sessao # Guarda a data original antes de mudar
                if 'nova_data_sessao' in data:
                    try:
                        session.data_sessao = datetime.strptime(data['nova_data_sessao'], '%Y-%m-%dT%H:%M')
                        session.data_reagendamento = datetime.utcnow() # Atualiza a data de reagendamento
                    except ValueError:
                        return jsonify({
                            'success': False,
                            'message': 'Formato de nova data/hora inválido para reagendamento. Use YYYY-MM-DDTHH:MM'
                        }), 400
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Nova data da sessão é obrigatória para reagendamento.'
                    }), 400
            session.status = new_status
            if new_status == SessionStatus.REALIZADA or new_status == SessionStatus.FALTOU or new_status == SessionStatus.CANCELADA:
                # Se o status for final, limpa data_original e data_reagendamento
                session.data_original = None
                session.data_reagendamento = None
        
        # Atualizar observações se fornecido
        if 'observacoes' in data:
            session.observacoes = data['observacoes']
        
        # Atualizar data da sessão se fornecido (apenas se não for reagendamento)
        if 'data_sessao' in data and session.status != SessionStatus.REAGENDADA:
            try:
                session.data_sessao = datetime.strptime(data['data_sessao'], '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    session.data_sessao = datetime.strptime(data['data_sessao'], '%Y-%m-%d %H:%M')
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Formato de data/hora inválido. Use YYYY-MM-DDTHH:MM ou YYYY-MM-DD HH:MM'
                    }), 400
        
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Enviar e-mail de reagendamento se aplicável
        if is_reagendamento:
            try:
                from src.utils.notificacoes_email import enviar_email_reagendamento_sessao
                enviar_email_reagendamento_sessao(session.id)
            except Exception as e:
                print(f"Erro ao enviar e-mail de reagendamento: {str(e)}")
                # Não falha a operação se o e-mail não for enviado
        
        return jsonify({
            'success': True,
            'message': 'Sessão atualizada com sucesso',
            'data': session.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar sessão: {str(e)}'
        }), 500