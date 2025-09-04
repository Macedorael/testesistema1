// Verificar se o usuário está logado antes de carregar a página
async function checkLoginStatus() {
    try {
        const response = await fetch('/api/me');
        if (response.status === 401) {
            // Usuário não está logado - redirecionar para login
            window.location.href = 'entrar.html';
            return false;
        }
        return true;
    } catch (error) {
        console.error('Erro ao verificar status de login:', error);
        // Em caso de erro, redirecionar para login
        window.location.href = 'entrar.html';
        return false;
    }
}

// Gerenciamento de Assinaturas
class SubscriptionManager {
    constructor() {
        this.currentSubscription = null;
        this.plans = {};
        this.init();
    }
    
    async init() {
        // Verificar login antes de carregar qualquer coisa
        const isLoggedIn = await checkLoginStatus();
        if (!isLoggedIn) {
            return; // Para a execução se não estiver logado
        }
        
        await this.loadPlans();
        await this.loadCurrentSubscription();
        this.setupEventListeners();
    }
    
    async loadPlans() {
        try {
            const response = await fetch('/api/subscriptions/plans');
            const data = await response.json();
            
            if (data.success) {
                this.plans = data.plans;
                this.renderPlans();
            } else {
                this.showError('Erro ao carregar planos');
            }
        } catch (error) {
            console.error('Erro ao carregar planos:', error);
            this.showError('Erro ao carregar planos');
        }
    }
    
    async loadCurrentSubscription() {
        try {
            const response = await fetch('/api/subscriptions/my-subscription');
            const data = await response.json();
            
            if (response.status === 401) {
                // Usuário não está logado - não tem assinatura
                this.currentSubscription = null;
                this.renderCurrentSubscription();
                return;
            }
            
            if (data.success) {
                this.currentSubscription = data.subscription;
                this.renderCurrentSubscription();
            } else {
                // Erro na API - assumir que não tem assinatura
                this.currentSubscription = null;
                this.renderCurrentSubscription();
            }
        } catch (error) {
            console.error('Erro ao carregar assinatura:', error);
            // Em caso de erro, assumir que não tem assinatura
            this.currentSubscription = null;
            this.renderCurrentSubscription();
        }
    }
    
    renderPlans() {
        const plansGrid = document.getElementById('plansGrid');
        plansGrid.innerHTML = '';
        
        const planNames = {
            'monthly': 'Mensal',
            'quarterly': 'Trimestral',
            'biannual': 'Semestral',
            'annual': 'Anual'
        };
        
        const planFeatures = {
            'monthly': ['Acesso completo ao sistema', 'Suporte por email', 'Backup automático'],
            'quarterly': ['Acesso completo ao sistema', 'Suporte por email', 'Backup automático', '5% de desconto'],
            'biannual': ['Acesso completo ao sistema', 'Suporte prioritário', 'Backup automático', '10% de desconto'],
            'annual': ['Acesso completo ao sistema', 'Suporte prioritário', 'Backup automático', '15% de desconto', 'Recursos premium']
        };
        
        Object.entries(this.plans).forEach(([planType, planInfo]) => {
            const isCurrentPlan = this.currentSubscription && this.currentSubscription.plan_type === planType;
            
            const planCard = document.createElement('div');
            planCard.className = `plan-card ${isCurrentPlan ? 'current' : ''}`;
            planCard.onclick = () => this.selectPlan(planType);
            
            planCard.innerHTML = `
                <div class="plan-name">${planNames[planType]}</div>
                <div class="plan-price">R$ ${planInfo.price.toFixed(2)}</div>
                <div class="plan-period">por ${planInfo.duration_months} ${planInfo.duration_months === 1 ? 'mês' : 'meses'}</div>
                <ul class="plan-features">
                    ${planFeatures[planType].map(feature => `<li>${feature}</li>`).join('')}
                </ul>
                <button class="btn ${isCurrentPlan ? 'btn-secondary' : 'btn-primary'}">
                    ${isCurrentPlan ? 'Plano Atual' : 'Selecionar'}
                </button>
            `;
            
            plansGrid.appendChild(planCard);
        });
    }
    
