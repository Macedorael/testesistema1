from flask import Blueprint, request, jsonify, session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.models.especialidade import Especialidade
from src.models.base import Base
import os

# Configuração do banco de dados
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')}"
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

especialidades_bp = Blueprint('especialidades', __name__)

@especialidades_bp.route('/especialidades', methods=['GET'])
def get_especialidades():
    """Listar todas as especialidades"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        especialidades = db_session.query(Especialidade).all()
        result = [especialidade.to_dict() for especialidade in especialidades]
        db_session.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@especialidades_bp.route('/especialidades', methods=['POST'])
def create_especialidade():
    """Criar nova especialidade"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        db_session = DBSession()
        
        # Verificar se já existe uma especialidade com esse nome
        existing = db_session.query(Especialidade).filter_by(nome=data['nome']).first()
        if existing:
            db_session.close()
            return jsonify({'error': 'Já existe uma especialidade com esse nome'}), 400
        
        especialidade = Especialidade(
            nome=data['nome'],
            descricao=data.get('descricao', '')
        )
        
        db_session.add(especialidade)
        db_session.commit()
        
        result = especialidade.to_dict()
        db_session.close()
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@especialidades_bp.route('/especialidades/<int:especialidade_id>', methods=['GET'])
def get_especialidade(especialidade_id):
    """Obter especialidade por ID"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        especialidade = db_session.query(Especialidade).filter_by(id=especialidade_id).first()
        
        if not especialidade:
            db_session.close()
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        result = especialidade.to_dict()
        db_session.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@especialidades_bp.route('/especialidades/<int:especialidade_id>', methods=['PUT'])
def update_especialidade(especialidade_id):
    """Atualizar especialidade"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        db_session = DBSession()
        especialidade = db_session.query(Especialidade).filter_by(id=especialidade_id).first()
        
        if not especialidade:
            db_session.close()
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        # Verificar se já existe outra especialidade com esse nome
        existing = db_session.query(Especialidade).filter(
            Especialidade.nome == data['nome'],
            Especialidade.id != especialidade_id
        ).first()
        if existing:
            db_session.close()
            return jsonify({'error': 'Já existe uma especialidade com esse nome'}), 400
        
        especialidade.nome = data['nome']
        especialidade.descricao = data.get('descricao', '')
        
        db_session.commit()
        
        result = especialidade.to_dict()
        db_session.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@especialidades_bp.route('/especialidades/<int:especialidade_id>', methods=['DELETE'])
def delete_especialidade(especialidade_id):
    """Deletar especialidade"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        db_session = DBSession()
        especialidade = db_session.query(Especialidade).filter_by(id=especialidade_id).first()
        
        if not especialidade:
            db_session.close()
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        # Verificar se há funcionários usando esta especialidade
        from src.models.funcionario import Funcionario
        funcionarios_count = db_session.query(Funcionario).filter_by(especialidade_id=especialidade_id).count()
        
        if funcionarios_count > 0:
            db_session.close()
            return jsonify({'error': f'Não é possível deletar. Existem {funcionarios_count} funcionário(s) usando esta especialidade'}), 400
        
        db_session.delete(especialidade)
        db_session.commit()
        db_session.close()
        
        return jsonify({'message': 'Especialidade deletada com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500