from flask import Blueprint, request, jsonify, session
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from src.models.consulta import Appointment
from src.models.usuario import db
from src.utils.auth import login_required, get_current_user
from src.utils.validation import validate_required, error_response_missing
import re

funcionarios_bp = Blueprint('funcionarios', __name__)

def validate_email(email):
    """Validar formato do email"""
    if not email:
        return True  # Email é opcional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@funcionarios_bp.route('/funcionarios', methods=['GET'])
@login_required
def get_funcionarios():
    """Retorna lista de funcionários do usuário logado"""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("[FUNCIONARIOS] Iniciando busca de funcionários")
        
        current_user = get_current_user()
        logger.info(f"[FUNCIONARIOS] Current user obtido: {current_user.id if current_user else 'None'}")
        
        if not current_user:
            logger.error("[FUNCIONARIOS] Usuário não encontrado")
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
        
        logger.info(f"[FUNCIONARIOS] Buscando funcionários para user_id: {current_user.id}")
        funcionarios = Funcionario.query.filter_by(user_id=current_user.id).all()
        logger.info(f"[FUNCIONARIOS] Encontrados {len(funcionarios)} funcionários")
        
        funcionarios_dict = []
        for i, funcionario in enumerate(funcionarios):
            try:
                logger.info(f"[FUNCIONARIOS] Convertendo funcionário {i+1}: ID={funcionario.id}, Nome={funcionario.nome}")
                func_dict = funcionario.to_dict()
                funcionarios_dict.append(func_dict)
                logger.info(f"[FUNCIONARIOS] Funcionário {i+1} convertido com sucesso")
            except Exception as conv_error:
                logger.error(f"[FUNCIONARIOS] Erro ao converter funcionário {i+1}: {str(conv_error)}")
                raise conv_error
        
        logger.info(f"[FUNCIONARIOS] Retornando {len(funcionarios_dict)} funcionários")
        return jsonify({
            'success': True,
            'funcionarios': funcionarios_dict
        })
    except Exception as e:
        logger.error(f"[FUNCIONARIOS] Erro geral: {str(e)}")
        logger.error(f"[FUNCIONARIOS] Tipo do erro: {type(e).__name__}")
        import traceback
        logger.error(f"[FUNCIONARIOS] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar funcionários: {str(e)}'
        }), 500

@funcionarios_bp.route('/funcionarios', methods=['POST'])
@login_required
def create_funcionario():
    """Cria um novo funcionário para o usuário logado"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        data = request.get_json()
        
        # Validar dados obrigatórios (mensagens específicas)
        missing = validate_required(data, {
            'nome': 'Nome',
            'especialidade_id': 'Especialidade'
        })
        if missing:
            return error_response_missing(missing)
        
        # Validar email se fornecido
        if data.get('email') and not validate_email(data['email']):
            return jsonify({
                'success': False,
                'message': 'Formato de email inválido'
            }), 400
        
        # Verificar se já existe um funcionário com esse email para este usuário
        if data.get('email'):
            existing = Funcionario.query.filter_by(
                email=data['email'], 
                user_id=current_user.id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': 'Já existe um funcionário com esse email'
                }), 400
        
        # Verificar se especialidade existe e pertence ao usuário
        especialidade = Especialidade.query.filter_by(
            id=data['especialidade_id'], 
            user_id=current_user.id
        ).first()
        if not especialidade:
            return jsonify({
                'success': False,
                'message': 'Especialidade não encontrada ou não autorizada'
            }), 404
        
        # Criar funcionário
        funcionario = Funcionario(
            user_id=current_user.id,
            nome=data['nome'],
            especialidade_id=data['especialidade_id'],
            telefone=data.get('telefone', ''),
            email=data.get('email', ''),
            obs=data.get('obs', '')
        )
        
        db.session.add(funcionario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Funcionário criado com sucesso',
            'funcionario': funcionario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar funcionário: {str(e)}'
        }), 500

@funcionarios_bp.route('/funcionarios/<int:funcionario_id>', methods=['GET'])
def get_funcionario(funcionario_id):
    """Obter funcionário por ID"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        funcionario = Funcionario.query.filter_by(id=funcionario_id).first()
        
        if not funcionario:
            return jsonify({'error': 'Funcionário não encontrado'}), 404
        
        result = funcionario.to_dict()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/<int:funcionario_id>', methods=['PUT'])