    renderCurrentSubscription() {
        const currentSubscriptionDiv = document.getElementById('currentSubscription');
        const noSubscriptionDiv = document.getElementById('noSubscription');
        const actionsWithSubscription = document.getElementById('actionsWithSubscription');
        const actionsWithoutSubscription = document.getElementById('actionsWithoutSubscription');
        
        if (this.currentSubscription && this.currentSubscription.status === 'active') {
            // Usuário tem assinatura ativa
            currentSubscriptionDiv.style.display = 'block';
            noSubscriptionDiv.style.display = 'none';
            actionsWithSubscription.style.display = 'block';
            actionsWithoutSubscription.style.display = 'none';
            
            const planNames = {
                'monthly': 'Mensal',
                'quarterly': 'Trimestral',
                'biannual': 'Semestral',
                'annual': 'Anual'
            };
            
            document.getElementById('currentPlan').textContent = planNames[this.currentSubscription.plan_type] || this.currentSubscription.plan_type;
            
            const statusElement = document.getElementById('currentStatus');
            statusElement.textContent = this.currentSubscription.status;
            statusElement.className = `info-value status-${this.currentSubscription.status}`;
            
            document.getElementById('currentPrice').textContent = `R$ ${this.currentSubscription.price.toFixed(2)}`;
            
            const endDate = new Date(this.currentSubscription.end_date);
            document.getElementById('nextBilling').textContent = endDate.toLocaleDateString('pt-BR');
            
            document.getElementById('daysRemaining').textContent = `${this.currentSubscription.days_remaining || 0} dias`;
            
            document.getElementById('autoRenewStatus').textContent = this.currentSubscription.auto_renew ? 'Ativada' : 'Desativada';
            
            document.getElementById('autoRenewToggle').checked = this.currentSubscription.auto_renew;
        } else {
            // Usuário não tem assinatura ativa
            currentSubscriptionDiv.style.display = 'none';
            noSubscriptionDiv.style.display = 'block';
            actionsWithSubscription.style.display = 'none';
            actionsWithoutSubscription.style.display = 'block';
        }
    }
    
    async selectPlan(planType) {
        if (this.currentSubscription && this.currentSubscription.plan_type === planType) {
            this.showError('Você já possui este plano ativo');
            return;
        }
        
        const planNames = {
            'monthly': 'Mensal',
            'quarterly': 'Trimestral',
            'biannual': 'Semestral',
            'annual': 'Anual'
        };
        
        const confirmMessage = `Deseja assinar o plano ${planNames[planType]}?`;
        
        if (confirm(confirmMessage)) {
            this.processSubscription(planType);
        }
    }
    
    async renewSubscription() {
        if (!this.currentSubscription) {
            this.showError('Nenhuma assinatura encontrada');
            return;
        }
        
        // Mostrar modal de seleção de planos
        this.showPlanSelectionModal();
    }
    
