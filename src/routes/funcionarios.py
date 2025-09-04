from flask import Blueprint, request, jsonify, session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.models.funcionario import Funcionario
from src.models.base import Base
from src.models.especialidade import Especialidade
from src.models.consulta import Appointment
import os
import re

# Configuração do banco de dados
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')}"
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

funcionarios_bp = Blueprint('funcionarios', __name__)

def validate_email(email):
    """Validar formato do email"""
    if not email:
        return True  # Email é opcional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@funcionarios_bp.route('/funcionarios', methods=['GET'])
def get_funcionarios():
    """Listar todos os funcionários"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        funcionarios = db_session.query(Funcionario).all()
        result = [funcionario.to_dict() for funcionario in funcionarios]
        db_session.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/funcionarios', methods=['POST'])
def create_funcionario():
    """Criar novo funcionário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        # Validar email se fornecido
        if data.get('email') and not validate_email(data['email']):
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        db_session = DBSession()
        
        # Verificar se já existe um funcionário com esse email
        if data.get('email'):
            existing = db_session.query(Funcionario).filter_by(email=data['email']).first()
            if existing:
                db_session.close()
                return jsonify({'error': 'Já existe um funcionário com esse email'}), 400
        
        # Verificar se a especialidade existe
        if data.get('especialidade_id'):
            especialidade = db_session.query(Especialidade).filter_by(id=data['especialidade_id']).first()
            if not especialidade:
                db_session.close()
                return jsonify({'error': 'Especialidade não encontrada'}), 400
        
        funcionario = Funcionario(
            nome=data['nome'],
            telefone=data.get('telefone', ''),
            email=data.get('email', ''),
            especialidade_id=data.get('especialidade_id'),
            obs=data.get('obs', '')
        )
        
        db_session.add(funcionario)
        db_session.commit()
        
        result = funcionario.to_dict()
        db_session.close()
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/funcionarios/<int:funcionario_id>', methods=['GET'])
def get_funcionario(funcionario_id):
    """Obter funcionário por ID"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        funcionario = db_session.query(Funcionario).filter_by(id=funcionario_id).first()
        
        if not funcionario:
            db_session.close()
            return jsonify({'error': 'Funcionário não encontrado'}), 404
        
        result = funcionario.to_dict()
        db_session.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/funcionarios/<int:funcionario_id>', methods=['PUT'])
def update_funcionario(funcionario_id):
    """Atualizar funcionário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        # Validar email se fornecido
        if data.get('email') and not validate_email(data['email']):
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        db_session = DBSession()
        funcionario = db_session.query(Funcionario).filter_by(id=funcionario_id).first()
        
        if not funcionario:
            db_session.close()
            return jsonify({'error': 'Funcionário não encontrado'}), 404
        
        # Verificar se já existe outro funcionário com esse email
        if data.get('email'):
            existing = db_session.query(Funcionario).filter(
                Funcionario.email == data['email'],
                Funcionario.id != funcionario_id
            ).first()
            if existing:
                db_session.close()
                return jsonify({'error': 'Já existe um funcionário com esse email'}), 400
        
        # Verificar se a especialidade existe
        if data.get('especialidade_id'):
            especialidade = db_session.query(Especialidade).filter_by(id=data['especialidade_id']).first()
            if not especialidade:
                db_session.close()
                return jsonify({'error': 'Especialidade não encontrada'}), 400
        
        funcionario.nome = data['nome']
        funcionario.telefone = data.get('telefone', '')
        funcionario.email = data.get('email', '')
        funcionario.especialidade_id = data.get('especialidade_id')
        funcionario.obs = data.get('obs', '')
        
        db_session.commit()
        
        result = funcionario.to_dict()
        db_session.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/funcionarios/<int:funcionario_id>', methods=['DELETE'])
def delete_funcionario(funcionario_id):
    """Deletar funcionário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        funcionario = db_session.query(Funcionario).filter_by(id=funcionario_id).first()
        
        if not funcionario:
            db_session.close()
            return jsonify({'error': 'Funcionário não encontrado'}), 404
        
        # Verificar se o funcionário tem agendamentos
        agendamentos = db_session.query(Appointment).filter_by(funcionario_id=funcionario_id).all()
        
        if agendamentos:
            # Retornar informações sobre os agendamentos
            agendamentos_info = []
            for agendamento in agendamentos:
                agendamentos_info.append({
                    'id': agendamento.id,
                    'patient_id': agendamento.patient_id,
                    'data_primeira_sessao': agendamento.data_primeira_sessao.isoformat(),
                    'quantidade_sessoes': agendamento.quantidade_sessoes
                })
            
            db_session.close()
            return jsonify({
                'error': 'Funcionário possui agendamentos',
                'has_appointments': True,
                'appointments': agendamentos_info,
                'funcionario_nome': funcionario.nome
            }), 409
        
        db_session.delete(funcionario)
        db_session.commit()
        db_session.close()
        
        return jsonify({'message': 'Funcionário deletado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/funcionarios/<int:funcionario_id>/appointments', methods=['GET'])
def get_funcionario_appointments(funcionario_id):
    """Buscar agendamentos de um funcionário específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        
        # Verificar se o funcionário existe
        funcionario = db_session.query(Funcionario).filter_by(id=funcionario_id).first()
        if not funcionario:
            db_session.close()
            return jsonify({'error': 'Funcionário não encontrado'}), 404
        
        # Buscar agendamentos do funcionário
        agendamentos = db_session.query(Appointment).filter_by(funcionario_id=funcionario_id).all()
        
        result = [{
            'id': agendamento.id,
            'paciente_nome': agendamento.paciente_nome,
            'data': agendamento.data.strftime('%Y-%m-%d') if agendamento.data else None,
            'hora': agendamento.hora.strftime('%H:%M') if agendamento.hora else None,
            'status': agendamento.status
        } for agendamento in agendamentos]
        
        db_session.close()
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
        
        db_session = DBSession()
        
        # Verificar se ambos os funcionários existem
        funcionario_antigo = db_session.query(Funcionario).filter_by(id=funcionario_id).first()
        funcionario_novo = db_session.query(Funcionario).filter_by(id=novo_funcionario_id).first()
        
        if not funcionario_antigo:
            db_session.close()
            return jsonify({'error': 'Funcionário antigo não encontrado'}), 404
        
        if not funcionario_novo:
            db_session.close()
            return jsonify({'error': 'Novo funcionário não encontrado'}), 404
        
        # Transferir todos os agendamentos
        agendamentos = db_session.query(Appointment).filter_by(funcionario_id=funcionario_id).all()
        
        for agendamento in agendamentos:
            agendamento.funcionario_id = novo_funcionario_id
        
        db_session.commit()
        
        # Agora deletar o funcionário antigo
        db_session.delete(funcionario_antigo)
        db_session.commit()
        db_session.close()
        
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
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        # Buscar todos os funcionários/profissionais de saúde
        funcionarios = db_session.query(Funcionario).join(Especialidade, Funcionario.especialidade_id == Especialidade.id, isouter=True).all()
        
        # Retornar todos os funcionários como profissionais de saúde
        medicos = []
        for funcionario in funcionarios:
            medicos.append({
                'id': funcionario.id,
                'nome': funcionario.nome,
                'especialidade': funcionario.especialidade.nome if funcionario.especialidade else 'Medicina Geral'
            })
        
        db_session.close()
        return jsonify(medicos)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@funcionarios_bp.route('/psicologos', methods=['GET'])
def get_psicologos():
    """Endpoint de compatibilidade - redireciona para /medicos"""
    try:
        return get_medicos()
    except Exception as e:
        return jsonify({'error': str(e)}), 500