@login_required
def update_funcionario(funcionario_id):
    """Atualiza um funcionário do usuário logado"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        funcionario = Funcionario.query.filter_by(
            id=funcionario_id, 
            user_id=current_user.id
        ).first()
        if not funcionario:
            return jsonify({
                'success': False,
                'message': 'Funcionário não encontrado ou não autorizado'
            }), 404
            
        data = request.get_json()
        
        # Validar dados obrigatórios quando fornecidos
        fields_to_check = {}
        if 'nome' in data:
            fields_to_check['nome'] = 'Nome'
        if 'especialidade_id' in data:
            fields_to_check['especialidade_id'] = 'Especialidade'
        missing = validate_required(data, fields_to_check) if fields_to_check else None
        if missing:
            return error_response_missing(missing)
        
        # Validar email se fornecido
        if data.get('email') and not validate_email(data['email']):
            return jsonify({
                'success': False,
                'message': 'Formato de email inválido'
            }), 400
        
        # Verificar se já existe outro funcionário com esse email para este usuário
        if data.get('email'):
            existing = Funcionario.query.filter(
                Funcionario.email == data['email'],
                Funcionario.id != funcionario_id,
                Funcionario.user_id == current_user.id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': 'Já existe um funcionário com esse email'
                }), 400
        
        if 'especialidade_id' in data:
            especialidade = Especialidade.query.filter_by(
                id=data['especialidade_id'],
                user_id=current_user.id
            ).first()
            if not especialidade:
                return jsonify({
                    'success': False,
                    'message': 'Especialidade não encontrada ou não autorizada'
                }), 404
        
        # Atualizar campos
        if 'nome' in data:
            funcionario.nome = data['nome']
        if 'especialidade_id' in data:
            funcionario.especialidade_id = data['especialidade_id']
        if 'telefone' in data:
            funcionario.telefone = data['telefone']
        if 'email' in data:
            funcionario.email = data['email']
        if 'obs' in data:
            funcionario.obs = data['obs']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Funcionário atualizado com sucesso',
            'funcionario': funcionario.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar funcionário: {str(e)}'
        }), 500

@funcionarios_bp.route('/<int:funcionario_id>', methods=['DELETE'])
@login_required
def delete_funcionario(funcionario_id):
    """Deleta um funcionário do usuário logado"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        funcionario = Funcionario.query.filter_by(
            id=funcionario_id, 
            user_id=current_user.id
        ).first()
        if not funcionario:
            return jsonify({
                'success': False,
                'message': 'Funcionário não encontrado ou não autorizado'
            }), 404
        
        # Verificar se há appointments associados do mesmo usuário
        appointments = Appointment.query.filter_by(
            funcionario_id=funcionario_id,
            user_id=current_user.id
        ).first()
        if appointments:
            return jsonify({
                'success': False,
                'message': 'Não é possível excluir funcionário com agendamentos associados'
            }), 400
        
        db.session.delete(funcionario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Funcionário excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir funcionário: {str(e)}'
        }), 500

