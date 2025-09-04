from flask import Blueprint, request, jsonify, session
from src.models.especialidade import Especialidade
from src.models.base import db

especialidades_bp = Blueprint('especialidades', __name__)

@especialidades_bp.route('/especialidades', methods=['GET'])
def get_especialidades():
    """Listar todas as especialidades"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        especialidades = Especialidade.query.all()
        result = [especialidade.to_dict() for especialidade in especialidades]
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
        
        # Verificar se já existe uma especialidade com esse nome
        existing = Especialidade.query.filter_by(nome=data['nome']).first()
        if existing:
            return jsonify({'error': 'Já existe uma especialidade com esse nome'}), 400
        
        especialidade = Especialidade(
            nome=data['nome'],
            descricao=data.get('descricao', '')
        )
        
        db.session.add(especialidade)
        db.session.commit()
        
        result = especialidade.to_dict()
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@especialidades_bp.route('/especialidades/<int:especialidade_id>', methods=['GET'])
def get_especialidade(especialidade_id):
    """Obter especialidade por ID"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        especialidade = Especialidade.query.filter_by(id=especialidade_id).first()
        
        if not especialidade:
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        result = especialidade.to_dict()
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
        
        especialidade = Especialidade.query.filter_by(id=especialidade_id).first()
        
        if not especialidade:
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        # Verificar se já existe outra especialidade com esse nome
        existing = Especialidade.query.filter(
            Especialidade.nome == data['nome'],
            Especialidade.id != especialidade_id
        ).first()
        if existing:
            return jsonify({'error': 'Já existe uma especialidade com esse nome'}), 400
        
        especialidade.nome = data['nome']
        especialidade.descricao = data.get('descricao', '')
        
        db.session.commit()
        
        result = especialidade.to_dict()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@especialidades_bp.route('/especialidades/<int:especialidade_id>', methods=['DELETE'])
def delete_especialidade(especialidade_id):
    """Deletar especialidade"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        especialidade = Especialidade.query.filter_by(id=especialidade_id).first()
        
        if not especialidade:
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        # Verificar se há funcionários usando esta especialidade
        from src.models.funcionario import Funcionario
        funcionarios_count = Funcionario.query.filter_by(especialidade_id=especialidade_id).count()
        
        if funcionarios_count > 0:
            return jsonify({'error': f'Não é possível deletar. Existem {funcionarios_count} funcionário(s) usando esta especialidade'}), 400
        
        db.session.delete(especialidade)
        db.session.commit()
        
        return jsonify({'message': 'Especialidade deletada com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500