// Main Application JavaScript
class App {
    constructor() {
        this.currentPage = 'dashboard';
        this.apiBase = '/api';
        this.currentUser = null;
        this.init();
    }

    async init() {
        await this.loadCurrentUser();
        
        // Verificar status da assinatura antes de carregar a aplicação
        const hasActiveSubscription = await this.checkSubscriptionStatus();
        // Caso não haja assinatura ativa ou a verificação falhe, não redirecionar.
        // Continuar carregando a aplicação normalmente para a tela inicial.
        
        this.setupEventListeners();
        
        // Verificar se há um hash na URL e carregar a página correspondente
        const hash = window.location.hash.substring(1); // Remove o #
        const initialPage = hash || 'dashboard';
        this.loadPage(initialPage);
    }

    async loadCurrentUser() {
        // Não verificar se estiver fazendo logout
        if (window.isLoggingOut) {
            return;
        }
        
        try {
            const response = await fetch('/api/me');
            if (response.ok) {
                this.currentUser = await response.json();
                this.updateUserInfo();
            }
        } catch (error) {
            console.error('Erro ao carregar usuário atual:', error);
        }
    }

    async checkSubscriptionStatus() {
        try {
            const response = await fetch('/api/subscriptions/status');
            if (response.ok) {
                const data = await response.json();
                return data.success && data.has_active_subscription;
            }
            return false;
        } catch (error) {
            console.error('Erro ao verificar status da assinatura:', error);
            return false;
        }
    }


    updateUserInfo() {
        if (this.currentUser) {
            const userInfo = document.getElementById('user-info');
            if (userInfo) {
                userInfo.innerHTML = `
                    <span class="me-2">${this.currentUser.username}</span>
                `;
        return content;
            }
        }
    }




    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                const page = e.target.closest('[data-page]').dataset.page;
                
                e.preventDefault();
                this.loadPage(page);
                this.updateActiveNav(e.target.closest('[data-page]'));

