from flask import Blueprint, request, jsonify, session, render_template_string
from src.models.usuario import User
from src.models.assinatura import Subscription
from src.models.historico_assinatura import SubscriptionHistory
from src.models.paciente import Patient
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from src.models.password_reset import PasswordResetToken
from src.models.email_verification import EmailVerificationToken
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
                            <th>Data de Criação</th>
                            <th>Assinatura</th>
                            <th>Status</th>
                            <th>Dias Restantes</th>
                            <th>Auto-Renovação</th>
                            <th>Renovações</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody id="users-table-body">
                        <tr>
                            <td colspan="10" class="text-center">
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
                
                if (data.success && data.data) {
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
                
                if (data.success && data.data) {
                    data.data.forEach(user => {
                    const row = document.createElement('tr');
                    
                    const roleClass = user.role === 'admin' ? 'badge-admin' : 'badge-user';
                    const roleText = user.role === 'admin' ? 'Administrador' : 'Usuário';
                    
                    // Formatar data de criação
                    let createdAtText = '-';
                    let isNewUser = false;
                    if (user.created_at) {
                        const createdDate = new Date(user.created_at);
                        createdAtText = createdDate.toLocaleDateString('pt-BR');
                        
                        // Verificar se é usuário novo (menos de 24 horas)
                        const now = new Date();
                        const diffTime = Math.abs(now - createdDate);
                        const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
                        isNewUser = diffHours <= 24;
                    }
                    
                    // Traduzir tipo de plano para português
                    // Quando não há assinatura (plan_type null/undefined), mostrar "Sem assinatura"
                    let subscriptionText = 'Sem assinatura';
                    if (user.subscription && user.subscription.plan_type) {
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
                                subscriptionText = String(user.subscription.plan_type);
                        }
                    }
                    
                    // Traduzir status para português
                    // Quando status vier null/undefined, exibir "inativo"
                    let statusText = 'inativo';
                    if (user.subscription && user.subscription.status) {
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
                                statusText = String(user.subscription.status);
                        }
                    }
                    
                    const daysRemaining = (user.subscription && typeof user.subscription.days_remaining !== 'undefined')
                        ? user.subscription.days_remaining
                        : '-';
                    const autoRenew = (user.subscription && typeof user.subscription.auto_renew !== 'undefined')
                        ? (user.subscription.auto_renew ? 'Sim' : 'Não')
                        : '-';
                    const renewalsCount = user.subscription ? user.subscription.renewals_count : 0;
                    
                    // Adicionar classe para usuários novos
                    const newUserClass = isNewUser ? 'table-warning' : '';
                    const newUserBadge = isNewUser ? ' <span class="badge bg-success ms-1">NOVO</span>' : '';
                    
                    const actionsHtml = (() => {
                        const hasActive = !!user.subscription && user.subscription.status === 'active';
                        const activationBtn = `
                            <button class="btn btn-outline-success btn-sm me-1" onclick="activateSubscription(${user.id})">
                                <i class="fas fa-play me-1"></i>Liberar Acesso
                            </button>`;
                        const deactivationBtn = `
                            <button class="btn btn-outline-danger btn-sm me-1" onclick="deactivateSubscription(${user.id})">
                                <i class="fas fa-stop me-1"></i>Encerrar Acesso
                            </button>`;
                        const deleteBtn = `
                            <button class="btn btn-outline-danger btn-sm" onclick="deleteUser(${user.id}, '${user.username}')" title="Excluir usuário permanentemente">
                                <i class="fas fa-trash me-1"></i>Excluir
                            </button>`;
                        const subscriptionBtn = hasActive ? deactivationBtn : activationBtn;
                        return subscriptionBtn + deleteBtn;
                    })();

                    row.innerHTML = `
                        <td>${user.id}</td>
                        <td>${user.username}${newUserBadge}</td>
                        <td>${user.email}</td>
                        <td><span class="badge ${roleClass}">${roleText}</span></td>
                        <td>${createdAtText}</td>
                        <td>${subscriptionText}</td>
                        <td>${statusText}</td>
                        <td>${daysRemaining}</td>
                        <td>${autoRenew}</td>
                        <td>${renewalsCount}</td>
                        <td>${actionsHtml}</td>
                    `;
                    
                    // Adicionar classe de destaque para usuários novos
                    if (isNewUser) {
                        row.classList.add('table-warning');
                    }
                    
                    tbody.appendChild(row);
                });
                } else {
                    tbody.innerHTML = '<tr><td colspan="10" class="text-center text-warning">Nenhum usuário encontrado</td></tr>';
                }
            } catch (error) {
                console.error('Erro ao carregar usuários:', error);
                document.getElementById('users-table-body').innerHTML = 
                    '<tr><td colspan="10" class="text-center text-danger">Erro ao carregar dados</td></tr>';
            }
        }

        function refreshData() {
            loadStats();
            loadUsers();
        }

        async function activateSubscription(userId, planType = 'monthly') {
            try {
                const input = prompt('Defina os dias de acesso (ex: 30):', '30');
                if (input === null) return;
                const days = parseInt(input, 10);
                if (isNaN(days) || days <= 0) {
                    alert('Informe um número válido de dias.');
                    return;
                }
                const resp = await fetch(`/admin/user/${userId}/access/grant`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ days })
                });
                const data = await resp.json();
                if (resp.ok && data.success) {
                    alert('Acesso liberado com sucesso');
                    refreshData();
                } else {
                    alert(data.error || 'Falha ao liberar acesso');
                }
            } catch (err) {
                console.error('Erro ao liberar acesso:', err);
                alert('Erro ao liberar acesso');
            }
        }

        async function deactivateSubscription(userId, reason = null) {
            try {
                const confirmed = confirm('Remover (desativar) a assinatura deste usuário?');
                if (!confirmed) return;
                const resp = await fetch(`/admin/user/${userId}/subscription/deactivate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason })
                });
                const data = await resp.json();
                if (resp.ok && data.success) {
                    alert('Assinatura removida com sucesso');
                    refreshData();
                } else {
                    alert(data.error || 'Falha ao encerrar acesso');
                }
            } catch (err) {
                console.error('Erro ao encerrar acesso:', err);
                alert('Erro ao encerrar acesso');
            }
        }

        async function deleteUser(userId, username) {
            try {
                // Confirmação dupla para exclusão
                const firstConfirm = confirm(`Tem certeza que deseja EXCLUIR PERMANENTEMENTE o usuário "${username}"?\\n\\nEsta ação não pode ser desfeita e removerá todos os dados relacionados ao usuário.`);
                if (!firstConfirm) return;
                
                const secondConfirm = confirm(`ÚLTIMA CONFIRMAÇÃO:\\n\\nVocê está prestes a excluir permanentemente o usuário "${username}" (ID: ${userId}).\\n\\nTodos os dados relacionados (pacientes, agendamentos, pagamentos, etc.) serão removidos.\\n\\nDigite "CONFIRMAR" para prosseguir:`);
                if (!secondConfirm) return;
                
                // Mostrar loading
                const loadingMsg = document.createElement('div');
                loadingMsg.innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin me-2"></i>Excluindo usuário...</div>';
                document.body.appendChild(loadingMsg);
                
                const response = await fetch(`/admin/user/${userId}/delete`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                // Remover loading
                document.body.removeChild(loadingMsg);
                
                if (response.ok && data.success) {
                    alert(`Usuário excluído com sucesso!\\n\\n${data.message}\\n\\nDetalhes:\\n- Pacientes removidos: ${data.details.patients_removed}\\n- Funcionários removidos: ${data.details.funcionarios_removed}\\n- Especialidades removidas: ${data.details.especialidades_removed}\\n- Assinaturas removidas: ${data.details.subscriptions_removed}\\n- Histórico removido: ${data.details.subscription_history_removed}\\n- Tokens removidos: ${data.details.reset_tokens_removed}`);
                    refreshData();
                } else {
                    alert(`Erro ao excluir usuário: ${data.message || 'Erro desconhecido'}`);
                }
            } catch (error) {
                console.error('Erro ao excluir usuário:', error);
                alert('Erro ao excluir usuário. Verifique a conexão e tente novamente.');
            }
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
        # Total de usuários (exclui pacientes)
        total_users = User.query.filter(User.role != 'patient').count()
        
        # Assinaturas ativas
        active_subscriptions = Subscription.query.filter_by(status='active').filter(
            Subscription.end_date > datetime.utcnow()
        ).count()
        
        stats_data = {
            'total_users': total_users,
            'active_subscriptions': active_subscriptions
        }
        
        return jsonify({
            'success': True,
            'data': stats_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar estatísticas: {str(e)}'
        }), 500

@admin_bp.route('/users')
@require_admin()
def get_users():
    """Retorna lista de todos os usuários com suas assinaturas"""
    try:
        from src.models.historico_assinatura import SubscriptionHistory
        
        # Listar apenas usuários não-pacientes
        users = User.query.filter(User.role != 'patient').all()
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
            'success': True,
            'data': users_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
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
            'success': True,
            'data': user_data
        })
    except Exception as e:
        return jsonify({
            'error': f'Erro ao buscar usuário: {str(e)}'
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
            'success': True,
            'message': 'Usuário atualizado com sucesso',
            'data': user_data
        })
    except Exception as e:
        return jsonify({
            'error': f'Erro ao atualizar usuário: {str(e)}'
        }), 500

@admin_bp.route('/user/<int:user_id>/delete', methods=['DELETE'])
@require_admin()
def delete_user(user_id):
    """Deleta usuário com limpeza segura de dependências"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Verificar se o usuário atual é admin
        current_user = User.query.get(session.get('user_id'))
        if not current_user or not current_user.is_admin:
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores podem excluir usuários.'
            }), 403
        
        # Impedir que não-admins excluam administradores
        if user.is_admin and not current_user.is_admin:
            return jsonify({
                'success': False,
                'message': 'Não é possível excluir um administrador.'
            }), 403
        
        # Contar registros relacionados antes da exclusão
        patients_count = Patient.query.filter_by(user_id=user_id).count()
        funcionarios_count = Funcionario.query.filter_by(user_id=user_id).count()
        especialidades_count = Especialidade.query.filter_by(user_id=user_id).count()
        subscription_history_count = SubscriptionHistory.query.filter_by(user_id=user_id).count()
        subscriptions_count = Subscription.query.filter_by(user_id=user_id).count()
        reset_tokens_count = PasswordResetToken.query.filter_by(user_id=user_id).count()
        email_tokens_count = EmailVerificationToken.query.filter_by(user_id=user_id).count()
        
        # Limpeza ordenada de dependências
        # 1. Excluir pacientes (cascata remove agendamentos, pagamentos, diários)
        Patient.query.filter_by(user_id=user_id).delete()
        
        # 2. Excluir funcionários
        Funcionario.query.filter_by(user_id=user_id).delete()
        
        # 3. Excluir especialidades
        Especialidade.query.filter_by(user_id=user_id).delete()
        
        # 4. Excluir histórico de assinaturas
        SubscriptionHistory.query.filter_by(user_id=user_id).delete()
        
        # 5. Excluir assinaturas
        Subscription.query.filter_by(user_id=user_id).delete()
        
        # 6. Excluir tokens de reset de senha
        PasswordResetToken.query.filter_by(user_id=user_id).delete()
        
        # 6b. Excluir tokens de verificação de email (evitar violação de FK em MySQL)
        EmailVerificationToken.query.filter_by(user_id=user_id).delete()
        
        # 7. Finalmente, excluir o usuário
        db.session.delete(user)
        
        # Commit das alterações
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usuário {user.username} (ID: {user_id}) excluído com sucesso.',
            'details': {
                'patients_removed': patients_count,
                'funcionarios_removed': funcionarios_count,
                'especialidades_removed': especialidades_count,
                'subscription_history_removed': subscription_history_count,
                'subscriptions_removed': subscriptions_count,
                'reset_tokens_removed': reset_tokens_count,
                'email_verification_tokens_removed': email_tokens_count
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir usuário: {str(e)}'
        }), 500

# Endpoints para ativar/desativar assinatura pelo admin
@admin_bp.route('/user/<int:user_id>/subscription/activate', methods=['POST'])
@require_admin()
def admin_activate_subscription(user_id):
    """Cria/ativa uma assinatura para o usuário especificado"""
    try:
        user = User.query.get_or_404(user_id)

        data = request.get_json(silent=True) or {}
        plan_type = data.get('plan_type', 'monthly')
        auto_renew = data.get('auto_renew', True)

        # Validar tipo de plano
        if plan_type not in Subscription.PLAN_PRICES:
            return jsonify({'success': False, 'error': 'Tipo de plano inválido'}), 400

        # Cancelar assinaturas ativas anteriores (se houver)
        active_subs = Subscription.query.filter_by(user_id=user_id, status='active').filter(
            Subscription.end_date > datetime.utcnow()
        ).all()
        for sub in active_subs:
            sub.cancel()

        # Criar nova assinatura
        new_sub = Subscription(user_id=user_id, plan_type=plan_type, auto_renew=auto_renew)
        db.session.add(new_sub)
        db.session.flush()  # Garantir ID para histórico

        # Registrar histórico
        SubscriptionHistory.create_history_entry(
            user_id=user_id,
            action='created',
            plan_type=plan_type,
            price=new_sub.price,
            subscription_id=new_sub.id,
            start_date=new_sub.start_date,
            end_date=new_sub.end_date,
            details='Assinatura ativada pelo admin'
        )

        db.session.commit()
        return jsonify({'success': True, 'message': 'Assinatura ativada'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao ativar assinatura: {str(e)}'}), 500


@admin_bp.route('/user/<int:user_id>/subscription/deactivate', methods=['POST'])
@require_admin()
def admin_deactivate_subscription(user_id):
    """Desativa/cancela a assinatura ativa do usuário"""
    try:
        user = User.query.get_or_404(user_id)

        data = request.get_json(silent=True) or {}
        reason = data.get('reason')

        # Localizar a assinatura ativa mais recente
        active_sub = Subscription.query.filter_by(user_id=user_id, status='active').filter(
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.created_at.desc()).first()

        if not active_sub:
            return jsonify({'success': False, 'error': 'Nenhuma assinatura ativa encontrada'}), 404

        # Cancelar
        active_sub.cancel()

        # Registrar histórico
        SubscriptionHistory.create_history_entry(
            user_id=user_id,
            action='cancelled',
            plan_type=active_sub.plan_type,
            price=active_sub.price,
            subscription_id=active_sub.id,
            start_date=active_sub.start_date,
            end_date=active_sub.end_date,
            details=reason or 'Assinatura cancelada pelo admin'
        )

        db.session.commit()
        return jsonify({'success': True, 'message': 'Assinatura desativada'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao desativar assinatura: {str(e)}'}), 500

# Novo endpoint: liberar acesso por N dias
@admin_bp.route('/user/<int:user_id>/access/grant', methods=['POST'])
@require_admin()
def grant_user_access_days(user_id):
    """Libera acesso ao usuário por N dias criando uma assinatura sem cobrança."""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json(silent=True) or {}
        days = int(data.get('days', 0))
        if days <= 0:
            return jsonify({'success': False, 'error': 'Dias de acesso inválidos'}), 400

        # Cancelar assinaturas ativas anteriores
        active_subs = Subscription.query.filter_by(user_id=user_id, status='active').filter(
            Subscription.end_date > datetime.utcnow()
        ).all()
        for sub in active_subs:
            sub.cancel()

        # Criar assinatura "trial" com fim manual
        new_sub = Subscription(user_id=user_id, plan_type='trial', auto_renew=False)
        new_sub.end_date = new_sub.start_date + timedelta(days=days)
        new_sub.price = 0.0
        new_sub.status = 'active'

        db.session.add(new_sub)
        db.session.flush()

        # Histórico
        SubscriptionHistory.create_history_entry(
            user_id=user_id,
            action='created',
            plan_type='manual_days',
            price=0.0,
            subscription_id=new_sub.id,
            start_date=new_sub.start_date,
            end_date=new_sub.end_date,
            details=f'Acesso liberado pelo admin por {days} dias'
        )

        db.session.commit()
        return jsonify({'success': True, 'message': f'Acesso liberado por {days} dias'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao liberar acesso: {str(e)}'}), 500