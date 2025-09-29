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
            
            if (response.status === 401) {
                // Usuário não está logado
                this.currentSubscription = null;
                this.renderCurrentSubscription(null);
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.subscription) {
                this.currentSubscription = data.subscription;
            } else {
                this.currentSubscription = null;
            }
            
            this.renderCurrentSubscription(this.currentSubscription);
            
        } catch (error) {
            console.error('Erro ao carregar assinatura atual:', error);
            this.currentSubscription = null;
            this.renderCurrentSubscription(null);
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
            
            const savings = plan.savings ? `<div class="savings compact">Economize R$ ${plan.savings.toFixed(2)}</div>` : '';
            
            plansHTML += `
                <div class="plan-card compact ${planType === 'annual' ? 'recommended' : ''}">
                    ${planType === 'annual' ? '<div class="recommended-badge compact">Recomendado</div>' : ''}
                    <h3 class="compact">${plan.name}</h3>
                    <div class="price compact">R$ ${plan.price.toFixed(2)}</div>
                    <div class="duration compact">${plan.duration}</div>
                    ${savings}
                    <p class="description compact">${plan.description}</p>
                    <button class="btn btn-primary select-plan-btn compact" data-plan="${planType}">
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
    
    renderCurrentSubscription(subscription) {
        console.log('renderCurrentSubscription chamada com:', subscription);
        
        const currentSubDiv = document.getElementById('currentSubscription');
        const plansDiv = document.getElementById('plansSection');
        const noSubDiv = document.getElementById('noSubscription');
        
        if (subscription && subscription.status === 'active') {
            // Mostrar seção de assinatura atual
            currentSubDiv.style.display = 'block';
            plansDiv.style.display = 'none';
            noSubDiv.style.display = 'none';
            
            // Mapear plan_type para nome do plano
            const planNames = {
                'monthly': 'Mensal',
                'quarterly': 'Trimestral',
                'biannual': 'Semestral',
                'annual': 'Anual'
            };
            
            // Preencher informações da assinatura
            document.getElementById('currentPlan').textContent = planNames[subscription.plan_type] || subscription.plan_type || 'N/A';
            document.getElementById('currentPrice').textContent = subscription.price ? `R$ ${subscription.price.toFixed(2)}` : 'N/A';
            
            // Status com estilo melhorado e compacto
            const statusElement = document.getElementById('currentStatus');
            statusElement.textContent = subscription.status === 'active' ? 'Ativo' : subscription.status;
            statusElement.className = subscription.status === 'active' ? 'value status-active compact' : 'value compact';
            
            // Calcular e mostrar dias restantes usando o campo days_remaining da API
            const daysRemaining = subscription.days_remaining || 0;
            const daysElement = document.getElementById('daysRemaining');
            daysElement.textContent = `${daysRemaining} dias`;
            
            // Aplicar cores baseadas nos dias restantes com estilo compacto
            if (daysRemaining <= 7) {
                daysElement.className = 'value days-remaining text-danger compact';
                showExpiryAlert('danger', `Sua assinatura expira em ${daysRemaining} dias!`);
            } else if (daysRemaining <= 30) {
                daysElement.className = 'value days-remaining text-warning compact';
                showExpiryAlert('warning', `Sua assinatura expira em ${daysRemaining} dias.`);
            } else {
                daysElement.className = 'value days-remaining compact';
            }
            
            // Data de expiração com estilo compacto usando end_date da API
            if (subscription.end_date) {
                const expiryDate = new Date(subscription.end_date);
                const expiryElement = document.getElementById('nextBilling');
                expiryElement.textContent = expiryDate.toLocaleDateString('pt-BR');
                expiryElement.className = 'value compact';
            } else {
                const expiryElement = document.getElementById('nextBilling');
                expiryElement.textContent = '-';
                expiryElement.className = 'value compact';
            }
            
            // Status de renovação automática com estilo compacto
            const autoRenewElement = document.getElementById('autoRenewStatus');
            const isAutoRenew = subscription.auto_renew;
            console.log('Atualizando status de renovação automática:', isAutoRenew);
            
            autoRenewElement.textContent = isAutoRenew ? 'Ativada' : 'Desativada';
            autoRenewElement.className = isAutoRenew ? 'value auto-renew-status auto-renew-active compact' : 'value auto-renew-status auto-renew-inactive compact';
            
            // Atualizar texto e ícone do botão de renovação automática
            const autoRenewBtn = document.getElementById('updateAutoRenewBtn');
            const autoRenewBtnText = document.getElementById('autoRenewBtnText');
            const autoRenewIcon = document.getElementById('autoRenewIcon');
            
            console.log('Elementos do botão encontrados:', {
                btn: !!autoRenewBtn,
                text: !!autoRenewBtnText,
                icon: !!autoRenewIcon
            });
            
            if (autoRenewBtn && autoRenewBtnText && autoRenewIcon) {
                if (isAutoRenew) {
                    autoRenewBtnText.textContent = 'Desativar Renovação Automática';
                    autoRenewIcon.className = 'fas fa-toggle-off';
                    autoRenewBtn.className = 'btn btn-danger';
                    console.log('Botão configurado para DESATIVAR (auto_renew=true)');
                } else {
                    autoRenewBtnText.textContent = 'Ativar Renovação Automática';
                    autoRenewIcon.className = 'fas fa-toggle-on';
                    autoRenewBtn.className = 'btn btn-success';
                    console.log('Botão configurado para ATIVAR (auto_renew=false)');
                }
            } else {
                console.error('Elementos do botão não encontrados!');
            }
            
            // Aplicar classes compactas aos botões
            const buttons = currentSubDiv.querySelectorAll('.btn');
            buttons.forEach(button => {
                if (!button.classList.contains('compact')) {
                    button.classList.add('compact');
                }
            });
            
        } else {
            // Esconder seção de assinatura atual e mostrar planos
            currentSubDiv.style.display = 'none';
            plansDiv.style.display = 'block';
            noSubDiv.style.display = 'block';
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
                <div class="compact" style="
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    max-width: 450px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                ">
                    <h3 class="compact" style="margin-bottom: 15px; text-align: center; color: #2c3e50; font-size: 1.4rem;">Escolha seu novo plano</h3>
                    <p class="compact" style="text-align: center; color: #6c757d; margin-bottom: 20px; font-size: 0.9rem;">Selecione o plano que deseja para sua renovação:</p>
                    <div style="display: grid; gap: 12px;">`;
        
        Object.entries(this.plans).forEach(([planType, planInfo]) => {
            const isCurrentPlan = this.currentSubscription.plan_type === planType;
            const planLevel = planHierarchy[planType];
            const isDowngrade = planLevel < currentPlanLevel;
            const isDisabled = isDowngrade;
            
            modalHTML += `
                <div class="compact" style="
                    border: 2px solid ${isCurrentPlan ? '#28a745' : (isDisabled ? '#dc3545' : '#e9ecef')};
                    border-radius: 6px;
                    padding: 12px;
                    cursor: ${isDisabled ? 'not-allowed' : 'pointer'};
                    transition: all 0.3s ease;
                    background: ${isCurrentPlan ? '#f8fff9' : (isDisabled ? '#f8d7da' : 'white')};
                    opacity: ${isDisabled ? '0.6' : '1'};
                " ${!isDisabled ? `onclick="subscriptionManager.selectRenewalPlan('${planType}')" onmouseover="this.style.borderColor='#007bff'" onmouseout="this.style.borderColor='${isCurrentPlan ? '#28a745' : '#e9ecef'}'"` : ''}>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong class="compact" style="color: ${isDisabled ? '#721c24' : '#2c3e50'}; font-size: 0.95rem;">${planNames[planType]}</strong>
                            ${isCurrentPlan ? '<span class="compact" style="color: #28a745; font-size: 0.8em; margin-left: 8px;">(Plano Atual)</span>' : ''}
                            ${isDisabled ? '<span class="compact" style="color: #721c24; font-size: 0.8em; margin-left: 8px;">(Não disponível - plano inferior)</span>' : ''}
                            <div class="compact" style="color: ${isDisabled ? '#721c24' : '#6c757d'}; font-size: 0.8em;">${planInfo.duration_months} ${planInfo.duration_months === 1 ? 'mês' : 'meses'}</div>
                        </div>
                        <div class="compact" style="font-size: 1.1em; font-weight: bold; color: ${isDisabled ? '#721c24' : '#007bff'};">
                            R$ ${planInfo.price.toFixed(2)}
                        </div>
                    </div>
                </div>`;
        });
        
        modalHTML += `
                    </div>
                    <div style="text-align: center; margin-top: 20px;">
                        <button class="compact" onclick="subscriptionManager.closePlanModal()" style="
                            background: #6c757d;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 0.9em;
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
        console.log('SubscriptionManager.updateAutoRenew() chamada');
        console.log('currentSubscription:', this.currentSubscription);
        
        if (!this.currentSubscription) {
            console.error('Nenhuma assinatura atual encontrada');
            this.showError('Nenhuma assinatura encontrada');
            return;
        }

        if (this.isProcessing) {
            console.log('Já está processando, ignorando clique');
            return;
        }

        this.isProcessing = true;
        this.showLoading(true);

        try {
            // Alternar o estado atual da renovação automática
            const newAutoRenew = !this.currentSubscription.auto_renew;
            console.log('Alterando auto_renew de', this.currentSubscription.auto_renew, 'para', newAutoRenew);
            
            const response = await fetch('/api/subscriptions/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    auto_renew: newAutoRenew
                })
            });

            const data = await response.json();
            console.log('Resposta da API:', data);

            if (response.ok && data.success) {
                // ATUALIZAÇÃO IMEDIATA E FORÇADA DO STATUS VISUAL
                console.log('=== FORÇANDO ATUALIZAÇÃO VISUAL ===');
                
                // 1. Atualizar o objeto currentSubscription
                this.currentSubscription.auto_renew = newAutoRenew;
                console.log('currentSubscription.auto_renew atualizado para:', this.currentSubscription.auto_renew);
                
                // 2. Atualizar DIRETAMENTE o elemento de status
                const autoRenewElement = document.getElementById('autoRenewStatus');
                if (autoRenewElement) {
                    autoRenewElement.textContent = newAutoRenew ? 'Ativada' : 'Desativada';
                    autoRenewElement.className = newAutoRenew ? 'value auto-renew-status auto-renew-active compact' : 'value auto-renew-status auto-renew-inactive compact';
                    console.log('Status atualizado diretamente:', autoRenewElement.textContent);
                } else {
                    console.error('Elemento autoRenewStatus não encontrado!');
                }
                
                // 3. Atualizar DIRETAMENTE o botão
                const autoRenewBtn = document.getElementById('updateAutoRenewBtn');
                const autoRenewBtnText = document.getElementById('autoRenewBtnText');
                const autoRenewIcon = document.getElementById('autoRenewIcon');
                
                if (autoRenewBtn && autoRenewBtnText && autoRenewIcon) {
                    if (newAutoRenew) {
                        autoRenewBtnText.textContent = 'Desativar Renovação Automática';
                        autoRenewIcon.className = 'fas fa-toggle-off';
                        autoRenewBtn.className = 'btn btn-danger';
                        console.log('Botão atualizado para DESATIVAR');
                    } else {
                        autoRenewBtnText.textContent = 'Ativar Renovação Automática';
                        autoRenewIcon.className = 'fas fa-toggle-on';
                        autoRenewBtn.className = 'btn btn-success';
                        console.log('Botão atualizado para ATIVAR');
                    }
                } else {
                    console.error('Elementos do botão não encontrados!');
                }
                
                // 4. Forçar repaint do DOM
                autoRenewElement.style.display = 'none';
                autoRenewElement.offsetHeight; // Trigger reflow
                autoRenewElement.style.display = '';
                
                const action = newAutoRenew ? 'ativada' : 'desativada';
                this.showSuccess(`Renovação automática ${action} com sucesso`);
                
                console.log('=== ATUALIZAÇÃO VISUAL CONCLUÍDA ===');
                
            } else {
                console.error('Erro na resposta da API:', data);
                this.showError(data.message || 'Erro ao atualizar renovação automática');
            }
        } catch (error) {
            console.error('Erro ao atualizar renovação automática:', error);
            this.showError('Erro ao atualizar renovação automática');
        } finally {
            this.isProcessing = false;
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
            
            // Verificar autenticação antes de prosseguir
            console.log('🔐 Verificando autenticação antes da assinatura...');
            const authCheck = await fetch('/api/me');
            if (authCheck.status === 401) {
                console.log('❌ Usuário não autenticado, redirecionando para login');
                this.showError('Sessão expirada. Redirecionando para login...');
                setTimeout(() => {
                    window.location.href = 'entrar.html';
                }, 2000);
                return;
            }
            
            // Verificar novamente se já tem assinatura antes de criar
            await this.loadCurrentSubscription();
            if (this.currentSubscription) {
                this.showError('Você já possui uma assinatura ativa. Recarregando página...');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
                return;
            }
            
            console.log('📤 Enviando requisição de assinatura...');
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
            
            console.log('📥 Resposta recebida:', response.status);
            
            // Verificar se a resposta é de erro de autenticação
            if (response.status === 401) {
                console.log('❌ Erro de autenticação na resposta');
                this.showError('Sessão expirada. Redirecionando para login...');
                setTimeout(() => {
                    window.location.href = 'entrar.html';
                }, 2000);
                return;
            }
            
            const data = await response.json();
            console.log('📊 Dados da resposta:', data);
            
            if (data.success) {
                this.showSuccess('Assinatura criada com sucesso! Redirecionando para o sistema...');
                
                // Aguardar um pouco mais e verificar se a assinatura foi criada
                setTimeout(async () => {
                    await this.loadCurrentSubscription();
                    if (this.currentSubscription) {
                        window.location.href = '/';
                    } else {
                        // Se não conseguiu carregar, recarregar a página
                        window.location.reload();
                    }
                }, 3000);
            } else {
                // Se o erro for "já possui assinatura", recarregar a página
                if (data.error && data.error.includes('já possui')) {
                    this.showError('Você já possui uma assinatura ativa. Recarregando página...');
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    this.showError(data.error || 'Erro ao processar assinatura');
                    this.enableAllButtons();
                    this.isProcessing = false;
                }
            }
        } catch (error) {
            console.error('Erro ao processar assinatura:', error);
            this.showError('Erro de conexão. Recarregando página...');
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } finally {
            this.showLoading(false);
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
    console.log('updateAutoRenew() chamada');
    console.log('subscriptionManager:', subscriptionManager);
    
    if (!subscriptionManager) {
        console.error('subscriptionManager não está inicializado');
        return;
    }
    
    subscriptionManager.updateAutoRenew();
}

function cancelSubscription() {
    subscriptionManager.cancelSubscription();
}

function goToSystem() {
    window.location.href = 'index.html';
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
    window.location.href = 'historico-assinaturas.html';
}

// Função auxiliar para mostrar alertas de expiração
function showExpiryAlert(type, message) {
    const alertDiv = document.getElementById('expiryAlert');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : 'exclamation-triangle'}"></i>
        <span>${message}</span>
    `;
    alertDiv.style.display = 'block';
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', async function() {
    subscriptionManager = new SubscriptionManager();
    await subscriptionManager.init();
});