                // Auto-close navbar on small screens after selection
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    try {
                        const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse) || new bootstrap.Collapse(navbarCollapse, { toggle: false });
                        bsCollapse.hide();
                    } catch (err) {
                        // Fallback in case Bootstrap is not available
                        navbarCollapse.classList.remove('show');
                    }
                }
            });
        });

        // Handle browser back/forward
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.loadPage(e.state.page, false);
            }
        });
    }

    updateActiveNav(activeLink) {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Remove active class from all dropdown items (dashboards)
        document.querySelectorAll('.dropdown-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to clicked link
        if (activeLink.classList.contains('dropdown-item')) {
            // Se for um item do dropdown (dashboard), adiciona active apenas nele
            activeLink.classList.add('active');
        } else {
            // Se for um nav-link normal, adiciona active nele
            activeLink.classList.add('active');
        }
    }

    async loadPage(page, pushState = true) {
        // Preservar o slug solicitado (URL em português) e mapear internamente para páginas existentes
        const originalPage = page;
        const pageMap = {
            // Principais seções
            'pacientes': 'patients',
            'agendamentos': 'appointments',
            'pagamentos': 'payments',
            // Dashboards
            'dashboard-pagamentos': 'dashboard-payments',
            'dashboard-sessoes': 'dashboard-sessions'
        };

        const internalPage = pageMap[originalPage] || originalPage;
        this.currentPage = internalPage;
        
        if (pushState) {
            history.pushState({ page: originalPage }, '', `#${originalPage}`);
        }

        this.showLoading();

        try {
            let content = '';
            
            // Usar a página interna para renderização
            switch (internalPage) {
                case 'dashboard':
                    content = await this.loadDashboard();
                    break;
                case 'dashboard-payments':
                    content = await this.loadDashboardPayments();
                    break;
                case 'dashboard-sessions':
                    content = await this.loadDashboardSessions();
                    break;

                case 'patients':
                    content = await this.loadPatients();
                    break;
                case 'appointments':
                    content = await this.loadAppointments();
                    break;
                case 'payments':
                    content = await this.loadPayments();
                    break;
                case 'especialidades':
                    content = await this.loadEspecialidades();
                    break;
                case 'funcionarios':
                    content = await this.loadFuncionarios();
                    break;
                case 'perfil':
                    // Redirecionar para a página de perfil dedicada
                    window.location.href = '/perfil';
                    return;
                default:
                    content = '<div class="alert alert-warning">Página não encontrada</div>';
            }

            // Usar helper seguro para evitar erro quando o container não existir
            this.safeSetHtml('main-content', content);
            
            // Initialize page-specific functionality and await dashboards to finish
            await this.initPageFunctionality(internalPage);
            
        } catch (error) {
            console.error('Error loading page:', error);
            this.showError('Erro ao carregar página');
        } finally {
            this.hideLoading();
        }
    }

    // Helper para definir innerHTML com segurança
    safeSetHtml(elementId, html) {
        const el = document.getElementById(elementId);
        if (!el) {
            console.warn(`[safeSetHtml] Elemento #${elementId} não encontrado`);
            return false;
        }
        el.innerHTML = html;
        return true;
    }

    async initPageFunctionality(page) {
        switch (page) {
            case 'dashboard':
                if (window.Dashboard) {
                    await window.Dashboard.init();
                }
                break;
            case 'dashboard-payments':
                if (window.DashboardPayments) {
                    await window.DashboardPayments.init();
                }
                break;
            case 'dashboard-sessions':
                if (window.DashboardSessions) {
                    await window.DashboardSessions.init();
                }
                break;
            case 'patients':
                if (window.Patients) {
                    window.Patients.init();
                }
                break;
            case 'appointments':
                if (window.Appointments) {
                    window.Appointments.init();
                }
                break;
            case 'payments':
                if (window.Payments) {
                    window.Payments.init();
                }
                break;
            case 'especialidades':
                if (window.Especialidades) {
                    window.Especialidades.init();
                }
                break;
            case 'funcionarios':
                this.initFuncionariosPage();
                break;
        }
    }

    async loadDashboard() {
        return `
            <div class="row">
                <div class="col-12">
                    <h2 class="mb-4">
                        <i class="bi bi-speedometer2 me-2"></i>Dashboard
                    </h2>
                </div>
            </div>
            
            <!-- Stats Cards -->
            <div class="row" id="stats-cards">
                <!-- Stats will be loaded here -->
            </div>
            
            <!-- Charts Row -->
            <div class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Receita Mensal</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="revenueChart" height="100"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Status das Sessões</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="sessionsChart" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Atendimentos de Hoje -->
            <div class="row mt-4">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-calendar-day me-2"></i>
                                Atendimentos de Hoje
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="today-sessions">
                                <!-- Today sessions will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="row mt-4">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Próximas Sessões</h5>
                        </div>
                        <div class="card-body">
                            <div id="upcoming-sessions">
                                <!-- Upcoming sessions will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Pagamentos Recentes</h5>
                        </div>
                        <div class="card-body">
                            <div id="recent-payments">
                                <!-- Recent payments will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal para Criar/Editar Profissional -->
            <div class="modal fade" id="funcionarioModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="modalTitle">Novo Profissional</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="funcionarioForm">
                                <input type="hidden" id="funcionarioId">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="nome" class="form-label">Nome *</label>
                                            <input type="text" class="form-control" id="nome" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="telefone" class="form-label">Telefone</label>
                                            <input type="tel" class="form-control" id="telefone">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="email" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="email">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="especialidade" class="form-label">Especialidade</label>
                                            <select class="form-control" id="especialidade">
                                                <option value="">Selecione uma especialidade</option>
                                                <!-- Opções serão carregadas via JavaScript -->
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="obs" class="form-label">Observações</label>
                                    <textarea class="form-control" id="obs" rows="3"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="saveFuncionario()">Salvar</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal de Confirmação de Exclusão -->
            <div class="modal fade" id="deleteModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title">Confirmar Exclusão</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Tem certeza que deseja excluir este profissional?</p>
                            <p class="text-muted">Esta ação não pode ser desfeita.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-danger" onclick="confirmDelete()">Excluir</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Inicializar funcionalidade após renderizar o conteúdo
        setTimeout(() => {
            this.initFuncionariosPage();
        }, 100);
        
        return content;
    }
    
    async initFuncionariosPage() {
        try {
            // Carregar especialidades para o dropdown
            await this.loadEspecialidadesDropdown();
            // Carregar e renderizar funcionários
            await this.loadAndRenderFuncionarios();
        } catch (error) {
        console.error('Erro ao inicializar página de profissionais:', error);
            this.showError('Erro ao carregar dados dos profissionais');
        }
    }
    
    async loadEspecialidadesDropdown() {
        try {
            const response = await fetch('/api/especialidades');
            if (!response.ok) throw new Error('Erro ao carregar especialidades');
            
            const data = await response.json();
            
            // Verificar se a resposta tem o formato esperado
            let especialidades = [];
            if (data.success && data.especialidades) {
                especialidades = data.especialidades;
            } else if (Array.isArray(data)) {
                // Fallback para formato antigo (array direto)
                especialidades = data;
            }
            
            const select = document.getElementById('especialidade');
            
            if (select) {
                select.innerHTML = '<option value="">Selecione uma especialidade</option>';
                especialidades.forEach(esp => {
                    select.innerHTML += `<option value="${esp.id}">${esp.nome}</option>`;
                });
            }
        } catch (error) {
            console.error('Erro ao carregar especialidades:', error);
        }
    }
    
    async loadAndRenderFuncionarios() {
        try {
            // Mostrar estado de carregamento na tabela
            const tbodyLoading = document.getElementById('funcionariosTableBody');
            if (tbodyLoading) {
                tbodyLoading.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Carregando...</span>
                            </div>
                        </td>
                    </tr>
                `;
            }

            const response = await fetch('/api/funcionarios');
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = 'entrar.html';
                    return;
                }
            throw new Error('Erro ao carregar profissionais');
            }
            
            const data = await response.json();
            
            // Verificar se a resposta tem o formato esperado
            let funcionarios = [];
            if (data.success && data.funcionarios) {
                funcionarios = data.funcionarios;
            } else if (Array.isArray(data)) {
                // Fallback para formato antigo (array direto)
                funcionarios = data;
            }
            
            this.renderFuncionariosTable(funcionarios);
        } catch (error) {
            console.error('Erro ao carregar profissionais:', error);
            this.showError('Erro ao carregar profissionais: ' + error.message);
            const tbodyError = document.getElementById('funcionariosTableBody');
            if (tbodyError) {
                tbodyError.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-danger">
                            Falha ao carregar profissionais
                        </td>
                    </tr>
                `;
            }
        }
    }
    
    renderFuncionariosTable(funcionarios) {
        const tbody = document.getElementById('funcionariosTableBody');
        
        if (!tbody) return;
        
        if (funcionarios.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        <i class="bi bi-person-badge" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                        <p>Nenhum profissional cadastrado</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = funcionarios.map(funcionario => `
            <tr>
                <td>${funcionario.nome}</td>
                <td>${funcionario.telefone || '-'}</td>
                <td>${funcionario.email || '-'}</td>
                <td>${funcionario.especialidade_nome || '-'}</td>
                <td>${funcionario.obs ? (funcionario.obs.length > 50 ? funcionario.obs.substring(0, 50) + '...' : funcionario.obs) : '-'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editFuncionario(${funcionario.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteFuncionario(${funcionario.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Armazenar funcionários globalmente para uso nas funções de edição/exclusão
        window.funcionarios = funcionarios;
    }

    async loadPatients() {
        return `
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2>
                            <i class="bi bi-people me-2"></i>Pacientes
                        </h2>
                        <button class="btn btn-primary" onclick="Patients.showCreateModal()">
                            <i class="bi bi-plus-lg me-1"></i>Novo Paciente
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Search and Filters -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="input-group">
                        <span class="input-group-text">
                            <i class="bi bi-search"></i>
                        </span>
                        <input type="text" class="form-control" id="patient-search" placeholder="Buscar pacientes...">
                    </div>
                </div>
            </div>
            
            <!-- Patients List -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="patients-list">
                                <!-- Patients will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return content;
    }

    async loadAppointments() {
        return `
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2>
                            <i class="bi bi-calendar-check me-2"></i>Agendamentos
                        </h2>
                        <button class="btn btn-primary" onclick="Appointments.showCreateModal()">
                            <i class="bi bi-plus-lg me-1"></i>Novo Agendamento
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Filters -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <select class="form-select" id="appointment-filter">
                        <option value="">Todos os agendamentos</option>
                        <option value="upcoming">Próximos</option>
                        <option value="completed">Concluídos</option>
                        <option value="cancelled">Cancelados</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <select class="form-select" id="patient-filter">
                        <option value="">Todos os pacientes</option>
                        <!-- Patients will be loaded here -->
                    </select>
                </div>
            </div>
            
            <!-- Appointments List -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="appointments-list">
                                <!-- Appointments will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal de Transferência de Agendamentos -->
            <!-- Modal de Transferência de Agendamentos -->
            <div class="modal fade" id="transferModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">Profissional possui agendamentos</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning">
                                <i class="bi bi-exclamation-triangle"></i>
                                <strong>Atenção!</strong> O profissional <span id="funcionarioNomeTransfer"></span> possui agendamentos ativos.
                            </div>
                            
                            <div class="mb-3">
                                <h6>Agendamentos encontrados:</h6>
                                <div id="agendamentosList" class="list-group mb-3">
                                    <!-- Lista de agendamentos será preenchida via JavaScript -->
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="novoFuncionario" class="form-label">Transferir agendamentos para:</label>
                                <select class="form-control" id="novoFuncionario">
                                    <option value="">Selecione um profissional</option>
                                    <!-- Opções serão carregadas via JavaScript -->
                                </select>
                            </div>
                            
                            <p class="text-muted">
                                <i class="bi bi-info-circle"></i>
                                Todos os agendamentos serão transferidos para o profissional selecionado e o profissional atual será excluído.
                            </p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-warning" onclick="confirmTransferAndDelete()">Transferir e Excluir</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return content;
    }

    async loadPayments() {
        return `
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2>
                            <i class="bi bi-credit-card me-2"></i>Pagamentos
                        </h2>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-primary" onclick="Payments.showFechamentoCaixa()">
                                <i class="bi bi-calculator me-1"></i>Fechamento de Caixa
                            </button>
                            <button class="btn btn-primary" onclick="Payments.showCreateModal()">
                                <i class="bi bi-plus-lg me-1"></i>Registrar Pagamento
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Filters -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <input type="date" class="form-control" id="date-from" placeholder="Data inicial">
                </div>
                <div class="col-md-3">
                    <input type="date" class="form-control" id="date-to" placeholder="Data final">
                </div>
                <div class="col-md-4">
                    <select class="form-select" id="payment-patient-filter">
                        <option value="">Todos os pacientes</option>
                        <!-- Patients will be loaded here -->
                    </select>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-outline-primary w-100" onclick="Payments.applyFilters()">
                        <i class="bi bi-funnel me-1"></i>Filtrar
                    </button>
                </div>
            </div>
            
            <!-- Payments List -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="payments-list">
                                <!-- Payments will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return content;
    }

    // API Helper Methods
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Incluir cookies de sessão
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // UI Helper Methods
    showLoading() {
        document.getElementById('loading-spinner').classList.remove('d-none');
    }

    hideLoading() {
        document.getElementById('loading-spinner').classList.add('d-none');
    }

    showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        const toastId = 'toast-' + Date.now();
        
        const toastHtml = `
            <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} text-${type} me-2"></i>
                    <strong class="me-auto">${type === 'success' ? 'Sucesso' : 'Erro'}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    showError(message) {
        this.showToast(message, 'danger');
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatCurrency(value) {
        if (value === null || value === undefined) return 'R$ 0,00';
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    formatCPF(cpf) {
        if (!cpf) return '';
        return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }

    formatPhone(phone) {
        if (!phone) return '';
        return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }

    async loadDashboardPayments() {
        return `
            <div class="row">
                <div class="col-12">
                    <h2 class="mb-4">
                        <i class="bi bi-credit-card me-2"></i>Dashboard de Pagamentos
                    </h2>
                </div>
            </div>
            
            <!-- Filtros de Data -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="row align-items-end">
                                <div class="col-md-3">
                                    <label for="payments-date-from" class="form-label">Data Inicial</label>
                                    <input type="date" class="form-control" id="payments-date-from">
                                </div>
                                <div class="col-md-3">
                                    <label for="payments-date-to" class="form-label">Data Final</label>
                                    <input type="date" class="form-control" id="payments-date-to">
                                </div>
                                <div class="col-md-3">
                                    <button class="btn btn-primary" id="payments-filter-btn">
                                        <i class="bi bi-funnel me-1"></i>Filtrar
                                    </button>
                                    <button class="btn btn-outline-secondary ms-2" id="payments-clear-btn">
                                        <i class="bi bi-x-circle me-1"></i>Limpar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Cards de Estatísticas -->
            <div class="row mb-4">
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h6 class="card-title">Total Recebido</h6>
                                    <h3 class="mb-0" id="total-recebido">R$ 0,00</h3>
                                </div>
                                <div class="align-self-center">
                                    <i class="bi bi-cash-coin fs-1"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h6 class="card-title">Total a Receber</h6>
                                    <h3 class="mb-0" id="total-receber">R$ 0,00</h3>
                                </div>
                                <div class="align-self-center">
                                    <i class="bi bi-hourglass-split fs-1"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h6 class="card-title">Total de Pagamentos</h6>
                                    <h3 class="mb-0" id="total-pagamentos">0</h3>
                                </div>
                                <div class="align-self-center">
                                    <i class="bi bi-receipt fs-1"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="card bg-danger text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h6 class="card-title">Sessões Pendentes</h6>
                                    <h3 class="mb-0" id="sessoes-pendentes">0</h3>
                                </div>
                                <div class="align-self-center">
                                    <i class="bi bi-exclamation-triangle fs-1"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modalidade com Maior Volume -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-trophy me-2"></i>Modalidade com Maior Volume
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="modalidade-maior-volume">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Quebra por Modalidade -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-pie-chart me-2"></i>Pagamentos por Modalidade
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row" id="modalidades-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Pagamentos Recentes e Sessões Pendentes -->
            <div class="row">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-clock-history me-2"></i>Pagamentos Recentes
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="recent-payments-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-calendar-x me-2"></i>Sessões Pendentes de Pagamento
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="pending-sessions-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return content;
    }

    async loadDashboardSessions() {
        return `
            <div class="row">
                <div class="col-12">
                    <h2 class="mb-4">
                        <i class="bi bi-calendar-check me-2"></i>Dashboard de Sessões
                    </h2>
                </div>
            </div>
            
            <!-- Filtros de Data -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="row align-items-end">
                                <div class="col-md-2">
                                    <label for="sessions-date-from" class="form-label">Data Inicial</label>
                                    <input type="date" class="form-control" id="sessions-date-from">
                                </div>
                                <div class="col-md-2">
                                    <label for="sessions-date-to" class="form-label">Data Final</label>
                                    <input type="date" class="form-control" id="sessions-date-to">
                                </div>

                                <div class="col-md-3">
                                    <button class="btn btn-primary" id="sessions-filter-btn">
                                        <i class="bi bi-funnel me-1"></i>Filtrar
                                    </button>
                                    <button class="btn btn-outline-secondary ms-2" id="sessions-clear-btn">
                                        <i class="bi bi-x-circle me-1"></i>Limpar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Cards de Estatísticas -->
            <div class="row mb-4">
                <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-calendar-check fs-1"></i>
                            <h3 class="mt-2 mb-0" id="total-sessoes">0</h3>
                            <small>Total de Sessões</small>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-check-circle fs-1"></i>
                            <h3 class="mt-2 mb-0" id="sessoes-realizadas">0</h3>
                            <small>Realizadas</small>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-calendar-event fs-1"></i>
                            <h3 class="mt-2 mb-0" id="sessoes-agendadas">0</h3>
                            <small>Agendadas</small>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-arrow-repeat fs-1"></i>
                            <h3 class="mt-2 mb-0" id="sessoes-reagendadas">0</h3>
                            <small>Reagendadas</small>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
                    <div class="card bg-danger text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-person-x fs-1"></i>
                            <h3 class="mt-2 mb-0" id="sessoes-faltou">0</h3>
                            <small>Faltas</small>
                        </div>
                    </div>
                </div>
                <div class="col-lg-2 col-md-4 col-sm-6 mb-3">
                    <div class="card bg-secondary text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-x-circle fs-1"></i>
                            <h3 class="mt-2 mb-0" id="sessoes-canceladas">0</h3>
                            <small>Canceladas</small>
                        </div>
                    </div>
                </div>
            </div>
            

            
            <!-- Listas Detalhadas -->
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-arrow-repeat me-2"></i>Sessões Reagendadas
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="rescheduled-sessions-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-person-x me-2"></i>Pacientes com Faltas
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="missed-sessions-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-calendar-day me-2"></i>Sessões de Hoje
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="today-sessions-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-calendar-week me-2"></i>Próximas Sessões
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="upcoming-sessions-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Pacientes por Profissional -->
            <div class="row mb-4">
                <div class="col-12">
                    <h3 class="mb-3">
                        <i class="bi bi-people-fill me-2"></i>Pacientes por Profissional
                    </h3>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-person-lines-fill me-2"></i>Detalhamento de Pacientes por Profissional
                                </h5>
                                <div class="col-md-4">
                                    <label for="patients-psychologist-filter" class="form-label">Filtrar por Profissional</label>
                                    <select class="form-select" id="patients-psychologist-filter">
                                        <option value="">Todos os profissionais</option>
                                        <!-- Será preenchido via JavaScript -->
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="patients-by-psychologist-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Seção de Pacientes -->
            <div class="row mb-4">
                <div class="col-12">
                    <h3 class="mb-3">
                        <i class="bi bi-people me-2"></i>Meus Pacientes
                    </h3>
                </div>
            </div>
            
            <!-- Cards de Estatísticas de Pacientes -->
            <div class="row mb-4">
                <div class="col-lg-4 col-md-6 mb-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-people fs-1"></i>
                            <h3 class="mt-2 mb-0" id="total-pacientes">0</h3>
                            <small>Total de Pacientes</small>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6 mb-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-person-check fs-1"></i>
                            <h3 class="mt-2 mb-0" id="pacientes-ativos">0</h3>
                            <small>Pacientes Ativos (30 dias)</small>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 col-md-6 mb-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="bi bi-calendar-day fs-1"></i>
                            <h3 class="mt-2 mb-0" id="pacientes-hoje">0</h3>
                            <small>Pacientes Hoje</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Atendimentos por Profissional -->
            <div class="row mb-4">
                <div class="col-12">
                    <h3 class="mb-3">
                        <i class="bi bi-person-badge me-2"></i>Atendimentos por Profissional
                    </h3>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-bar-chart me-2"></i>Estatísticas por Profissional
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="psychologists-stats-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Agenda dos Próximos 10 Dias por Profissional -->
            <div class="row mb-4">
                <div class="col-12">
                    <h3 class="mb-3">
                        <i class="bi bi-calendar-week me-2"></i>Agenda dos Próximos 10 Dias por Profissional
                    </h3>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-calendar-check me-2"></i>Sessões Agendadas por Profissional
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="upcoming-sessions-by-psychologist-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Lista de Pacientes -->
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-list-ul me-2"></i>Lista de Pacientes e Atendimentos
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="patients-list-container">
                                <!-- Será preenchido via JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return content;
    }

    async loadEspecialidades() {
        return `
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2>
                            <i class="bi bi-tags me-2"></i>Especialidades
                        </h2>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#especialidadeModal">
                            <i class="bi bi-plus-lg me-1"></i>Nova Especialidade
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Search and Filters -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="input-group">
                        <span class="input-group-text">
                            <i class="bi bi-search"></i>
                        </span>
                        <input type="text" class="form-control" id="especialidade-search" placeholder="Buscar especialidades...">
                    </div>
                </div>
            </div>
            
            <!-- Especialidades List -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Nome Especialidades</th>
                                            <th>Descrição</th>
                                            <th>Criado em</th>
                                            <th>Ações</th>
                                        </tr>
                                    </thead>
                                    <tbody id="especialidadesTableBody">
                                        <!-- Especialidades will be loaded here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal para Criar/Editar Especialidade -->
            <div class="modal fade" id="especialidadeModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="modalTitle">Nova Especialidade</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="especialidadeForm">
                                <input type="hidden" id="especialidadeId">
                                <div class="mb-3">
                                    <label for="nome" class="form-label">Nome *</label>
                                    <input type="text" class="form-control" id="nome" placeholder="Ex: Psicologia Clínica, Terapia Cognitiva, Neuropsicologia..." required>
                                </div>
                                <div class="mb-3">
                                    <label for="descricao" class="form-label">Descrição</label>
                                    <textarea class="form-control" id="descricao" rows="3"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="saveEspecialidade()">Salvar</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal de Confirmação de Exclusão -->
            <div class="modal fade" id="deleteModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title">Confirmar Exclusão</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Tem certeza que deseja excluir esta especialidade?</p>
                            <p class="text-muted">Esta ação não pode ser desfeita.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-danger" onclick="confirmDelete()">Excluir</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return content;
    }

    async loadFuncionarios() {
        const content = `
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h2>
                            <i class="bi bi-person-badge me-2"></i>Profissionais
                        </h2>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#funcionarioModal">
                            <i class="bi bi-plus-lg me-1"></i>Novo Profissional
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Search and Filters -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="input-group">
                        <span class="input-group-text">
                            <i class="bi bi-search"></i>
                        </span>
                        <input type="text" class="form-control" id="funcionario-search" placeholder="Buscar profissionais...">
                    </div>
                </div>
            </div>
            
            <!-- Funcionarios List -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Nome</th>
                                            <th>Telefone</th>
                                            <th>Email</th>
                                            <th>Especialidade</th>
                                            <th>Observações</th>
                                            <th>Ações</th>
                                        </tr>
                                    </thead>
                                    <tbody id="funcionariosTableBody">
                                        <!-- Funcionarios will be loaded here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal para Criar/Editar Profissional -->
            <div class="modal fade" id="funcionarioModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="modalTitle">Novo Profissional</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="funcionarioForm">
                                <input type="hidden" id="funcionarioId">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="nome" class="form-label">Nome *</label>
                                            <input type="text" class="form-control" id="nome" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="telefone" class="form-label">Telefone</label>
                                            <input type="tel" class="form-control" id="telefone">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="email" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="email">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="especialidade" class="form-label">Especialidade</label>
                                            <select class="form-control" id="especialidade">
                                                <option value="">Selecione uma especialidade</option>
                                                <!-- Opções serão carregadas via JavaScript -->
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="obs" class="form-label">Observações</label>
                                    <textarea class="form-control" id="obs" rows="3"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="saveFuncionario()">Salvar</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal de Confirmação de Exclusão -->
            <div class="modal fade" id="deleteModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title">Confirmar Exclusão</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Tem certeza que deseja excluir este profissional?</p>
                            <p class="text-muted">Esta ação não pode ser desfeita.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-danger" onclick="confirmDelete()">Excluir</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return content;
    }

    showLoading() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.classList.remove('d-none');
        }
    }

    hideLoading() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.classList.add('d-none');
        }
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'success' ? 'bg-success' : 
                       type === 'error' ? 'bg-danger' : 
                       type === 'warning' ? 'bg-warning' : 'bg-info';

        const toastHTML = `
            <div class="toast ${bgClass} text-white" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header ${bgClass} text-white">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : 
                                     type === 'error' ? 'exclamation-triangle' : 
                                     type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                    <strong class="me-auto">${type === 'success' ? 'Sucesso' : 
                                              type === 'error' ? 'Erro' : 
                                              type === 'warning' ? 'Aviso' : 'Informação'}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

}

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    window.app = new App();
});

// Funções globais para profissionais
function editFuncionario(id) {
    const funcionario = window.funcionarios?.find(f => f.id === id);
    
    if (!funcionario) {
        window.app.showError('Profissional não encontrado');
        return;
    }
    
    // Preencher formulário
    document.getElementById('funcionarioId').value = funcionario.id;
    document.getElementById('nome').value = funcionario.nome;
    document.getElementById('telefone').value = funcionario.telefone || '';
    document.getElementById('email').value = funcionario.email || '';
    document.getElementById('especialidade').value = funcionario.especialidade_id || '';
    document.getElementById('obs').value = funcionario.obs || '';
    document.getElementById('modalTitle').textContent = 'Editar Profissional';
    
    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById('funcionarioModal'));
    modal.show();
}

function deleteFuncionario(id) {
    console.log('deleteFuncionario chamada do app.js para ID:', id);
    
    const funcionario = window.funcionarios?.find(f => f.id === id);
    
    if (!funcionario) {
        window.app.showError('Profissional não encontrado');
        return;
    }
    
    const nomeFuncionario = funcionario.nome || 'profissional selecionado';
    
    // Criar popup de confirmação jQuery
    const popupHtml = `
        <div id="deleteConfirmPopup" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 15px;
                max-width: 400px;
                width: 90%;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            ">
                <div style="
                    color: #dc3545;
                    font-size: 3em;
                    margin-bottom: 15px;
                ">⚠️</div>
                <h4 style="margin-bottom: 15px; color: #333;">Confirmar Exclusão</h4>
                <p style="margin-bottom: 25px; color: #666;">
                    Tem certeza que deseja excluir o profissional <strong>${nomeFuncionario}</strong>?
                    <br><small>Esta ação não pode ser desfeita.</small>
                </p>
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button id="cancelDelete" style="
                        background: #6c757d;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 14px;
                    ">Cancelar</button>
                    <button id="confirmDelete" style="
                        background: #dc3545;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 14px;
                    ">Excluir</button>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(popupHtml);
    
    // Configurar eventos dos botões
    $('#cancelDelete').click(function() {
        $('#deleteConfirmPopup').remove();
    });
    
    $('#confirmDelete').click(function() {
        $('#deleteConfirmPopup').remove();
        executeDeleteFromApp(id);
    });
    
    // Fechar popup ao clicar fora
    $('#deleteConfirmPopup').click(function(e) {
        if (e.target.id === 'deleteConfirmPopup') {
            $(this).remove();
        }
    });
    
    console.log('Popup de confirmação criado para profissional:', nomeFuncionario);
}

async function saveFuncionario() {
    const form = document.getElementById('funcionarioForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const funcionarioId = document.getElementById('funcionarioId').value;
    const especialidadeId = document.getElementById('especialidade').value;
    
    const data = {
        nome: document.getElementById('nome').value.trim(),
        telefone: document.getElementById('telefone').value.trim(),
        email: document.getElementById('email').value.trim(),
        especialidade_id: especialidadeId ? parseInt(especialidadeId) : null,
        obs: document.getElementById('obs').value.trim()
    };
    
    try {
        const url = funcionarioId ? `/api/funcionarios/${funcionarioId}` : '/api/funcionarios';
        const method = funcionarioId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao salvar profissional');
        }
        
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('funcionarioModal'));
        modal.hide();
        
        // Recarregar lista
        await window.app.loadAndRenderFuncionarios();
        
        window.app.showToast(
            funcionarioId ? 'Profissional atualizado com sucesso!' : 'Profissional criado com sucesso!',
            'success'
        );
        
        // Resetar formulário
        form.reset();
        document.getElementById('funcionarioId').value = '';
        document.getElementById('modalTitle').textContent = 'Novo Profissional';
    } catch (error) {
        console.error('Erro:', error);
        window.app.showError('Erro ao salvar profissional: ' + error.message);
    }
}

// Função executeDeleteFromApp para profissionais (chamada pelo popup jQuery)
function executeDeleteFromApp(funcionarioId) {
    console.log('executeDeleteFromApp chamada para profissional ID:', funcionarioId);
    
    // Mostrar loading
    const loadingPopup = `
        <div id="loadingPopup" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
            ">
                <div style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #dc3545;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 15px;
                "></div>
                <p>Excluindo profissional...</p>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    
    $('body').append(loadingPopup);
    
    // Fazer requisição DELETE usando jQuery
    $.ajax({
        url: `/api/funcionarios/${funcionarioId}`,
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        success: function(data, textStatus, xhr) {
            $('#loadingPopup').remove();
            console.log('Profissional excluído com sucesso:', data);
            
            // Mostrar popup de sucesso
            showSuccessPopupApp('✅ Profissional excluído com sucesso!');
            
            // Recarregar lista após um breve delay
            setTimeout(() => {
                if (window.app && window.app.loadAndRenderFuncionarios) {
                    window.app.loadAndRenderFuncionarios();
                } else if (window.loadFuncionarios) {
                    window.loadFuncionarios();
                }
            }, 1000);
        },
        error: function(xhr, textStatus, errorThrown) {
            $('#loadingPopup').remove();
            console.log('Erro ao excluir profissional - Status:', xhr.status);
            console.log('Resposta do servidor:', xhr.responseText);
            
            let errorMessage = 'Erro ao excluir profissional';
            
            if (xhr.status === 409) {
                // Profissional possui agendamentos - mostrar mensagem clara
                errorMessage = 'Este profissional possui agendamentos ativos e não pode ser excluído. Para excluir este profissional, primeiro transfira ou cancele todos os agendamentos associados a ele.';
            } else if (xhr.responseText) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.message || response.error || errorMessage;
                } catch (e) {
                    // Manter mensagem padrão
                }
            }
            
            showErrorPopupApp('❌ ' + errorMessage);
        }
    });
}

// Funções auxiliares para popups de feedback no app.js
function showSuccessPopupApp(message) {
    const successPopup = `
        <div id="successPopupApp" style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10001;
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2em;">${message}</span>
                <button onclick="$('#successPopupApp').remove()" style="
                    background: none;
                    border: none;
                    color: #155724;
                    font-size: 1.2em;
                    cursor: pointer;
                    margin-left: auto;
                ">×</button>
            </div>
        </div>
        <style>
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        </style>
    `;
    
    $('body').append(successPopup);
    
    // Auto-remover após 3 segundos
    setTimeout(() => {
        $('#successPopupApp').fadeOut(300, function() {
            $(this).remove();
        });
    }, 3000);
}

function showErrorPopupApp(message) {
    const errorPopup = `
        <div id="errorPopupApp" style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10001;
            max-width: 350px;
            animation: slideIn 0.3s ease-out;
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.1em;">${message}</span>
                <button onclick="$('#errorPopupApp').remove()" style="
                    background: none;
                    border: none;
                    color: #721c24;
                    font-size: 1.2em;
                    cursor: pointer;
                    margin-left: auto;
                ">×</button>
            </div>
        </div>
        <style>
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        </style>
    `;
    
    $('body').append(errorPopup);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        $('#errorPopupApp').fadeOut(300, function() {
            $(this).remove();
        });
    }, 5000);
}

// Manter função confirmDelete para compatibilidade (mas não será mais usada)
window.confirmDelete = async function confirmDelete() {
    console.log('confirmDelete (legacy) chamada - redirecionando para nova implementação');
    // Esta função não será mais usada, mas mantida para compatibilidade
}

async function showTransferModal(data) {
    try {
        // Aguardar um pouco para garantir que o DOM esteja completamente carregado
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Verificar se o elemento existe antes de tentar definir o textContent
        let funcionarioNomeElement = document.getElementById('funcionarioNomeTransfer');
        let attempts = 0;
        const maxAttempts = 5;
        
        while (!funcionarioNomeElement && attempts < maxAttempts) {
            console.log(`Tentativa ${attempts + 1} de encontrar funcionarioNomeTransfer`);
            await new Promise(resolve => setTimeout(resolve, 200));
            funcionarioNomeElement = document.getElementById('funcionarioNomeTransfer');
            attempts++;
        }
        
        if (!funcionarioNomeElement) {
            console.error('Elemento funcionarioNomeTransfer não encontrado no DOM após múltiplas tentativas');
            throw new Error('Modal de transferência não está disponível no DOM');
        }
        
        funcionarioNomeElement.textContent = data.funcionario_nome;
        
        // Preencher lista de agendamentos
        const agendamentosList = document.getElementById('agendamentosList');
        if (!agendamentosList) {
            throw new Error('Elemento agendamentosList não encontrado no DOM');
        }
        agendamentosList.innerHTML = '';
        
        data.appointments.forEach(agendamento => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>Paciente ID:</strong> ${agendamento.patient_id}<br>
                        <strong>Data:</strong> ${new Date(agendamento.data_primeira_sessao).toLocaleDateString('pt-BR')}<br>
                        <strong>Sessões:</strong> ${agendamento.quantidade_sessoes}
                    </div>
                    <span class="badge bg-primary">${agendamento.id}</span>
                </div>
            `;
            agendamentosList.appendChild(item);
        });
        
// Carregar lista de profissionais disponíveis
        await loadFuncionariosForTransfer();
        
        // Armazenar dados para transferência
        window.transferData = data;
        
        // Mostrar modal
        const transferModalElement = document.getElementById('transferModal');
        if (!transferModalElement) {
            throw new Error('Modal transferModal não encontrado no DOM');
        }
        const transferModal = new bootstrap.Modal(transferModalElement);
        transferModal.show();
        
    } catch (error) {
        console.error('Erro ao mostrar modal de transferência:', error);
        window.app.showError('Erro ao carregar dados de transferência');
    }
}

