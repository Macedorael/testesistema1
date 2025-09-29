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
        this.isProcessing = false; // Adicionar controle de processamento
        this.init();
    }
    
    async init() {
        console.log('🔄 Iniciando SubscriptionManager...');
        
        // Verificar login antes de carregar qualquer coisa
        const isLoggedIn = await checkLoginStatus();
        console.log('🔐 Status de login:', isLoggedIn);
        
        if (!isLoggedIn) {
            console.log('❌ Usuário não logado, parando execução');
            return; // Para a execução se não estiver logado
        }
        
        console.log('📋 Carregando planos...');
        await this.loadPlans();
        
        console.log('📊 Carregando assinatura atual...');
        await this.loadCurrentSubscription();
        
        console.log('🎯 Configurando event listeners...');
        this.setupEventListeners();
        
        console.log('✅ SubscriptionManager inicializado com sucesso');
    }
    
    async loadPlans() {
        console.log('📋 Fazendo requisição para /api/subscriptions/plans...');
        try {
            const response = await fetch('/api/subscriptions/plans');
            console.log('📋 Resposta da API plans:', response.status, response.statusText);
            
            if (response.ok) {
                const data = await response.json();
                console.log('📋 Dados dos planos recebidos:', data);
                this.plans = data.plans;
                console.log('📋 Planos armazenados:', this.plans);
                this.renderPlans();
                console.log('📋 Planos renderizados com sucesso');
            } else {
                console.error('❌ Erro ao carregar planos:', response.status, response.statusText);
                this.showError('Erro ao carregar planos de assinatura');
            }
        } catch (error) {
            console.error('❌ Erro na requisição de planos:', error);
            this.showError('Erro ao conectar com o servidor');
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
        console.log('🎨 Iniciando renderização dos planos...');
        const plansContainer = document.getElementById('plansGrid');
        
        if (!plansContainer) {
            console.error('❌ Container de planos não encontrado!');
            return;
        }
        
        console.log('🎨 Container encontrado, planos disponíveis:', this.plans);
        
        if (!this.plans || Object.keys(this.plans).length === 0) {
            console.warn('⚠️ Nenhum plano disponível para renderizar');
            plansContainer.innerHTML = '<p class="text-center">Nenhum plano disponível no momento.</p>';
            return;
        }

        let plansHTML = '';
        
        for (const [planType, plan] of Object.entries(this.plans)) {
            console.log(`🎨 Renderizando plano: ${planType}`, plan);
            
            const savings = plan.savings ? `<div class="savings">Economize R$ ${plan.savings.toFixed(2)}</div>` : '';
            
            plansHTML += `
                <div class="plan-card ${planType === 'annual' ? 'recommended' : ''}">
                    ${planType === 'annual' ? '<div class="recommended-badge">Recomendado</div>' : ''}
                    <h3>${plan.name}</h3>
                    <div class="price">R$ ${plan.price.toFixed(2)}</div>
                    <div class="duration">${plan.duration}</div>
                    ${savings}
                    <p class="description">${plan.description}</p>
                    <button class="btn btn-primary select-plan-btn" data-plan="${planType}">
                        Selecionar Plano
                    </button>
                </div>
            `;
        }
        
        plansContainer.innerHTML = plansHTML;
        console.log('🎨 HTML dos planos inserido no container');
        
        // Mostrar a seção de planos
        const plansSection = document.getElementById('plansSection');
        if (plansSection) {
            plansSection.style.display = 'block';
            console.log('🎨 Seção de planos exibida');
        }
        
        // Adicionar event listeners aos botões
        const planButtons = plansContainer.querySelectorAll('.select-plan-btn');
        console.log(`🎨 Encontrados ${planButtons.length} botões de plano`);
        
        planButtons.forEach(button => {
            const planType = button.getAttribute('data-plan');
            console.log(`🎨 Adicionando listener para plano: ${planType}`);
            
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log(`🎯 Clique no plano: ${planType}`);
                
                if (this.isProcessing) {
                    console.log('⏳ Processamento em andamento, ignorando clique');
                    return;
                }
                
                this.selectPlanWithDebounce(planType, button);
            });
        });
        
        console.log('🎨 Renderização dos planos concluída com sucesso');
    }
    
    renderCurrentSubscription() {
        const currentSubDiv = document.getElementById('currentSubscription');
        if (!currentSubDiv) return;
        
        if (this.currentSubscription && this.currentSubscription.status === 'active') {
            const planNames = {
                'monthly': 'Mensal',
                'quarterly': 'Trimestral',
                'biannual': 'Semestral',
                'annual': 'Anual'
            };
            
            const planName = planNames[this.currentSubscription.plan_type] || this.currentSubscription.plan_type;
            const expiryDate = new Date(this.currentSubscription.expires_at).toLocaleDateString('pt-BR');
            
            currentSubDiv.innerHTML = `
                <div class="current-subscription">
                    <h3>Sua Assinatura Atual</h3>
                    <div class="subscription-info">
                        <p><strong>Plano:</strong> ${planName}</p>
                        <p><strong>Status:</strong> <span class="status-active">Ativo</span></p>
                        <p><strong>Expira em:</strong> ${expiryDate}</p>
                        <p><strong>Renovação Automática:</strong> ${this.currentSubscription.auto_renew ? 'Ativada' : 'Desativada'}</p>
                    </div>
                    <div class="subscription-actions">
                        <button onclick="renewSubscription()" class="btn btn-primary">Renovar Assinatura</button>
                        <button onclick="updateAutoRenew()" class="btn btn-secondary">
                            ${this.currentSubscription.auto_renew ? 'Desativar' : 'Ativar'} Renovação Automática
                        </button>
                        <button onclick="cancelSubscription()" class="btn btn-danger">Cancelar Assinatura</button>
                        <button onclick="goToSystem()" class="btn btn-success">Ir para o Sistema</button>
                    </div>
                </div>
            `;
            
            // Esconder os planos se há assinatura ativa
            const plansSection = document.querySelector('.plans-section');
            if (plansSection) {
                plansSection.style.display = 'none';
            }
        } else {
            currentSubDiv.innerHTML = '';
            // Mostrar os planos se não há assinatura ativa
            const plansSection = document.querySelector('.plans-section');
            if (plansSection) {
                plansSection.style.display = 'block';
            }
        }
    }
    
    // Nova função com proteção contra duplo clique
    async selectPlanWithDebounce(planType, button) {
        // Verificar se já está processando
        if (this.isProcessing) {
            console.log('Já processando uma assinatura...');
            return;
        }
        
        // Desabilitar botão imediatamente
        button.disabled = true;
        button.textContent = 'Processando...';
        
        try {
            await this.selectPlan(planType);
        } finally {
            // Reabilitar botão após 3 segundos (tempo suficiente para evitar duplo clique)
            setTimeout(() => {
                if (!this.isProcessing) {
                    button.disabled = false;
                    button.textContent = 'Selecionar';
                }
            }, 3000);
        }
    }

    async selectPlan(planType) {
        if (this.isProcessing) {
            return;
        }
        
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
            await this.processSubscription(planType);
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
        // Verificar se já está processando
        if (this.isProcessing) {
            console.log('Já processando uma assinatura...');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.showLoading(true);
            
            // Desabilitar todos os botões durante o processamento
            this.disableAllButtons();
            
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
                this.enableAllButtons(); // Reabilitar botões em caso de erro
            }
        } catch (error) {
            console.error('Erro ao processar assinatura:', error);
            this.showError('Erro de conexão. Tente novamente.');
            this.enableAllButtons(); // Reabilitar botões em caso de erro
        } finally {
            this.showLoading(false);
            // Não resetar isProcessing aqui se o redirecionamento vai acontecer
            if (!document.querySelector('#successAlert').style.display || document.querySelector('#successAlert').style.display === 'none') {
                this.isProcessing = false;
            }
        }
    }
    
    // Função para desabilitar todos os botões
    disableAllButtons() {
        const buttons = document.querySelectorAll('.plan-card button');
        buttons.forEach(button => {
            button.disabled = true;
            if (button.textContent === 'Selecionar') {
                button.textContent = 'Processando...';
            }
        });
    }
    
    // Função para reabilitar todos os botões
    enableAllButtons() {
        const buttons = document.querySelectorAll('.plan-card button');
        buttons.forEach(button => {
            if (!button.id.includes('current')) {
                button.disabled = false;
                if (button.textContent === 'Processando...') {
                    button.textContent = 'Selecionar';
                }
            }
        });
    }

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
        // Event listeners para botões de ação
        const renewBtn = document.getElementById('renewBtn');
        const updateAutoRenewBtn = document.getElementById('updateAutoRenewBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const historyBtn = document.getElementById('historyBtn');
        const goToSystemBtn = document.getElementById('goToSystemBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (renewBtn) {
            renewBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.isProcessing) {
                    renewSubscription();
                }
            });
        }
        
        if (updateAutoRenewBtn) {
            updateAutoRenewBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.isProcessing) {
                    updateAutoRenew();
                }
            });
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.isProcessing) {
                    cancelSubscription();
                }
            });
        }
        
        if (historyBtn) {
            historyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                viewHistory();
            });
        }
        
        if (goToSystemBtn) {
            goToSystemBtn.addEventListener('click', (e) => {
                e.preventDefault();
                goToSystem();
            });
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
        }
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
document.addEventListener('DOMContentLoaded', async function() {
    subscriptionManager = new SubscriptionManager();
    await subscriptionManager.init();
});