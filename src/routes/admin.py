from flask import Blueprint, request, jsonify, session, render_template_string
from src.models.usuario import User
from src.models.assinatura import Subscription
from src.models.historico_assinatura import SubscriptionHistory
from src.models.paciente import Patient
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from src.models.password_reset import PasswordResetToken
from src.models.email_verification import EmailVerificationToken
from src.models.consulta import Appointment, Session
from src.models.pagamento import Payment, PaymentSession
from src.models.diario import DiaryEntry
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
        /* Botões do header com cor do app e espaçamento */
        .header-actions { display: flex; align-items: center; gap: 0.5rem; }
        .btn-app { background-color: #667eea; color: #fff; border: none; }
        .btn-app:hover { background-color: #5a54d1; color: #fff; }
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
                    <div class="header-actions">
                        <a href="/admin/payments" class="btn btn-app">
                            <i class="fas fa-credit-card me-2"></i>Pagamentos de Usuário
                        </a>
                        <button onclick="logout()" class="btn btn-app">
                            <i class="fas fa-sign-out-alt me-2"></i>Sair do Sistema
                        </button>
                    </div>
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
                            <th>Status</th>
                            <th>Dias Restantes</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody id="users-table-body">
                        <tr>
                            <td colspan="8" class="text-center">
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
                    // Removido: coluna de renovações
                    
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
                        <td>${statusText}</td>
                        <td>${daysRemaining}</td>
                        <td>${actionsHtml}</td>
                    `;
                    
                    // Adicionar classe de destaque para usuários novos
                    if (isNewUser) {
                        row.classList.add('table-warning');
                    }
                    
                    tbody.appendChild(row);
                });
                } else {
                    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-warning">Nenhum usuário encontrado</td></tr>';
                }
            } catch (error) {
                console.error('Erro ao carregar usuários:', error);
                document.getElementById('users-table-body').innerHTML = 
                    '<tr><td colspan="8" class="text-center text-danger">Erro ao carregar dados</td></tr>';
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

        async function activatePartner(userId) {
            try {
                const confirmed = confirm('Ativar parceria por 1 ano? Assinaturas ativas serão canceladas.');
                if (!confirmed) return;
                const resp = await fetch(`/admin/user/${userId}/subscription/partner`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await resp.json();
                if (resp.ok && data.success) {
                    alert('Parceria ativada por 1 ano.');
                    refreshData();
                } else {
                    alert(data.error || 'Falha ao ativar parceria');
                }
            } catch (err) {
                console.error('Erro ao ativar parceria:', err);
                alert('Erro ao ativar parceria');
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

@admin_bp.route('/payments')
@require_admin()
def admin_payments_page():
    """Página de controle de pagamentos de usuários (registro manual e histórico)."""
    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagamentos de Usuário - Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .admin-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem 0; }
        .card { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-section { margin-top: 1.5rem; }
        .badge-modalidade { font-size: 0.75rem; }
    </style>
    </head>
<body style="background-color: #f8f9fa;">
    <div class="admin-header">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-0"><i class="fas fa-credit-card me-2"></i>Pagamentos de Usuário</h1>
                    <small>Registro manual mensal (PIX, Link, Cartão) e histórico</small>
                </div>
                <div>
                    <a href="/admin/dashboard" class="btn btn-outline-light"><i class="fas fa-home me-2"></i>Dashboard Admin</a>
                </div>
            </div>
        </div>
    </div>

    <div class="container my-4">
        <!-- Formulário de Registro -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Registrar Pagamento de Usuário</h5>
            </div>
            <div class="card-body">
                <form id="adminPaymentForm" class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label">Usuário *</label>
                        <input type="text" class="form-control" id="userSelectInput" list="userList" placeholder="Digite nome, email ou ID" required>
                        <datalist id="userList"></datalist>
                        <input type="hidden" id="selectedUserId">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Valor (R$) *</label>
                        <input type="number" step="0.01" min="0" class="form-control" id="valorInput" placeholder="Ex: 29.90" required>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Dias de acesso *</label>
                        <input type="number" min="1" class="form-control" id="diasInput" placeholder="Ex: 30" value="30" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Modalidade *</label>
                        <select class="form-select" id="modalidadeSelect" required>
                            <option value="PIX">PIX</option>
                            <option value="LINK_PAGAMENTO">Link de pagamento</option>
                            <option value="CARTAO_CREDITO">Cartão Crédito</option>
                            <option value="CARTAO_DEBITO">Cartão Débito</option>
                            <option value="DINHEIRO">Dinheiro</option>
                            <option value="PARCERIA">Parceria (1 ano)</option>
                            <option value="OUTROS">Outros</option>
                        </select>
                    </div>

                    <!-- Checkbox Parceiria: ao marcar, valor=0, dias=365, modalidade=PARCERIA -->
                    <div class="col-md-2 d-flex align-items-end">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="parceiriaCheckbox">
                            <label class="form-check-label" for="parceiriaCheckbox">Parceiria</label>
                        </div>
                    </div>

                    <div class="col-12 d-flex align-items-center gap-2">
                        <button type="submit" class="btn btn-primary"><i class="fas fa-save me-2"></i>Registrar Pagamento</button>
                        <button type="button" class="btn btn-outline-secondary" id="toggleObsBtn">
                            <i class="fas fa-sticky-note me-1"></i>Adicionar observações
                        </button>
                    </div>
                    <div class="col-12">
                        <div id="observacoesContainer" class="mt-2" style="display:none;">
                            <label class="form-label">Observações</label>
                            <textarea class="form-control" id="observacoesInput" rows="2" placeholder="Opcional: info da maquininha, referência PIX ou link..."></textarea>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <!-- Histórico -->
        <div class="card form-section">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Histórico de Pagamentos (Admin)</h5>
                <button class="btn btn-outline-secondary btn-sm" id="refreshHistoryBtn"><i class="fas fa-sync me-1"></i>Atualizar</button>
            </div>
            <div class="card-body" id="historyContainer">
                <div class="text-muted">Carregando histórico...</div>
            </div>
        </div>
    </div>

    <script>
        let allUsers = [];

        async function loadUsersForSelect() {
            const resp = await fetch('/admin/users');
            const data = await resp.json();
            const list = document.getElementById('userList');
            list.innerHTML = '';
            if (data.success && data.data && Array.isArray(data.data)) {
                allUsers = data.data;
                renderUserOptions(allUsers);
            } else {
                renderUserOptions([]);
            }
        }

        function renderUserOptions(users) {
            const list = document.getElementById('userList');
            list.innerHTML = '';
            if (!users || users.length === 0) {
                // Sem usuários, deixar a lista vazia
                return;
            }
            users.forEach(u => {
                const opt = document.createElement('option');
                opt.value = `${u.id} - ${u.username} (${u.email})`;
                opt.dataset.id = u.id;
                list.appendChild(opt);
            });
        }

        function formatCurrencyBRL(value) {
            return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        }

        async function loadHistory() {
            const resp = await fetch('/admin/payments/history');
            const data = await resp.json();
            const container = document.getElementById('historyContainer');
            if (!data.success) {
                container.innerHTML = `<div class="text-danger">Erro ao carregar histórico: ${data.error || data.message || 'Erro desconhecido'}</div>`;
                return;
            }
            const items = data.data || [];
            if (items.length === 0) {
                container.innerHTML = '<div class="text-muted">Nenhum pagamento registrado.</div>';
                return;
            }
            container.innerHTML = items.map(p => `
                <div class="d-flex align-items-center border rounded p-2 mb-2">
                    <div class="me-3 text-success"><i class="fas fa-receipt"></i></div>
                    <div class="flex-grow-1">
                        <div class="fw-bold">${p.username}</div>
                        <div class="small text-muted">${new Date(p.action_date).toLocaleString('pt-BR')}</div>
                        <div class="fw-bold text-success">${formatCurrencyBRL(p.price)}</div>
                        <div class="small">Modalidade: <span class="badge bg-info">${p.modalidade || '-'}</span></div>
                        ${p.details ? `<div class="small text-muted">${p.details}</div>` : ''}
                        <div class="small">Dias adicionados: <span class="badge bg-primary">${p.days}</span></div>
                    </div>
                </div>
            `).join('');
        }

        document.getElementById('adminPaymentForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const userId = document.getElementById('selectedUserId').value;
            let valor = parseFloat(document.getElementById('valorInput').value);
            let days = parseInt(document.getElementById('diasInput').value, 10);
            const modalidade = document.getElementById('modalidadeSelect').value;
            const observacoes = document.getElementById('observacoesInput').value;

            if (!userId || !modalidade) {
                alert('Selecione o usuário e a modalidade.');
                return;
            }

            // Regras especiais para PARCERIA: 1 ano de acesso, permite valor 0
            if (modalidade === 'PARCERIA') {
                days = 365;
                if (isNaN(valor) || valor < 0) valor = 0;
            } else {
                if (isNaN(valor) || valor <= 0 || isNaN(days) || days <= 0) {
                    alert('Preencha corretamente: Valor (>0) e Dias (>0).');
                    return;
                }
            }

            const resp = await fetch(`/admin/user/${userId}/payment/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ valor, days, modalidade, observacoes })
            });
            const data = await resp.json();
            if (resp.ok && data.success) {
                alert('Pagamento registrado e acesso atualizado.');
                document.getElementById('adminPaymentForm').reset();
                loadHistory();
            } else {
                alert(data.error || data.message || 'Erro ao registrar pagamento');
            }
        });

        document.getElementById('refreshHistoryBtn').addEventListener('click', loadHistory);

        // Seleção de usuário em único input com datalist
        function updateSelectedUserIdFromInput() {
            const input = document.getElementById('userSelectInput');
            const hidden = document.getElementById('selectedUserId');
            const list = document.getElementById('userList');
            const val = (input.value || '').trim();
            hidden.value = '';
            if (!val) return;

            // Tentar casar com uma opção da lista
            let matchedId = '';
            for (const opt of list.options) {
                if (opt.value === val) { matchedId = opt.dataset.id; break; }
            }
            // Se não casou exatamente, tentar extrair ID do início do texto
            if (!matchedId) {
                const m = val.match(/^\s*(\d+)/);
                if (m) matchedId = m[1];
            }
            // Se ainda não, tentar encontrar uma única correspondência por nome/email/id
            if (!matchedId) {
                const term = val.toLowerCase();
                const matches = allUsers.filter(u => {
                    return String(u.id).includes(term) ||
                           (u.username || '').toLowerCase().includes(term) ||
                           (u.email || '').toLowerCase().includes(term);
                });
                if (matches.length === 1) matchedId = matches[0].id;
            }
            hidden.value = matchedId;
        }

        const userSelectInput = document.getElementById('userSelectInput');
        if (userSelectInput) {
            userSelectInput.addEventListener('input', updateSelectedUserIdFromInput);
            userSelectInput.addEventListener('change', updateSelectedUserIdFromInput);
        }

        // Botão para mostrar/ocultar observações
        const toggleObsBtn = document.getElementById('toggleObsBtn');
        const observacoesContainer = document.getElementById('observacoesContainer');
        if (toggleObsBtn && observacoesContainer) {
            toggleObsBtn.addEventListener('click', () => {
                const isVisible = observacoesContainer.style.display !== 'none';
                observacoesContainer.style.display = isVisible ? 'none' : 'block';
                toggleObsBtn.innerHTML = isVisible
                    ? '<i class="fas fa-sticky-note me-1"></i>Adicionar observações'
                    : '<i class="fas fa-eye-slash me-1"></i>Ocultar observações';
            });
        }

        // Checkbox "Parceiria": auto-preenche e trava os campos
        const parceiriaCheckbox = document.getElementById('parceiriaCheckbox');
        if (parceiriaCheckbox) {
            parceiriaCheckbox.addEventListener('change', function() {
                const valorInput = document.getElementById('valorInput');
                const diasInput = document.getElementById('diasInput');
                const modalidadeSelect = document.getElementById('modalidadeSelect');
                if (this.checked) {
                    // Guardar valores anteriores
                    valorInput.dataset.prev = valorInput.value;
                    diasInput.dataset.prev = diasInput.value;
                    modalidadeSelect.dataset.prev = modalidadeSelect.value;

                    // Aplicar regras de parceria
                    valorInput.value = 0;
                    diasInput.value = 365;
                    modalidadeSelect.value = 'PARCERIA';

                    // Travar edição enquanto marcado
                    valorInput.disabled = true;
                    diasInput.disabled = true;
                    modalidadeSelect.disabled = true;
                } else {
                    // Liberar edição e restaurar valores anteriores
                    valorInput.disabled = false;
                    diasInput.disabled = false;
                    modalidadeSelect.disabled = false;
                    if (valorInput.dataset.prev !== undefined) valorInput.value = valorInput.dataset.prev;
                    if (diasInput.dataset.prev !== undefined) diasInput.value = diasInput.dataset.prev;
                    if (modalidadeSelect.dataset.prev !== undefined) modalidadeSelect.value = modalidadeSelect.dataset.prev;
                }
            });
        }

        document.addEventListener('DOMContentLoaded', async () => {
            await loadUsersForSelect();
            await loadHistory();
        });
    </script>
    <script>
        function logout() {
            if (confirm('Tem certeza que deseja sair do sistema?')) {
                fetch('/api/logout', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
                    .then(() => { localStorage.clear(); sessionStorage.clear(); window.location.href = '/'; })
                    .catch(() => { localStorage.clear(); sessionStorage.clear(); window.location.href = '/'; });
            }
        }
    </script>
</body>
</html>
    ''')

@admin_bp.route('/user/<int:user_id>/payment/register', methods=['POST'])
@require_admin()
def admin_register_user_payment(user_id):
    """Registra um pagamento manual para o usuário e adiciona dias de acesso.

    Campos esperados (JSON):
    - valor: float (>0)
    - days: int (>0)
    - modalidade: string (um dos PaymentMethod)
    - observacoes: string (opcional)
    """
    try:
        from src.models.assinatura import Subscription
        from src.models.historico_assinatura import SubscriptionHistory
        from src.models.pagamento import PaymentMethod

        user = User.query.get_or_404(user_id)

        data = request.get_json(silent=True) or {}
        valor = float(data.get('valor', 0))
        days = int(data.get('days', 0))
        modalidade = data.get('modalidade')
        observacoes = (data.get('observacoes') or '').strip()

        # Validar modalidade contra enum
        try:
            _ = PaymentMethod[modalidade]
        except Exception:
            return jsonify({'success': False, 'error': 'Modalidade inválida'}), 400

        # Regras de validação específicas
        if modalidade == 'PARCERIA':
            # Permite valor 0 e força 365 dias
            if valor < 0:
                return jsonify({'success': False, 'error': 'Valor inválido'}), 400
            days = 365
            # Observação padrão se não houver
            if not observacoes:
                observacoes = 'Parceria: acesso concedido por 1 ano'
        else:
            if valor <= 0:
                return jsonify({'success': False, 'error': 'Valor inválido'}), 400
            if days <= 0:
                return jsonify({'success': False, 'error': 'Dias inválidos'}), 400

        # Buscar assinatura ativa
        active_sub = Subscription.query.filter_by(user_id=user.id, status='active').filter(
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.created_at.desc()).first()

        previous_end_str = None
        action = 'updated'
        plan_type = 'monthly'

        if active_sub:
            previous_end_str = active_sub.end_date.strftime('%d/%m/%Y')
            # Somar dias ao fim atual
            active_sub.end_date = active_sub.end_date + timedelta(days=days)
            db.session.add(active_sub)
        else:
            # Criar nova assinatura ativa com os dias informados
            new_sub = Subscription(user_id=user.id, plan_type=plan_type, auto_renew=False)
            new_sub.end_date = new_sub.start_date + timedelta(days=days)
            new_sub.status = 'active'
            db.session.add(new_sub)
            db.session.flush()
            active_sub = new_sub
            action = 'created'

        # Registrar histórico com detalhes do pagamento admin
        details = f"Pagamento admin: modalidade={modalidade}; valor={valor}; dias={days}; obs={observacoes}"
        if previous_end_str:
            details += f"; fim_anterior={previous_end_str}"

        history = SubscriptionHistory.create_history_entry(
            user_id=user.id,
            action=action,
            plan_type=plan_type,
            price=valor,
            subscription_id=active_sub.id,
            start_date=active_sub.start_date,
            end_date=active_sub.end_date,
            details=details
        )

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Pagamento registrado e acesso atualizado',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'price': valor,
                'days': days,
                'modalidade': modalidade,
                'subscription': active_sub.to_dict(),
                'history': history.to_dict() if hasattr(history, 'to_dict') else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao registrar pagamento: {str(e)}'}), 500

@admin_bp.route('/payments/history', methods=['GET'])
@require_admin()
def admin_payments_history():
    """Lista histórico de pagamentos administrativos (filtrando entradas de histórico geradas por admin)."""
    try:
        from src.models.historico_assinatura import SubscriptionHistory

        # Buscar últimas 50 entradas com detalhe iniciando com 'Pagamento admin:'
        query = SubscriptionHistory.query.filter(
            SubscriptionHistory.details.like('Pagamento admin:%')
        ).order_by(SubscriptionHistory.action_date.desc()).limit(50)

        items = []
        for h in query.all():
            # Parse básico de detalhes para extrair modalidade e dias
            detalhes = h.details or ''
            def extract(key, cast=None):
                try:
                    # padrão key=valor; ou key=valor fim
                    part = next((p for p in detalhes.split(';') if p.strip().startswith(f"{key}=")), None)
                    if not part:
                        return None
                    val = part.split('=', 1)[1].strip()
                    return cast(val) if cast else val
                except Exception:
                    return None

            modalidade = extract('modalidade')
            if not modalidade:
                # Fallback: tentar identificar por valores conhecidos na string de detalhes
                consts = ['PIX','DINHEIRO','CARTAO_CREDITO','CARTAO_DEBITO','LINK_PAGAMENTO','OUTROS','PARCERIA']
                try:
                    modalidade = next((c for c in consts if c in detalhes), None)
                except Exception:
                    modalidade = None
            days = extract('dias', cast=lambda v: int(''.join(ch for ch in v if ch.isdigit())))
            obs = extract('obs')

            user = User.query.get(h.user_id)
            items.append({
                'user_id': h.user_id,
                'username': getattr(user, 'username', None),
                'action_date': h.action_date.isoformat() if getattr(h, 'action_date', None) else None,
                'price': getattr(h, 'price', None),
                'days': days,
                'modalidade': modalidade,
                'details': obs,
            })

        return jsonify({'success': True, 'data': items}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro ao listar histórico: {str(e)}'}), 500


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
        
        # Limpeza ordenada de dependências evitando bulk delete para não violar FKs no MySQL
        # 1. Excluir dados relacionados a pacientes do usuário, na ordem: payment_sessions -> sessions -> appointments -> payments -> diary_entries -> patient
        patients = Patient.query.filter_by(user_id=user_id).all()
        for patient in patients:
            # Appointments e suas sessões/pagamentos
            appointments = Appointment.query.filter_by(user_id=user_id, patient_id=patient.id).all()
            for appt in appointments:
                # Sessions e suas associações de pagamento
                sessions = Session.query.filter_by(appointment_id=appt.id).all()
                for sess in sessions:
                    # PaymentSessions vinculados à sessão
                    sess_payment_links = PaymentSession.query.filter_by(session_id=sess.id).all()
                    for ps in sess_payment_links:
                        db.session.delete(ps)
                    db.session.delete(sess)
                # Após remover sessões, remover o agendamento
                db.session.delete(appt)

            # Pagamentos do paciente e suas associações
            payments = Payment.query.filter_by(user_id=user_id, patient_id=patient.id).all()
            for pay in payments:
                pay_links = PaymentSession.query.filter_by(payment_id=pay.id).all()
                for ps in pay_links:
                    db.session.delete(ps)
                db.session.delete(pay)

            # Diário do paciente
            diaries = DiaryEntry.query.filter_by(user_id=user_id, patient_id=patient.id).all()
            for de in diaries:
                db.session.delete(de)

            # Finalmente, remover o paciente
            db.session.delete(patient)

        # 2. Excluir funcionários do usuário
        funcionarios = Funcionario.query.filter_by(user_id=user_id).all()
        for func in funcionarios:
            db.session.delete(func)

        # 3. Excluir especialidades do usuário
        especialidades = Especialidade.query.filter_by(user_id=user_id).all()
        for esp in especialidades:
            db.session.delete(esp)

        # 4. Excluir histórico de assinaturas
        subs_hist = SubscriptionHistory.query.filter_by(user_id=user_id).all()
        for sh in subs_hist:
            db.session.delete(sh)

        # 5. Excluir assinaturas
        subs = Subscription.query.filter_by(user_id=user_id).all()
        for s in subs:
            db.session.delete(s)

        # 6. Excluir tokens de reset de senha
        reset_tokens = PasswordResetToken.query.filter_by(user_id=user_id).all()
        for rt in reset_tokens:
            db.session.delete(rt)

        # 6b. Excluir tokens de verificação de email
        email_tokens = EmailVerificationToken.query.filter_by(user_id=user_id).all()
        for et in email_tokens:
            db.session.delete(et)

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

# Novo endpoint: ativar parceria por 1 ano (365 dias)
@admin_bp.route('/user/<int:user_id>/subscription/partner', methods=['POST'])
@require_admin()
def admin_activate_partner(user_id):
    """Concede parceria ao usuário com 1 ano de acesso sem cobrança."""
    try:
        user = User.query.get_or_404(user_id)

        # Cancelar assinaturas ativas anteriores
        active_subs = Subscription.query.filter_by(user_id=user_id, status='active').filter(
            Subscription.end_date > datetime.utcnow()
        ).all()
        for sub in active_subs:
            sub.cancel()

        # Criar assinatura 'trial' com 365 dias e preço 0
        new_sub = Subscription(user_id=user_id, plan_type='trial', auto_renew=False)
        new_sub.end_date = new_sub.start_date + timedelta(days=365)
        new_sub.price = 0.0
        new_sub.status = 'active'

        db.session.add(new_sub)
        db.session.flush()

        # Registrar histórico
        SubscriptionHistory.create_history_entry(
            user_id=user_id,
            action='created',
            plan_type='partner',
            price=0.0,
            subscription_id=new_sub.id,
            start_date=new_sub.start_date,
            end_date=new_sub.end_date,
            details='Parceria: acesso concedido por 1 ano'
        )

        db.session.commit()
        return jsonify({'success': True, 'message': 'Parceria ativada por 1 ano'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao ativar parceria: {str(e)}'}), 500