from flask import Blueprint, request, jsonify, session, render_template_string
from src.models.usuario import User
from src.models.assinatura import Subscription
from src.models.base import db
from src.utils.auth import login_required
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def require_admin():
    """Decorator para verificar se o usuário é administrador"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Login necessário'}), 401
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_admin():
                return jsonify({'error': 'Acesso negado - privilégios de administrador necessários'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@admin_bp.route('/dashboard')
@require_admin()
def admin_dashboard():
    """Página principal do dashboard administrativo"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Administrativo - Consultório</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .admin-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
        }
        .stat-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-2px);
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        .table-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-top: 2rem;
        }
        .badge-admin {
            background-color: #dc3545;
        }
        .badge-user {
            background-color: #28a745;
        }
    </style>
</head>
<body style="background-color: #f8f9fa;">
    <div class="admin-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1><i class="fas fa-tachometer-alt me-3"></i>Dashboard Administrativo</h1>
                    <p class="mb-0">Visão geral do sistema de consultório</p>
                </div>
                <div class="col-md-4 text-end">
                    <button onclick="logout()" class="btn btn-primary">
                        <i class="fas fa-sign-out-alt me-2"></i>Sair do Sistema
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="container mt-4">
        <!-- Estatísticas Gerais -->
        <div class="row" id="stats-container">
            <div class="col-md-6">
                <div class="stat-card text-center">
                    <i class="fas fa-users fa-2x text-primary mb-3"></i>
                    <div class="stat-number" id="total-users">-</div>
                    <div class="text-muted">Total de Usuários</div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="stat-card text-center">
                    <i class="fas fa-crown fa-2x text-warning mb-3"></i>
                    <div class="stat-number" id="active-subscriptions">-</div>
                    <div class="text-muted">Assinaturas Ativas</div>
                </div>
            </div>
        </div>

        <!-- Tabela de Usuários -->
        <div class="table-container">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h3><i class="fas fa-users me-2"></i>Usuários do Sistema</h3>
                <button class="btn btn-primary" onclick="refreshData()">
                    <i class="fas fa-sync-alt me-2"></i>Atualizar
                </button>
            </div>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Nome de Usuário</th>
                            <th>E-mail</th>
                            <th>Tipo</th>
                            <th>Assinatura</th>
                            <th>Status</th>
                            <th>Dias Restantes</th>
                            <th>Auto-Renovação</th>
                            <th>Renovações</th>
                        </tr>
                    </thead>
                    <tbody id="users-table-body">
                        <tr>
                            <td colspan="9" class="text-center">
                                <i class="fas fa-spinner fa-spin me-2"></i>Carregando dados...
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        async function loadStats() {
            try {
                const response = await fetch('/admin/stats');
                const data = await response.json();
                
                if (data.sucesso && data.data) {
                    document.getElementById('total-users').textContent = data.data.total_users;
                    document.getElementById('active-subscriptions').textContent = data.data.active_subscriptions;
                } else {
                    document.getElementById('total-users').textContent = '0';
                    document.getElementById('active-subscriptions').textContent = '0';
                }
            } catch (error) {
                console.error('Erro ao carregar estatísticas:', error);
                document.getElementById('total-users').textContent = 'Erro';
                document.getElementById('active-subscriptions').textContent = 'Erro';
            }
        }

        async function loadUsers() {
            try {
                const response = await fetch('/admin/users');
                const data = await response.json();
                
                const tbody = document.getElementById('users-table-body');
                tbody.innerHTML = '';
                
                if (data.sucesso && data.data) {
                    data.data.forEach(user => {
                    const row = document.createElement('tr');
                    
                    const roleClass = user.role === 'admin' ? 'badge-admin' : 'badge-user';
                    const roleText = user.role === 'admin' ? 'Administrador' : 'Usuário';
                    
                    // Traduzir tipo de plano para português
                    let subscriptionText = 'Nenhuma';
                    if (user.subscription) {
                        switch(user.subscription.plan_type) {
                            case 'annual':
                                subscriptionText = 'Anual';
                                break;
                            case 'monthly':
                                subscriptionText = 'Mensal';
                                break;
                            case 'quarterly':
                                subscriptionText = 'Trimestral';
                                break;
                            case 'biannual':
                                subscriptionText = 'Semestral';
                                break;
                            default:
                                subscriptionText = user.subscription.plan_type;
                        }
                    }
                    
                    // Traduzir status para português
                    let statusText = 'Sem assinatura';
                    if (user.subscription) {
                        switch(user.subscription.status) {
                            case 'active':
                                statusText = 'ativo';
                                break;
                            case 'inactive':
                                statusText = 'inativo';
                                break;
                            case 'expired':
                                statusText = 'expirado';
                                break;
                            case 'cancelled':
                                statusText = 'cancelado';
                                break;
                            default:
                                statusText = user.subscription.status;
                        }
                    }
                    
                    const daysRemaining = user.subscription ? user.subscription.days_remaining : '-';
                    const autoRenew = user.subscription ? (user.subscription.auto_renew ? 'Sim' : 'Não') : '-';
                    const renewalsCount = user.subscription ? user.subscription.renewals_count : 0;
                    
                    row.innerHTML = `
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${user.email}</td>
                        <td><span class="badge ${roleClass}">${roleText}</span></td>
                        <td>${subscriptionText}</td>
                        <td>${statusText}</td>
                        <td>${daysRemaining}</td>
                        <td>${autoRenew}</td>
                        <td>${renewalsCount}</td>
                    `;
                    
                    tbody.appendChild(row);
                });
                } else {
                    tbody.innerHTML = '<tr><td colspan="9" class="text-center text-warning">Nenhum usuário encontrado</td></tr>';
                }
            } catch (error) {
                console.error('Erro ao carregar usuários:', error);
                document.getElementById('users-table-body').innerHTML = 
                    '<tr><td colspan="9" class="text-center text-danger">Erro ao carregar dados</td></tr>';
            }
        }

        function refreshData() {
            loadStats();
            loadUsers();
        }

        // Carregar dados ao inicializar a página
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
        });

        // Função de logout
        function logout() {
            if (confirm('Tem certeza que deseja sair do sistema?')) {
                fetch('/api/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }).then(response => {
                    // Limpar dados de sessão locais
                    localStorage.clear();
                    sessionStorage.clear();
                    
                    // Redirecionar para a tela inicial (landing page)
                    window.location.href = '/';
                }).catch(error => {
                    console.error('Erro no logout:', error);
                    // Mesmo se der erro, limpar dados locais e redirecionar
                    localStorage.clear();
                    sessionStorage.clear();
                    window.location.href = '/';
                });
            }
        }
    </script>
