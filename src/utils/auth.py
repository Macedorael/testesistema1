from functools import wraps
from flask import session, jsonify
from src.models.usuario import User

def login_required(f):
    """Decorador que exige que o usuário esteja logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    """Decorador que exige que o usuário tenha uma assinatura ativa"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if not user.has_active_subscription():
            return jsonify({
                'error': 'Assinatura ativa necessária para acessar este recurso',
                'subscription_required': True
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def login_and_subscription_required(f):
    """Decorador que exige login e assinatura ativa"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primeiro verifica login
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        
        # Depois verifica assinatura
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if not user.has_active_subscription():
            return jsonify({
                'error': 'Assinatura ativa necessária para acessar este recurso',
                'subscription_required': True
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retorna o usuário atual da sessão"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