@funcionarios_bp.route('/funcionarios/<int:funcionario_id>/appointments', methods=['GET'])
def get_funcionario_appointments(funcionario_id):
    """Buscar agendamentos de um funcionário específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o funcionário existe
        funcionario = Funcionario.query.filter_by(id=funcionario_id).first()
        if not funcionario:
            return jsonify({'error': 'Funcionário não encontrado'}), 404
        
        # Buscar agendamentos do funcionário
        agendamentos = Appointment.query.filter_by(funcionario_id=funcionario_id).all()
        
        result = [{
            'id': agendamento.id,
            'paciente_nome': agendamento.paciente_nome,
            'data': agendamento.data.strftime('%Y-%m-%d') if agendamento.data else None,
            'hora': agendamento.hora.strftime('%H:%M') if agendamento.hora else None,
            'status': agendamento.status
        } for agendamento in agendamentos]
        
        return jsonify({
            'funcionario': funcionario.nome,
            'agendamentos': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/funcionarios/<int:funcionario_id>/transfer-appointments', methods=['POST'])
def transfer_appointments(funcionario_id):
    """Transferir agendamentos de um funcionário para outro"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        novo_funcionario_id = data.get('novo_funcionario_id')
        
        if not novo_funcionario_id:
            return jsonify({'error': 'ID do novo funcionário é obrigatório'}), 400
        
        # Verificar se ambos os funcionários existem
        funcionario_antigo = Funcionario.query.filter_by(id=funcionario_id).first()
        funcionario_novo = Funcionario.query.filter_by(id=novo_funcionario_id).first()
        
        if not funcionario_antigo:
            return jsonify({'error': 'Funcionário antigo não encontrado'}), 404
        
        if not funcionario_novo:
            return jsonify({'error': 'Novo funcionário não encontrado'}), 404
        
        # Transferir todos os agendamentos
        agendamentos = Appointment.query.filter_by(funcionario_id=funcionario_id).all()
        
        for agendamento in agendamentos:
            agendamento.funcionario_id = novo_funcionario_id
        
        db.session.commit()
        
        # Agora deletar o funcionário antigo
        db.session.delete(funcionario_antigo)
        db.session.commit()
        
        return jsonify({
            'message': f'Agendamentos transferidos para {funcionario_novo.nome} e funcionário {funcionario_antigo.nome} deletado com sucesso',
            'transferred_appointments': len(agendamentos)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/medicos', methods=['GET'])
def get_medicos():
    """Listar todos os médicos/profissionais de saúde"""
    if 'user_id' not in session:
        print("[ERROR] /medicos - Usuário não autenticado")
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        user_id = session.get('user_id')
        print(f"[DEBUG] /medicos - Iniciando busca de funcionários para user_id: {user_id}")
        
        # CORREÇÃO: Buscar APENAS os funcionários do usuário atual (isolamento de dados)
        funcionarios = Funcionario.query.filter_by(user_id=user_id).join(Especialidade, Funcionario.especialidade_id == Especialidade.id, isouter=True).all()
        
        print(f"[DEBUG] /medicos - Encontrados {len(funcionarios)} funcionários para user_id: {user_id}")
        
        # Retornar apenas os funcionários do usuário atual
        medicos = []
        for funcionario in funcionarios:
            especialidade_nome = funcionario.especialidade.nome if funcionario.especialidade else 'Especialidade não informada'
            medico_data = {
                'id': funcionario.id,
                'nome': funcionario.nome,
                'especialidade': especialidade_nome
            }
            medicos.append(medico_data)
            print(f"[DEBUG] /medicos - Funcionário: ID={funcionario.id}, Nome='{funcionario.nome}', Especialidade='{especialidade_nome}', User_ID={funcionario.user_id}")
        
        print(f"[DEBUG] /medicos - Retornando {len(medicos)} médicos para user_id: {user_id}")
        return jsonify(medicos)
    
    except Exception as e:
        print(f"[ERROR] /medicos - Erro ao buscar médicos: {str(e)}")
        import traceback
        print(f"[ERROR] /medicos - Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/psicologos', methods=['GET'])
def get_psicologos():
    """Endpoint de compatibilidade - redireciona para /medicos"""
    try:
        return get_medicos()
    except Exception as e:
        return jsonify({'error': str(e)}), 500