</body>
</html>
    ''')

@admin_bp.route('/stats')
@require_admin()
def get_stats():
    """Retorna estatísticas gerais do sistema"""
    try:
        # Total de usuários
        total_users = User.query.count()
        
        # Assinaturas ativas
        active_subscriptions = Subscription.query.filter_by(status='active').filter(
            Subscription.end_date > datetime.utcnow()
        ).count()
        
        stats_data = {
            'total_users': total_users,
            'active_subscriptions': active_subscriptions
        }
        
        return jsonify({
            'sucesso': True,
            'data': stats_data
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'message': f'Erro ao buscar estatísticas: {str(e)}'
        }), 500

@admin_bp.route('/users')
@require_admin()
def get_users():
    """Retorna lista de todos os usuários com suas assinaturas"""
    try:
        from src.models.historico_assinatura import SubscriptionHistory
        
        users = User.query.all()
        users_data = []
        
        for user in users:
            user_dict = user.to_dict()
            
            # Buscar assinatura ativa
            active_subscription = Subscription.query.filter_by(
                user_id=user.id,
                status='active'
            ).filter(
                Subscription.end_date > datetime.utcnow()
            ).order_by(Subscription.created_at.desc()).first()
            
            # Contar renovações do usuário
            renewals_count = SubscriptionHistory.query.filter_by(
                user_id=user.id,
                action='renewed'
            ).count()
            
            if active_subscription:
                user_dict['subscription'] = {
                    'plan_type': active_subscription.plan_type,
                    'status': active_subscription.status,
                    'days_remaining': active_subscription.days_remaining(),
                    'end_date': active_subscription.end_date.strftime('%d/%m/%Y'),
                    'auto_renew': active_subscription.auto_renew,
                    'renewals_count': renewals_count
                }
            else:
                user_dict['subscription'] = {
                    'plan_type': None,
                    'status': None,
                    'days_remaining': 0,
                    'end_date': None,
                    'auto_renew': False,
                    'renewals_count': renewals_count
                }
            
            users_data.append(user_dict)
        
        return jsonify({
            'sucesso': True,
            'data': users_data
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'message': f'Erro ao buscar usuários: {str(e)}'
        }), 500

@admin_bp.route('/user/<int:user_id>')
@require_admin()
def get_user_details(user_id):
    """Retorna detalhes específicos de um usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Buscar todas as assinaturas do usuário
        subscriptions = Subscription.query.filter_by(user_id=user_id).order_by(
            Subscription.created_at.desc()
        ).all()
        
        user_data = user.to_dict()
        user_data['subscriptions_history'] = [sub.to_dict() for sub in subscriptions]
        
        return jsonify({
            'sucesso': True,
            'data': user_data
        })
    except Exception as e:
        return jsonify({
            'erro': f'Erro ao buscar usuário: {str(e)}'
        }), 500

@admin_bp.route('/user/<int:user_id>/update')
@require_admin()
def update_user(user_id):
    """Atualiza detalhes específicos de um usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Buscar todas as assinaturas do usuário
        subscriptions = Subscription.query.filter_by(user_id=user_id).order_by(
            Subscription.created_at.desc()
        ).all()
        
        user_data = user.to_dict()
        user_data['subscriptions_history'] = [sub.to_dict() for sub in subscriptions]
        
        return jsonify({
            'sucesso': True,
            'message': 'Usuário atualizado com sucesso',
            'data': user_data
        })
    except Exception as e:
        return jsonify({
            'erro': f'Erro ao atualizar usuário: {str(e)}'
        }), 500

@admin_bp.route('/user/<int:user_id>/delete')
@require_admin()
def delete_user(user_id):
    """Deleta usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Buscar todas as assinaturas do usuário
        subscriptions = Subscription.query.filter_by(user_id=user_id).order_by(
            Subscription.created_at.desc()
        ).all()
        
        user_data = user.to_dict()
        user_data['subscriptions_history'] = [sub.to_dict() for sub in subscriptions]
        
        return jsonify({
            'sucesso': True,
            'message': 'Usuário deletado com sucesso'
        })
    except Exception as e:
        return jsonify({
            'erro': f'Erro ao deletar usuário: {str(e)}'
        }), 500