async function loadFuncionariosForTransfer() {
    try {
        const response = await fetch('/api/funcionarios');
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        const data = await response.json();
        
        // Verificar se a resposta tem o formato esperado
        let funcionarios = [];
        if (data.success && data.funcionarios) {
            funcionarios = data.funcionarios;
        } else if (Array.isArray(data)) {
            // Fallback para formato antigo (array direto)
            funcionarios = data;
        }
        
        const select = document.getElementById('novoFuncionario');
        if (!select) {
            throw new Error('Elemento novoFuncionario não encontrado no DOM');
        }
    select.innerHTML = '<option value="">Selecione um profissional</option>';
        
        funcionarios.forEach(funcionario => {
            // Não incluir o funcionário que está sendo excluído
            if (funcionario.id !== window.funcionarioToDelete) {
                const option = document.createElement('option');
                option.value = funcionario.id;
                option.textContent = `${funcionario.nome} - ${funcionario.especialidade_nome || 'Sem especialidade'}`;
                select.appendChild(option);
            }
        });
        
    } catch (error) {
        console.error('Erro ao carregar profissionais:', error);
        window.app.showError('Erro ao carregar lista de profissionais');
    }
}

async function confirmTransferAndDelete() {
    const novoFuncionarioId = document.getElementById('novoFuncionario').value;
    
    if (!novoFuncionarioId) {
        window.app.showError('Por favor, selecione um profissional para transferir os agendamentos');
        return;
    }
    
    try {
        const response = await fetch(`/api/funcionarios/${window.funcionarioToDelete}/transfer-appointments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                novo_funcionario_id: parseInt(novoFuncionarioId)
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao transferir agendamentos');
        }
        
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('transferModal'));
        modal.hide();
        
        // Recarregar lista
        await window.app.loadAndRenderFuncionarios();
        
        window.app.showToast(result.message, 'success');
        
        // Limpar variáveis
        window.funcionarioToDelete = null;
        window.transferData = null;
        
    } catch (error) {
        console.error('Erro:', error);
        window.app.showError('Erro ao transferir agendamentos: ' + error.message);
    }
}

// Função de logout
// Flag global para prevenir verificações automáticas durante logout
window.isLoggingOut = false;

function logout() {
    console.log('Função logout chamada'); // Debug
    
    // Prevenir verificações automáticas durante o logout
    window.isLoggingOut = true;
    
    // Confirmar se o usuário realmente quer sair
    const confirmResult = confirm('Tem certeza que deseja sair do sistema?');
    console.log('Resultado da confirmação:', confirmResult); // Debug
    
    if (confirmResult) {
        console.log('Usuário confirmou logout'); // Debug
        // Fazer requisição para a API de logout
        fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            console.log('Resposta da API de logout:', response); // Debug
            // Limpar dados de sessão locais
            localStorage.clear();
            sessionStorage.clear();
            
            // Redirecionar para a tela de login
            window.location.href = 'entrar.html';
        }).catch(error => {
            console.error('Erro no logout:', error);
            // Mesmo se der erro, limpar dados locais e redirecionar
            localStorage.clear();
            sessionStorage.clear();
            window.location.href = 'entrar.html';
        });
    } else {
        console.log('Usuário cancelou logout'); // Debug
        // Resetar flag se cancelou
        window.isLoggingOut = false;
    }
}

    // Função para configurar campos de data em português
    function configurarCamposDataPortugues() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.setAttribute('lang', 'pt-BR');
        });
    }


// Função global para configurar idioma português em campos de data
function configurarDateInputsPortugues() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.setAttribute('lang', 'pt-BR');
        input.setAttribute('locale', 'pt-BR');
    });
}

// Configurar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Definir idioma da página
    document.documentElement.lang = 'pt-BR';
    configurarDateInputsPortugues();
});

// Configurar quando novos elementos forem adicionados dinamicamente
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    const dateInputs = node.querySelectorAll ? node.querySelectorAll('input[type="date"]') : [];
                    dateInputs.forEach(input => {
                        input.setAttribute('lang', 'pt-BR');
                        input.setAttribute('locale', 'pt-BR');
                    });
                }
            });
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});


// Removido: verificação desnecessária de localStorage que causava loop
// A autenticação é gerenciada pelo backend via sessões