    showPlanSelectionModal() {
        const planNames = {
            'monthly': 'Mensal',
            'quarterly': 'Trimestral',
            'biannual': 'Semestral',
            'annual': 'Anual'
        };
        
        // Hierarquia dos planos (do menor para o maior)
        const planHierarchy = {
            'monthly': 1,
            'quarterly': 2,
            'biannual': 3,
            'annual': 4
        };
        
        const currentPlanLevel = planHierarchy[this.currentSubscription.plan_type];
        
        let modalHTML = `
            <div id="planModal" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            ">
                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                ">
                    <h3 style="margin-bottom: 20px; text-align: center; color: #2c3e50;">Escolha seu novo plano</h3>
                    <p style="text-align: center; color: #6c757d; margin-bottom: 25px;">Selecione o plano que deseja para sua renovação:</p>
                    <div style="display: grid; gap: 15px;">`;
        
        Object.entries(this.plans).forEach(([planType, planInfo]) => {
            const isCurrentPlan = this.currentSubscription.plan_type === planType;
            const planLevel = planHierarchy[planType];
            const isDowngrade = planLevel < currentPlanLevel;
            const isDisabled = isDowngrade;
            
            modalHTML += `
                <div style="
                    border: 2px solid ${isCurrentPlan ? '#28a745' : (isDisabled ? '#dc3545' : '#e9ecef')};
                    border-radius: 8px;
                    padding: 15px;
                    cursor: ${isDisabled ? 'not-allowed' : 'pointer'};
                    transition: all 0.3s ease;
                    background: ${isCurrentPlan ? '#f8fff9' : (isDisabled ? '#f8d7da' : 'white')};
                    opacity: ${isDisabled ? '0.6' : '1'};
                " ${!isDisabled ? `onclick="subscriptionManager.selectRenewalPlan('${planType}')" onmouseover="this.style.borderColor='#007bff'" onmouseout="this.style.borderColor='${isCurrentPlan ? '#28a745' : '#e9ecef'}'"` : ''}>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: ${isDisabled ? '#721c24' : '#2c3e50'};">${planNames[planType]}</strong>
                            ${isCurrentPlan ? '<span style="color: #28a745; font-size: 0.9em; margin-left: 10px;">(Plano Atual)</span>' : ''}
                            ${isDisabled ? '<span style="color: #721c24; font-size: 0.9em; margin-left: 10px;">(Não disponível - plano inferior)</span>' : ''}
                            <div style="color: ${isDisabled ? '#721c24' : '#6c757d'}; font-size: 0.9em;">${planInfo.duration_months} ${planInfo.duration_months === 1 ? 'mês' : 'meses'}</div>
                        </div>
                        <div style="font-size: 1.2em; font-weight: bold; color: ${isDisabled ? '#721c24' : '#007bff'};">
                            R$ ${planInfo.price.toFixed(2)}
                        </div>
                    </div>
                </div>`;
        });
        
        modalHTML += `
                    </div>
                    <div style="text-align: center; margin-top: 25px;">
                        <button onclick="subscriptionManager.closePlanModal()" style="
                            background: #6c757d;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 1em;
                        ">Cancelar</button>
                    </div>
                </div>
            </div>`;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    async selectRenewalPlan(planType) {
        try {
            // Validar se o plano selecionado não é inferior ao atual
            const planHierarchy = {
                'monthly': 1,
                'quarterly': 2,
                'biannual': 3,
                'annual': 4
            };
            
            const currentPlanLevel = planHierarchy[this.currentSubscription.plan_type];
            const selectedPlanLevel = planHierarchy[planType];
            
            if (selectedPlanLevel < currentPlanLevel) {
                alert('Não é possível renovar para um plano de menor duração que o atual. Por favor, escolha um plano igual ou superior.');
                return;
            }
            
            const planNames = {
                'monthly': 'Mensal',
                'quarterly': 'Trimestral',
                'biannual': 'Semestral',
                'annual': 'Anual'
            };
            
            const confirmed = confirm(`Tem certeza que deseja renovar para o plano ${planNames[planType]}?`);
            if (!confirmed) return;
            
            this.closePlanModal();
            
            // Mostrar loading
            const renewButton = document.querySelector('.renew-btn');
            if (renewButton) {
                renewButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
                renewButton.disabled = true;
            }
            
            // Renovar com o novo plano em uma única operação
            const renewResponse = await fetch('/api/subscriptions/renew-with-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plan_type: planType,
                    auto_renew: this.currentSubscription.auto_renew
                })
            });
            
            if (!renewResponse.ok) {
                const errorData = await renewResponse.json();
                throw new Error(errorData.error || 'Erro ao renovar assinatura');
            }
            
