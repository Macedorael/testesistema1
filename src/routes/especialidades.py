from flask import Blueprint, request, jsonify, session
from src.models.especialidade import Especialidade
from src.models.funcionario import Funcionario
from src.models.base import db
from src.utils.auth import login_required, get_current_user

especialidades_bp = Blueprint('especialidades', __name__)

@especialidades_bp.route('/especialidades', methods=['GET'])
@login_required
def get_especialidades():
    """Retorna lista de especialidades do usuário logado"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        especialidades = Especialidade.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'especialidades': [especialidade.to_dict() for especialidade in especialidades]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar especialidades: {str(e)}'
        }), 500

@especialidades_bp.route('/especialidades', methods=['POST'])
@login_required
def create_especialidade():
    """Cria uma nova especialidade para o usuário logado"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 401
            
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('nome'):
            return jsonify({
                'success': False,
                'message': 'Nome é obrigatório'
            }), 400
        
        # Verificar se já existe especialidade com esse nome para este usuário
        existing = Especialidade.query.filter_by(
            nome=data['nome'],
            user_id=current_user.id
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Já existe uma especialidade com esse nome'
            }), 400
        
        # Criar especialidade
        especialidade = Especialidade(
            user_id=current_user.id,
            nome=data['nome'],
            descricao=data.get('descricao')
        )
        
        db.session.add(especialidade)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Especialidade criada com sucesso',
            'especialidade': especialidade.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar especialidade: {str(e)}'
        }), 500

@especialidades_bp.route('/especialidades/<int:especialidade_id>', methods=['GET'])
@login_required
def get_especialidade(especialidade_id):
    """Obter especialidade por ID"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        especialidade = Especialidade.query.filter_by(id=especialidade_id, user_id=current_user.id).first()
        
        if not especialidade:
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        result = especialidade.to_dict()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@especialidades_bp.route('/especialidades/<int:especialidade_id>', methods=['PUT'])
@login_required
def update_especialidade(especialidade_id):
    """Atualizar especialidade"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        especialidade = Especialidade.query.filter_by(id=especialidade_id, user_id=current_user.id).first()
        
        if not especialidade:
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        # Verificar se já existe outra especialidade com esse nome para este usuário
        existing = Especialidade.query.filter(
            Especialidade.nome == data['nome'],
            Especialidade.id != especialidade_id,
            Especialidade.user_id == current_user.id
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
@login_required
def delete_especialidade(especialidade_id):
    """Deletar especialidade"""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        especialidade = Especialidade.query.filter_by(id=especialidade_id, user_id=current_user.id).first()
        
        if not especialidade:
            return jsonify({'error': 'Especialidade não encontrada'}), 404
        
        # Verificar se há funcionários associados a esta especialidade do mesmo usuário
        from src.models.funcionario import Funcionario
        funcionarios_count = Funcionario.query.filter_by(
            especialidade_id=especialidade_id,
            user_id=current_user.id
        ).count()
        
        if funcionarios_count > 0:
            return jsonify({'error': f'Não é possível deletar. Existem {funcionarios_count} funcionário(s) usando esta especialidade'}), 400
        
        db.session.delete(especialidade)
        db.session.commit()
        
        return jsonify({'message': 'Especialidade deletada com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500