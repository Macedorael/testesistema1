// Dashboard Sessions JavaScript
window.DashboardSessions = {
    initialized: false,
    currentData: {
        stats: {},
        rescheduled: [],
        missed: [],
        todaySessions: [],
        upcomingSessions: [],
        patientsStats: {},
        patientsList: [],
        psychologistsStats: [],
        psychologistsList: []
    },

    init() {
        // Verificar se não estamos no processo de logout
        if (window.isLoggingOut) {
            console.log('[DEBUG] DashboardSessions.init() cancelado - logout em progresso');
            return;
        }
        
        console.log('[DEBUG] DashboardSessions.init() iniciado');
        if (!this.initialized) {
            this.setupEventListeners();
            this.initialized = true;
        }
        this.loadDashboard();
    },

    setupEventListeners() {
        // Filtros de data
        const dateFromInput = document.getElementById('sessions-date-from');
        const dateToInput = document.getElementById('sessions-date-to');
        const psychologistFilter = document.getElementById('patients-psychologist-filter');
        const filterBtn = document.getElementById('sessions-filter-btn');
        const clearBtn = document.getElementById('sessions-clear-btn');

        if (filterBtn) {
            filterBtn.addEventListener('click', () => {
                this.loadDashboard();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (dateFromInput) dateFromInput.value = '';
                if (dateToInput) dateToInput.value = '';
                if (psychologistFilter) psychologistFilter.value = '';
                this.loadDashboard();
            });
        }

        if (psychologistFilter) {
            psychologistFilter.addEventListener('change', () => {
    // Recarregar apenas a seção de pacientes por profissional
                this.loadPatientsByPsychologist();
            });
        }

        // Refresh automático a cada 5 minutos
        setInterval(() => {
            this.loadDashboard();
        }, 300000);
    },

    async loadDashboard() {
        try {
    // Carregar lista de profissionais primeiro
            await this.loadPsychologistsList();
            
            await Promise.all([
                this.loadStats(),
                this.loadRescheduledSessions(),
                this.loadMissedSessions(),
                this.loadTodaySessions(),
                this.loadUpcomingSessions(),
                this.loadPatientsStats(),
                this.loadPatientsList(),
                this.loadPsychologistsStats(),
                this.loadUpcomingSessionsByPsychologist(),
                this.loadPatientsByPsychologist()
            ]);
        } catch (error) {
            console.error('Erro ao carregar dashboard de sessões:', error);
            this.showError('Erro ao carregar dados do dashboard');
        }
    },

    async loadStats() {
        try {
            const params = this.getDateFilters();
            const response = await fetch(`/api/dashboard/sessions/stats?${params}`);
            const result = await response.json();

            if (result.success) {
                this.currentData.stats = result.data;
                this.renderStats();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
            throw error;
        }
    },

    async loadRescheduledSessions() {
        try {
            const params = this.getDateFilters();
            const response = await fetch(`/api/dashboard/sessions/rescheduled?${params}&limit=10`);
            const result = await response.json();

            if (result.success) {
                this.currentData.rescheduled = result.data;
                this.renderRescheduledSessions();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar sessões reagendadas:', error);
            throw error;
        }
    },

    async loadMissedSessions() {
        try {
            const params = this.getDateFilters();
            const response = await fetch(`/api/dashboard/sessions/missed?${params}&limit=10`);
            const result = await response.json();

            if (result.success) {
                this.currentData.missed = result.data;
                this.renderMissedSessions();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar sessões com falta:', error);
            throw error;
        }
    },

    async loadTodaySessions() {
        try {
            console.log('[DEBUG] Carregando sessões de hoje...');
            const response = await fetch('/api/dashboard/sessions/today');
            const result = await response.json();

            console.log('[DEBUG] Resposta da API:', result);

            if (result.success) {
                this.currentData.todaySessions = result.data;
                console.log('[DEBUG] Sessões carregadas:', this.currentData.todaySessions);
                
                // Log detalhado de cada sessão
                this.currentData.todaySessions.forEach((session, index) => {
                    console.log(`[DEBUG] Sessão ${index + 1}:`, {
                        id: session.id,
                        patient_name: session.patient_name,
                        funcionario_nome: session.funcionario_nome,
                        especialidade_nome: session.especialidade_nome,
                        funcionario_especialidade: session.funcionario_especialidade,
                        funcionario_id: session.funcionario_id
                    });
                });
                
                this.renderTodaySessions();
            } else {
                console.error('[ERROR] Erro na API:', result.message);
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('[ERROR] Erro ao carregar sessões de hoje:', error);
            throw error;
        }
    },

    async loadUpcomingSessions() {
        try {
            const response = await fetch('/api/dashboard/sessions/upcoming?limit=10');
            const result = await response.json();

            if (result.success) {
                this.currentData.upcomingSessions = result.data;
                this.renderUpcomingSessions();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar próximas sessões:', error);
            throw error;
        }
    },

    getDateFilters() {
        const dateFrom = document.getElementById('sessions-date-from')?.value;
        const dateTo = document.getElementById('sessions-date-to')?.value;
        
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        
        return params.toString();
    },

    getPsychologistFilters() {
        const dateFrom = document.getElementById('sessions-date-from')?.value;
        const dateTo = document.getElementById('sessions-date-to')?.value;
        const psychologistId = document.getElementById('patients-psychologist-filter')?.value;
        
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        if (psychologistId) params.append('psychologist_id', psychologistId);
        
        return params.toString();
    },

    async loadPsychologistsList() {
        try {
            const response = await fetch('/api/dashboard/psychologists/list');
            const data = await response.json();
            
            if (data.success) {
                this.currentData.psychologistsList = data.data;
                this.renderPsychologistsList();
// Verificar se há profissionais e controlar visibilidade das seções
                this.togglePsychologistSections();
            }
        } catch (error) {
            console.error('Erro ao carregar lista de profissionais:', error);
        }
    },

    togglePsychologistSections() {
        const hasPsychologists = this.currentData.psychologistsList && this.currentData.psychologistsList.length > 0;
        
// Seções que devem ser ocultadas quando não há profissionais
        const sectionsToToggle = [];
        
        // Encontrar seções por texto do título
        const allH3 = document.querySelectorAll('h3');
        allH3.forEach(h3 => {
            const text = h3.textContent.trim();
            if (text.includes('Atendimentos por Profissional') || 
                text.includes('Agenda dos Próximos 10 Dias por Profissional') || 
                text.includes('Pacientes por Profissional')) {
                // Pegar o elemento pai que contém toda a seção (row)
                sectionsToToggle.push(h3.closest('.row'));
            }
        });
        
        // Adicionar cards específicos
        const psychologistsStatsCard = document.getElementById('psychologists-stats-container')?.closest('.card')?.closest('.row');
        const upcomingSessionsCard = document.getElementById('upcoming-sessions-by-psychologist-container')?.closest('.card')?.closest('.row');
        const patientsByPsychologistCard = document.getElementById('patients-by-psychologist-container')?.closest('.card')?.closest('.row');
        
        if (psychologistsStatsCard) sectionsToToggle.push(psychologistsStatsCard);
        if (upcomingSessionsCard) sectionsToToggle.push(upcomingSessionsCard);
        if (patientsByPsychologistCard) sectionsToToggle.push(patientsByPsychologistCard);
        
        // Aplicar visibilidade
        sectionsToToggle.forEach(section => {
            if (section) {
                section.style.display = hasPsychologists ? 'block' : 'none';
            }
        });
        
                console.log(`Seções de profissionais ${hasPsychologists ? 'exibidas' : 'ocultadas'} - ${this.currentData.psychologistsList?.length || 0} profissionais encontrados`);
    },

    renderPsychologistsList() {
        const select = document.getElementById('patients-psychologist-filter');
        if (!select) return;
        
        // Limpar opções existentes (exceto a primeira)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
    // Adicionar opções dos profissionais
        this.currentData.psychologistsList.forEach(psychologist => {
            const option = document.createElement('option');
            option.value = psychologist.id;
            option.textContent = psychologist.nome;
            select.appendChild(option);
        });
    },

    renderStats() {
        const stats = this.currentData.stats;
        console.log('Renderizando estatísticas:', stats);
        
        // Total de sessões
        const totalSessoesEl = document.getElementById('total-sessoes');
        if (totalSessoesEl) {
            totalSessoesEl.textContent = stats.total_sessoes || 0;
        }

        // Sessões agendadas
        const sessoesAgendadasEl = document.getElementById('sessoes-agendadas');
        if (sessoesAgendadasEl) {
            sessoesAgendadasEl.textContent = stats.sessoes_agendadas || 0;
        }

        // Sessões realizadas
        const sessoesRealizadasEl = document.getElementById('sessoes-realizadas');
        if (sessoesRealizadasEl) {
            sessoesRealizadasEl.textContent = stats.sessoes_realizadas || 0;
        }

        // Sessões reagendadas
        const sessoesReagendadasEl = document.getElementById('sessoes-reagendadas');
        if (sessoesReagendadasEl) {
            sessoesReagendadasEl.textContent = stats.sessoes_reagendadas || 0;
        }

        // Sessões com falta
        const sessoesFaltouEl = document.getElementById('sessoes-faltou');
        if (sessoesFaltouEl) {
            sessoesFaltouEl.textContent = stats.sessoes_faltou || 0;
        }

        // Sessões canceladas
        const sessoesCanceladasEl = document.getElementById('sessoes-canceladas');
        if (sessoesCanceladasEl) {
            sessoesCanceladasEl.textContent = stats.sessoes_canceladas || 0;
        }

        // Sessões de hoje
        const sessoesHojeEl = document.getElementById('sessoes-hoje');
        console.log('Elemento sessoes-hoje:', sessoesHojeEl, 'Valor:', stats.sessoes_hoje);
        if (sessoesHojeEl) {
            sessoesHojeEl.textContent = stats.sessoes_hoje || 0;
        }

        // Próximas sessões
        const proximasSessoesEl = document.getElementById('proximas-sessoes');
        console.log('Elemento proximas-sessoes:', proximasSessoesEl, 'Valor:', stats.proximas_sessoes);
        if (proximasSessoesEl) {
            proximasSessoesEl.textContent = stats.proximas_sessoes || 0;
        }
    },

    renderRescheduledSessions() {
        const sessions = this.currentData.rescheduled;
        const container = document.getElementById('rescheduled-sessions-container');
        
        if (!container) return;

        if (!sessions || sessions.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Nenhuma sessão reagendada encontrada no período.</p>';
            return;
        }

        let html = '';
        sessions.forEach(session => {
            const dataOriginal = session.data_original ? this.formatDateTime(session.data_original) : 'N/A';
            const dataReagendamento = session.data_reagendamento ? this.formatDateTime(session.data_reagendamento) : this.formatDateTime(session.data_sessao);

            html += `
                <div class="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900">${session.patient_name}</span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            Reagendada
                        </span>
                    </div>
                    <div class="space-y-1 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-500">Data original:</span>
                            <span class="text-gray-700">${dataOriginal}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Nova data:</span>
                            <span class="text-blue-600 font-medium">${dataReagendamento}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Sessão:</span>
                            <span class="text-gray-700">#${session.numero_sessao}</span>
                        </div>
                    </div>
                    ${session.observacoes ? `<div class="text-sm text-gray-500 mt-2 p-2 bg-gray-50 rounded">${session.observacoes}</div>` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
    },

    renderMissedSessions() {
        const sessions = this.currentData.missed;
        const container = document.getElementById('missed-sessions-container');
        
        if (!container) return;

        if (!sessions || sessions.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Nenhuma falta encontrada no período.</p>';
            return;
        }

        let html = '';
        sessions.forEach(session => {
            html += `
                <div class="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900">${session.patient_name}</span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Faltou
                        </span>
                    </div>
                    <div class="space-y-1 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-500">Data da sessão:</span>
                            <span class="text-red-600 font-medium">${this.formatDateTime(session.data_sessao)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Sessão:</span>
                            <span class="text-gray-700">#${session.numero_sessao}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Valor:</span>
                            <span class="text-gray-700">${this.formatCurrency(session.valor)}</span>
                        </div>
                    </div>
                    ${session.observacoes ? `<div class="text-sm text-gray-500 mt-2 p-2 bg-gray-50 rounded">${session.observacoes}</div>` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
    },

    renderTodaySessions() {
        const sessions = this.currentData.todaySessions;
        const container = document.getElementById('today-sessions-container');
        
        if (!container) return;

        if (!sessions || sessions.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Nenhuma sessão agendada para hoje.</p>';
            return;
        }

        let html = '';
        sessions.forEach(session => {
            const statusColor = session.status === 'reagendada' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800';
            const statusText = session.status === 'reagendada' ? 'Reagendada' : 'Agendada';

            html += `
                <div class="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900">${session.patient_name}</span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor}">
                            ${statusText}
                        </span>
                    </div>
                    <div class="space-y-1 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-500">${session.especialidade_nome || 'Especialidade não informada'}:</span>
                            <span class="text-gray-700">${session.funcionario_nome || 'N/A'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Horário:</span>
                            <span class="text-blue-600 font-medium">${this.formatTime(session.data_sessao)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Sessão:</span>
                            <span class="text-gray-700">#${session.numero_sessao}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Valor:</span>
                            <span class="text-gray-700">${this.formatCurrency(session.valor)}</span>
                        </div>
                    </div>
                    ${session.observacoes ? `<div class="text-sm text-gray-500 mt-2 p-2 bg-gray-50 rounded">${session.observacoes}</div>` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
    },

    renderUpcomingSessions() {
        const sessions = this.currentData.upcomingSessions;
        const container = document.getElementById('upcoming-sessions-container');
        
        if (!container) return;

        if (!sessions || sessions.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Nenhuma sessão próxima encontrada.</p>';
            return;
        }

        let html = '';
        sessions.forEach(session => {
            const statusColor = session.status === 'reagendada' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800';
            const statusText = session.status === 'reagendada' ? 'Reagendada' : 'Agendada';

            html += `
                <div class="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900">${session.patient_name}</span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor}">
                            ${statusText}
                        </span>
                    </div>
                    <div class="space-y-1 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-500">${session.especialidade_nome || 'Especialidade não informada'}:</span>
                            <span class="text-gray-700">${session.funcionario_nome || 'N/A'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Data/Hora:</span>
                            <span class="text-blue-600 font-medium">${this.formatDateTime(session.data_sessao)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Sessão:</span>
                            <span class="text-gray-700">#${session.numero_sessao}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-500">Valor:</span>
                            <span class="text-gray-700">${this.formatCurrency(session.valor)}</span>
                        </div>
                    </div>
                    ${session.observacoes ? `<div class="text-sm text-gray-500 mt-2 p-2 bg-gray-50 rounded">${session.observacoes}</div>` : ''}
                </div>
            `;
        });

        // Wrapper com altura limitada e barra de rolagem para mostrar apenas 5 sessões
        container.innerHTML = `<div style="max-height: 600px; overflow-y: auto; padding-right: 8px;" class="space-y-4">${html}</div>`;
    },

    async loadPatientsStats() {
        try {
            const response = await fetch('/api/dashboard/patients/stats');
            const result = await response.json();

            if (result.success) {
                this.currentData.patientsStats = result.data;
                this.renderPatientsStats();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar estatísticas de pacientes:', error);
            this.currentData.patientsStats = {};
        }
    },

    async loadPatientsList() {
        try {
            const response = await fetch('/api/dashboard/patients/list');
            const result = await response.json();

            if (result.success) {
                this.currentData.patientsList = result.data;
                this.renderPatientsList();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar lista de pacientes:', error);
            this.currentData.patientsList = [];
        }
    },

    renderPatientsStats() {
        const stats = this.currentData.patientsStats;
        
        // Total de pacientes
        const totalPacientesEl = document.getElementById('total-pacientes');
        if (totalPacientesEl) {
            totalPacientesEl.textContent = stats.total_pacientes || 0;
        }

        // Pacientes ativos
        const pacientesAtivosEl = document.getElementById('pacientes-ativos');
        if (pacientesAtivosEl) {
            pacientesAtivosEl.textContent = stats.pacientes_ativos || 0;
        }

        // Pacientes hoje
        const pacientesHojeEl = document.getElementById('pacientes-hoje');
        if (pacientesHojeEl) {
            pacientesHojeEl.textContent = stats.pacientes_hoje || 0;
        }
    },

    renderPatientsList() {
        const patients = this.currentData.patientsList;
        const container = document.getElementById('patients-list-container');
        
        if (!container) return;

        if (!patients || patients.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhum paciente encontrado.</p>';
            return;
        }

        let html = '<div class="table-responsive"><table class="table table-hover"><thead class="table-light"><tr>';
        html += '<th>Nome</th><th>Email</th><th>Telefone</th><th>Total Sessões</th><th>Realizadas</th><th>Agendadas</th><th>Última Sessão</th></tr></thead><tbody>';
        
        patients.forEach(patient => {
            const ultimaSessao = patient.ultima_sessao ? this.formatDate(patient.ultima_sessao) : 'Nunca';
            
            html += `
                <tr>
                    <td><strong>${patient.nome}</strong></td>
                    <td>${patient.email || '-'}</td>
                    <td>${patient.telefone || '-'}</td>
                    <td><span class="badge bg-primary">${patient.total_sessoes}</span></td>
                    <td><span class="badge bg-success">${patient.sessoes_realizadas}</span></td>
                    <td><span class="badge bg-info">${patient.sessoes_agendadas}</span></td>
                    <td>${ultimaSessao}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    },

    async loadPsychologistsStats() {
        try {
            const response = await fetch('/api/dashboard/sessions/by-psychologist');
            const result = await response.json();

            if (result.success) {
                this.currentData.psychologistsStats = result.data;
                this.renderPsychologistsStats();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar estatísticas de profissionais:', error);
            throw error;
        }
    },

    renderPsychologistsStats() {
        const container = document.getElementById('psychologists-stats-container');
        if (!container) return;

        if (!this.currentData.psychologistsStats || this.currentData.psychologistsStats.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhum profissional com atendimentos encontrado.</p>';
            return;
        }

        const html = this.currentData.psychologistsStats.map(psychologist => {
            const totalSessoes = psychologist.total_sessoes || 0;
            const realizadas = psychologist.sessoes_realizadas || 0;
            const agendadas = psychologist.sessoes_agendadas || 0;
            const reagendadas = psychologist.sessoes_reagendadas || 0;
            const faltou = psychologist.sessoes_faltou || 0;
            const canceladas = psychologist.sessoes_canceladas || 0;
            
            const percentualRealizadas = totalSessoes > 0 ? ((realizadas / totalSessoes) * 100).toFixed(1) : 0;
            
            return `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <h6 class="mb-1">${psychologist.nome}</h6>
                                <small class="text-muted">${psychologist.especialidade || 'Especialidade não informada'}</small>
                            </div>
                            <div class="col-md-2 text-center">
                                <h5 class="mb-0 text-primary">${totalSessoes}</h5>
                                <small class="text-muted">Total</small>
                            </div>
                            <div class="col-md-2 text-center">
                                <h5 class="mb-0 text-success">${realizadas}</h5>
                                <small class="text-muted">Realizadas</small>
                            </div>
                            <div class="col-md-2 text-center">
                                <h5 class="mb-0 text-info">${agendadas}</h5>
                                <small class="text-muted">Agendadas</small>
                            </div>
                            <div class="col-md-2 text-center">
                                <h5 class="mb-0 text-warning">${reagendadas}</h5>
                                <small class="text-muted">Reagendadas</small>
                            </div>
                            <div class="col-md-1 text-center">
                                <span class="badge bg-success">${percentualRealizadas}%</span>
                                <small class="d-block text-muted">Taxa</small>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-12">
                                <div class="progress" style="height: 8px;">
                                    <div class="progress-bar bg-success" style="width: ${(realizadas/totalSessoes)*100}%" title="Realizadas: ${realizadas}"></div>
                                    <div class="progress-bar bg-info" style="width: ${(agendadas/totalSessoes)*100}%" title="Agendadas: ${agendadas}"></div>
                                    <div class="progress-bar bg-warning" style="width: ${(reagendadas/totalSessoes)*100}%" title="Reagendadas: ${reagendadas}"></div>
                                    <div class="progress-bar bg-danger" style="width: ${(faltou/totalSessoes)*100}%" title="Faltas: ${faltou}"></div>
                                    <div class="progress-bar bg-secondary" style="width: ${(canceladas/totalSessoes)*100}%" title="Canceladas: ${canceladas}"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    },

    async loadUpcomingSessionsByPsychologist() {
        try {
            const response = await fetch('/api/dashboard/sessions/upcoming-by-psychologist');
            const result = await response.json();

            if (result.success) {
                this.currentData.upcomingSessionsByPsychologist = result.data;
                this.renderUpcomingSessionsByPsychologist();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar sessões futuras por profissional:', error);
            throw error;
        }
    },

    renderUpcomingSessionsByPsychologist() {
        const container = document.getElementById('upcoming-sessions-by-psychologist-container');
        if (!container) return;

        if (!this.currentData.upcomingSessionsByPsychologist || this.currentData.upcomingSessionsByPsychologist.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhuma sessão agendada para os próximos 10 dias.</p>';
            return;
        }

        const html = this.currentData.upcomingSessionsByPsychologist.map(psychologist => {
            const totalSessoes = psychologist.total_sessoes || 0;
            const agendadas = psychologist.sessoes_agendadas || 0;
            const reagendadas = psychologist.sessoes_reagendadas || 0;
            
            return `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-4">
                                <h6 class="mb-1">${psychologist.nome}</h6>
                                <small class="text-muted">${psychologist.especialidade || 'Especialidade não informada'}</small>
                            </div>
                            <div class="col-md-2 text-center">
                                <h5 class="mb-0 text-primary">${totalSessoes}</h5>
                                <small class="text-muted">Total</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <h5 class="mb-0 text-info">${agendadas}</h5>
                                <small class="text-muted">Agendadas</small>
                            </div>
                            <div class="col-md-3 text-center">
                                <h5 class="mb-0 text-warning">${reagendadas}</h5>
                                <small class="text-muted">Reagendadas</small>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-12">
                                <div class="progress" style="height: 8px;">
                                    <div class="progress-bar bg-info" style="width: ${totalSessoes > 0 ? (agendadas/totalSessoes)*100 : 0}%" title="Agendadas: ${agendadas}"></div>
                                    <div class="progress-bar bg-warning" style="width: ${totalSessoes > 0 ? (reagendadas/totalSessoes)*100 : 0}%" title="Reagendadas: ${reagendadas}"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    },

    async loadPatientsByPsychologist() {
        try {
            const params = this.getPsychologistFilters();
            const response = await fetch(`/api/dashboard/patients/by-psychologist?${params}`);
            const result = await response.json();
            
            if (result.success) {
                this.currentData.patientsByPsychologist = result.data;
                this.renderPatientsByPsychologist();
            } else {
                console.error('Erro ao carregar pacientes por profissional:', result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar pacientes por profissional:', error);
        }
    },

    renderPatientsByPsychologist() {
        const container = document.getElementById('patients-by-psychologist-container');
        if (!container) return;

        if (!this.currentData.patientsByPsychologist || this.currentData.patientsByPsychologist.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhum paciente encontrado.</p>';
            return;
        }

        const html = this.currentData.patientsByPsychologist.map(psychologist => {
            const totalPacientes = psychologist.total_pacientes || 0;
            
            let patientsHtml = '';
            if (psychologist.pacientes && psychologist.pacientes.length > 0) {
                patientsHtml = psychologist.pacientes.map(patient => {
                    const ultimaSessao = patient.ultima_sessao ? new Date(patient.ultima_sessao).toLocaleDateString('pt-BR') : 'Nunca';
                    const dataNascimento = patient.data_nascimento ? new Date(patient.data_nascimento).toLocaleDateString('pt-BR') : 'N/A';
                    
                    // Renderizar sessões dos últimos 10 dias
                    let sessoesHtml = '';
                    if (patient.sessoes_ultimos_10_dias && patient.sessoes_ultimos_10_dias.length > 0) {
                        // Ordenar sessões da primeira para a última (ordem cronológica crescente)
                        const sessoesOrdenadas = patient.sessoes_ultimos_10_dias.sort((a, b) => {
                            return new Date(a.data_sessao) - new Date(b.data_sessao);
                        });
                        
                        sessoesHtml = `
                            <div class="mt-3">
                                <h6 class="text-muted mb-2"><i class="bi bi-clock-history me-1"></i>Últimos 10 dias:</h6>
                                <div class="sessions-list" style="max-height: 200px; overflow-y: auto;">
                                    ${sessoesOrdenadas.map(sessao => {
                                        const statusClass = {
                                            'REALIZADA': 'success',
                                            'AGENDADA': 'info',
                                            'CANCELADA': 'danger',
                                            'REAGENDADA': 'warning'
                                        }[sessao.status] || 'secondary';
                                        
                                        const dataFormatada = new Date(sessao.data_sessao).toLocaleDateString('pt-BR', {
                                            day: '2-digit',
                                            month: '2-digit',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        });
                                        
                                        return `
                                            <div class="d-flex justify-content-between align-items-center mb-1 p-2 border rounded">
                                                <div>
                                                    <small class="fw-bold">${dataFormatada}</small>
                                                    ${sessao.observacoes ? `<br><small class="text-muted">${sessao.observacoes}</small>` : ''}
                                                </div>
                                                <div class="text-end">
                                                    <span class="badge bg-${statusClass}">${sessao.status}</span>
                                                    ${sessao.valor ? `<br><small class="text-success">R$ ${parseFloat(sessao.valor).toFixed(2)}</small>` : ''}
                                                </div>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        `;
                    } else {
                        sessoesHtml = `
                            <div class="mt-3">
                                <h6 class="text-muted mb-2"><i class="bi bi-clock-history me-1"></i>Últimos 10 dias:</h6>
                                <p class="small text-muted text-center">Nenhuma sessão nos últimos 10 dias</p>
                            </div>
                        `;
                    }
                    
                    return `
                        <div class="col-md-6 col-lg-4 mb-3">
                            <div class="card h-100 border-left-primary">
                                <div class="card-body">
                                    <div class="d-flex align-items-center mb-2">
                                        <i class="bi bi-person-circle text-primary me-2 fs-4"></i>
                                        <h6 class="mb-0 fw-bold">${patient.nome_completo}</h6>
                                    </div>
                                    <div class="small text-muted mb-2">
                                        <div><i class="bi bi-envelope me-1"></i>${patient.email || 'N/A'}</div>
                                        <div><i class="bi bi-telephone me-1"></i>${patient.telefone || 'N/A'}</div>
                                        <div><i class="bi bi-calendar me-1"></i>Nascimento: ${dataNascimento}</div>
                                    </div>
                                    <div class="row text-center mt-3">
                                        <div class="col-4">
                                            <div class="text-primary fw-bold">${patient.total_sessoes}</div>
                                            <div class="small text-muted">Total</div>
                                        </div>
                                        <div class="col-4">
                                            <div class="text-success fw-bold">${patient.sessoes_realizadas}</div>
                                            <div class="small text-muted">Realizadas</div>
                                        </div>
                                        <div class="col-4">
                                            <div class="text-info fw-bold">${patient.sessoes_agendadas}</div>
                                            <div class="small text-muted">Agendadas</div>
                                        </div>
                                    </div>
                                    <div class="mt-2 text-center">
                                        <small class="text-muted">Última sessão: ${ultimaSessao}</small>
                                    </div>
                                    ${sessoesHtml}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                patientsHtml = '<div class="col-12"><p class="text-muted text-center">Nenhum paciente encontrado para este profissional.</p></div>';
            }
            
            return `
                <div class="mb-4">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h5 class="mb-0">
                                        <i class="bi bi-person-badge me-2"></i>${psychologist.nome}
                                    </h5>
                                    <small class="opacity-75">${psychologist.especialidade}</small>
                                </div>
                                <div class="col-md-4 text-end">
                                    <span class="badge bg-light text-dark fs-6">
                                        <i class="bi bi-people me-1"></i>${totalPacientes} paciente${totalPacientes !== 1 ? 's' : ''}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                ${patientsHtml}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    },

    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value || 0);
    },

    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    },

    formatTime(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    },

    formatDateTime(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    },

    showError(message) {
        // Implementar notificação de erro
        console.error(message);
        alert(message);
    }
};

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash === '#dashboard-sessions') {
        window.DashboardSessions.init();
    }
});

// Reinicializar quando navegar para a página
window.addEventListener('hashchange', function() {
    if (window.location.hash === '#dashboard-sessions') {
        window.DashboardSessions.init();
    }
});