            // Recarregar a página para mostrar a nova assinatura
            window.location.reload();
            
        } catch (error) {
            console.error('Erro ao renovar assinatura:', error);
            alert('Erro ao renovar assinatura. Tente novamente.');
            
            // Restaurar botão
            const renewButton = document.querySelector('.renew-btn');
            if (renewButton) {
                renewButton.innerHTML = '<i class="fas fa-sync-alt"></i> Renovar Agora';
                renewButton.disabled = false;
            }
        }
    }
    
    closePlanModal() {
        const modal = document.getElementById('planModal');
        if (modal) {
            modal.remove();
        }
    }
    
    async updateAutoRenew() {
        if (!this.currentSubscription) {
            this.showError('Nenhuma assinatura encontrada');
            return;
        }
        
        const autoRenew = document.getElementById('autoRenewToggle').checked;
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/subscriptions/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    auto_renew: autoRenew
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Configuração de renovação atualizada');
                await this.loadCurrentSubscription();
            } else {
                this.showError(data.error || 'Erro ao atualizar configuração');
            }
        } catch (error) {
            console.error('Erro ao atualizar renovação:', error);
            this.showError('Erro ao atualizar configuração');
        } finally {
            this.showLoading(false);
        }
    }
    
    async cancelSubscription() {
        if (!this.currentSubscription) {
            this.showError('Nenhuma assinatura encontrada');
            return;
        }
        
        if (!confirm('Tem certeza que deseja cancelar sua assinatura? Esta ação não pode ser desfeita e você será desconectado do sistema.')) {
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/subscriptions/cancel', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message);
                
                // Se o logout foi feito (indicado pela propriedade logout), redirecionar para login
                if (data.logout) {
                    setTimeout(() => {
                        window.location.href = '/entrar.html';
                    }, 2000);
                } else {
                    await this.loadCurrentSubscription();
                    this.renderPlans();
                }
            } else {
                this.showError(data.error || 'Erro ao cancelar assinatura');
            }
        } catch (error) {
            console.error('Erro ao cancelar assinatura:', error);
            this.showError('Erro ao cancelar assinatura');
        } finally {
            this.showLoading(false);
        }
    }
    
    // Função para processar a assinatura
    async processSubscription(planType) {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/subscriptions/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plan_type: planType,
                    auto_renew: true
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Assinatura criada com sucesso! Redirecionando para o sistema...');
                
                // Redirecionar para o sistema principal após 2 segundos
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                this.showError(data.error || 'Erro ao processar assinatura');
            }
        } catch (error) {
            console.error('Erro ao processar assinatura:', error);
            this.showError('Erro de conexão. Tente novamente.');
        } finally {
            this.showLoading(false);
        }
    }
    
    // Função para processar assinatura de usuário não logado
    async processGuestSubscription(planType, email, password) {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/subscriptions/subscribe-guest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    plan_type: planType,
                    auto_renew: true
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message || 'Assinatura criada com sucesso!');
                
                // Redirecionar para login após 2 segundos
                setTimeout(() => {
                    window.location.href = 'entrar.html';
                }, 2000);
            } else {
                this.showError(data.error || 'Erro ao processar assinatura');
            }
        } catch (error) {
            console.error('Erro ao processar assinatura:', error);
            this.showError('Erro de conexão. Tente novamente.');
        } finally {
            this.showLoading(false);
        }
    }
    
    setupEventListeners() {
        // Event listeners já são configurados nos métodos de renderização
    }
    
    showLoading(show) {
        document.getElementById('loading').style.display = show ? 'block' : 'none';
    }
    
    showSuccess(message) {
        const alert = document.getElementById('successAlert');
        alert.textContent = message;
        alert.style.display = 'block';
        
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    }
    
    showError(message) {
        const alert = document.getElementById('errorAlert');
        alert.textContent = message;
        alert.style.display = 'block';
        
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    }
}

// Funções globais para os botões
let subscriptionManager;

function renewSubscription() {
    subscriptionManager.renewSubscription();
}

function updateAutoRenew() {
    subscriptionManager.updateAutoRenew();
}

function cancelSubscription() {
    subscriptionManager.cancelSubscription();
}

function goToSystem() {
    window.location.href = '/';
}

function logout() {
    if (confirm('Tem certeza que deseja sair do sistema?')) {
        fetch('/api/logout', {
            method: 'POST'
        }).then(() => {
            window.location.href = '/';
        }).catch(() => {
            // Mesmo se der erro, redireciona para a tela inicial
            window.location.href = '/';
        });
    }
}

function viewHistory() {
    window.location.href = '/subscription-history.html';
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    subscriptionManager = new SubscriptionManager();
});