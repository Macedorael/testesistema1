// Dashboard JavaScript
window.Dashboard = {
    charts: {},

    async init() {
        // Verificar se não estamos no processo de logout
        if (window.isLoggingOut) {
            console.log('[DEBUG] Dashboard.init() cancelado - logout em progresso');
            return;
        }
        
        console.log('[DEBUG] Dashboard.init() iniciado');
        await this.loadStats();
        await this.loadCharts();
        await this.loadTodaySessions();
        await this.loadUpcomingSessions();
        await this.loadRecentPayments();
    },

    async loadStats() {
        try {
            // Verificar se não estamos no processo de logout
            if (window.isLoggingOut) {
                console.log('[DEBUG] Dashboard.loadStats() cancelado - logout em progresso');
                return;
            }
            
            const response = await window.app.apiCall('/dashboard/stats');
            const stats = response.data;
            
            this.renderStatsCards(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
            // Só mostra erro se for um erro real, não quando não há dados
            if (error.message && !error.message.includes('não encontrado')) {
                window.app.showError('Erro ao carregar estatísticas');
            } else {
                // Renderiza cards com valores zerados quando não há dados
                this.renderStatsCards({
                    general: { total_patients: 0, active_patients: 0, inactive_patients: 0, total_appointments: 0, total_sessions: 0, total_payments: 0 },
                    financial: { total_recebido: 0, total_a_receber: 0, total_geral: 0 },
                    sessions: { realizadas: 0, agendadas: 0, canceladas: 0, faltou: 0, pagas: 0, pendentes: 0, proximas_7_dias: 0, hoje: 0, hoje_realizadas: 0, hoje_total: 0, hoje_restantes: 0 }
                });
            }
        }
    },

    renderStatsCards(stats) {
        const statsContainer = document.getElementById('stats-cards');
        if (!statsContainer) {
            console.warn('Elemento #stats-cards não encontrado');
            return;
        }
        
        const statsCards = [
            {
                title: 'Total de Pacientes',
                value: stats.general.total_patients,
                icon: 'people',
                color: 'primary',
                page: 'patients'
            },
            {
                title: 'Pacientes Ativos',
                value: stats.general.active_patients,
                icon: 'person-check',
                color: 'success',
                page: 'patients'
            },
            {
                title: 'Pacientes Inativos',
                value: stats.general.inactive_patients,
                icon: 'person-dash',
                color: 'danger',
                page: 'patients'
            },
            {
                title: 'Total Recebido',
                value: window.app.formatCurrency(stats.financial.total_recebido),
                icon: 'cash-coin',
                color: 'success'
            },
            {
                title: 'A Receber',
                value: window.app.formatCurrency(stats.financial.total_a_receber),
                icon: 'clock-history',
                color: 'warning'
            },
            {
                title: 'Sessões Hoje',
                value: `${stats.sessions.hoje_total} (${stats.sessions.hoje_restantes} restantes)`,
                icon: 'calendar-day',
                color: 'info'
            },
            {
                title: 'Próximas Sessões (7 dias)',
                value: stats.sessions.proximas_7_dias,
                icon: 'calendar-week',
                color: 'primary'
            },
            {
                title: 'Sessões Realizadas',
                value: stats.sessions.realizadas,
                icon: 'check-circle',
                color: 'success'
            },
            {
                title: 'Sessões Pendentes',
                value: stats.sessions.pendentes,
                icon: 'clock',
                color: 'warning'
            },
            {
                title: 'Total de Agendamentos',
                value: stats.general.total_appointments,
                icon: 'calendar-check',
                color: 'info'
            }
        ];

        const cardsHtml = statsCards.map(card => {
            const clickableAttr = card.page ? ` role="button" style="cursor:pointer" onclick="window.app.loadPage('${card.page}')" ` : '';
            return `
            <div class="col-lg-3 col-md-6 mb-4">
                <div class="stats-card ${card.color}"${clickableAttr}>
                    <div class="d-flex align-items-center">
                        <div class="stats-icon me-3">
                            <i class="bi bi-${card.icon}"></i>
                        </div>
                        <div>
                            <div class="stats-number">${card.value}</div>
                            <div class="stats-label">${card.title}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        }).join('');

        statsContainer.innerHTML = cardsHtml;
    },

    async loadCharts() {
        try {
            const [revenueResponse, statsResponse] = await Promise.all([
                window.app.apiCall('/dashboard/monthly-revenue'),
                window.app.apiCall('/dashboard/stats')
            ]);

            this.renderRevenueChart(revenueResponse.data);
            this.renderSessionsChart(statsResponse.data.sessions);
        } catch (error) {
            console.error('Error loading charts:', error);
            // Só mostra erro se for um erro real, não quando não há dados
            if (error.message && !error.message.includes('não encontrado')) {
                window.app.showError('Erro ao carregar gráficos');
            } else {
                // Renderiza gráficos com dados vazios
                this.renderRevenueChart([]);
                this.renderSessionsChart({ realizadas: 0, agendadas: 0, canceladas: 0, faltou: 0 });
            }
        }
    },

    renderRevenueChart(monthlyData) {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }

        // Se não há dados, criar dados vazios para os últimos 6 meses
        if (!monthlyData || monthlyData.length === 0) {
            const now = new Date();
            monthlyData = [];
            for (let i = 5; i >= 0; i--) {
                const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
                monthlyData.push({
                    month_name: date.toLocaleDateString('pt-BR', { month: 'long' }),
                    year: date.getFullYear(),
                    revenue: 0
                });
            }
        }

        const labels = monthlyData.map(item => `${item.month_name}/${item.year}`);
        const revenues = monthlyData.map(item => item.revenue || 0);

        this.charts.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Receita Mensal',
                    data: revenues,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('pt-BR', {
                                    style: 'currency',
                                    currency: 'BRL'
                                }).format(value);
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 6,
                        hoverRadius: 8
                    }
                }
            }
        });
    },

    renderSessionsChart(sessionsData) {
        const ctx = document.getElementById('sessionsChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.sessions) {
            this.charts.sessions.destroy();
        }

        // Se não há dados, usar valores zerados
        if (!sessionsData) {
            sessionsData = { realizadas: 0, agendadas: 0, canceladas: 0, faltou: 0 };
        }

        const data = [
            sessionsData.realizadas || 0,
            sessionsData.agendadas || 0,
            sessionsData.canceladas || 0,
            sessionsData.faltou || 0
        ];

        // Se todos os valores são zero, mostrar pelo menos um valor para o gráfico não ficar vazio
        const hasData = data.some(value => value > 0);
        if (!hasData) {
            data[0] = 1; // Mostrar "Nenhuma sessão" como uma fatia
        }

        let labels = ['Realizadas', 'Agendadas', 'Canceladas', 'Faltou'];
        let colors = ['#198754', '#0dcaf0', '#dc3545', '#ffc107'];
        
        // Se não há dados, ajustar labels e cores
        if (!hasData) {
            labels = ['Nenhuma sessão', '', '', ''];
            colors = ['#6c757d', 'transparent', 'transparent', 'transparent'];
        }

        this.charts.sessions = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    },

    async loadTodaySessions() {
        try {
            console.log('[DEBUG] Carregando sessões de hoje...');
            const response = await window.app.apiCall('/dashboard/sessions/today');
            const sessions = response.data;
            
            console.log('[DEBUG] Resposta da API para sessões de hoje:', response);
            console.log('[DEBUG] Número de sessões:', sessions.length);
            
            sessions.forEach((session, index) => {
                console.log(`[DEBUG] Sessão ${index + 1}:`, {
                    id: session.id,
                    patient_name: session.patient_name,
                    funcionario_nome: session.funcionario_nome,
                    especialidade_nome: session.especialidade_nome,
                    funcionario_especialidade: session.funcionario_especialidade,
                    funcionario_id: session.funcionario_id
                });
            });
            
            this.renderTodaySessions(sessions);
        } catch (error) {
            console.error('Error loading today sessions:', error);
            const container = document.getElementById('today-sessions');
            if (container) {
                container.innerHTML = '<div class="text-muted">Erro ao carregar atendimentos de hoje</div>';
            }
        }
    },

    renderTodaySessions(sessions) {
        const container = document.getElementById('today-sessions');
        
        if (!container) {
            console.warn('Element with id "today-sessions" not found');
            return;
        }
        
        if (sessions.length === 0) {
            container.innerHTML = '<div class="text-muted">Nenhum atendimento agendado para hoje</div>';
            return;
        }

        const sessionsHtml = sessions.map(session => `
            <div class="d-flex align-items-center mb-3 p-2 border rounded">
                <div class="me-3">
                    <i class="bi bi-calendar-event text-primary fs-4"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="fw-bold">${session.patient_name}</div>
                    <div class="text-muted small">
                        <i class="bi bi-clock me-1"></i>
                        ${window.app.formatDateTime(session.data_sessao)}
                    </div>
                    <div class="text-muted small">
                        <i class="bi bi-currency-dollar me-1"></i>
                        Sessão ${session.numero_sessao} - ${window.app.formatCurrency(session.valor)}
                    </div>
                    <div class="text-muted small">
                        <i class="bi bi-person-badge me-1"></i>
                        ${session.funcionario_nome} - ${session.especialidade_nome || 'Especialidade não informada'}
                    </div>
                </div>
                <div>
                    <span class="status-badge status-${session.status}">${session.status}</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = sessionsHtml;
    },

    async loadUpcomingSessions() {
        try {
            console.log('[DEBUG] Carregando sessões próximas...');
            const response = await window.app.apiCall('/dashboard/sessions/upcoming?limit=5');
            const sessions = response.data;
            
            console.log('[DEBUG] Resposta da API para sessões próximas:', response);
            console.log('[DEBUG] Número de sessões próximas:', sessions.length);
            
            sessions.forEach((session, index) => {
                console.log(`[DEBUG] Sessão próxima ${index + 1}:`, {
                    id: session.id,
                    patient_name: session.patient_name,
                    funcionario_nome: session.funcionario_nome,
                    especialidade_nome: session.especialidade_nome,
                    funcionario_especialidade: session.funcionario_especialidade,
                    funcionario_id: session.funcionario_id
                });
            });
            
            this.renderUpcomingSessions(sessions);
        } catch (error) {
            console.error('Error loading upcoming sessions:', error);
            const container = document.getElementById('upcoming-sessions');
            if (container) {
                container.innerHTML = '<div class="text-muted">Erro ao carregar próximas sessões</div>';
            }
        }
    },

    renderUpcomingSessions(sessions) {
        const container = document.getElementById('upcoming-sessions');
        
        if (!container) {
            console.warn('Element with id "upcoming-sessions" not found');
            return;
        }
        
        if (sessions.length === 0) {
            container.innerHTML = '<div class="text-muted">Nenhuma sessão agendada</div>';
            return;
        }

        const sessionsHtml = sessions.map(session => `
            <div class="d-flex align-items-center mb-3 p-2 border rounded">
                <div class="me-3">
                    <i class="bi bi-calendar-event text-primary fs-4"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="fw-bold">${session.patient_name}</div>
                    <div class="text-muted small">
                        <i class="bi bi-clock me-1"></i>
                        ${window.app.formatDateTime(session.data_sessao)}
                    </div>
                    <div class="text-muted small">
                        <i class="bi bi-currency-dollar me-1"></i>
                        Sessão ${session.numero_sessao} - ${window.app.formatCurrency(session.valor)}
                    </div>
                    <div class="text-muted small">
                        <i class="bi bi-person-badge me-1"></i>
                        ${session.funcionario_nome} - ${session.especialidade_nome || 'Especialidade não informada'}
                    </div>
                </div>
                <div>
                    <span class="status-badge status-${session.status}">${session.status}</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = sessionsHtml;
    },

    async loadRecentPayments() {
        try {
            const response = await window.app.apiCall('/dashboard/recent-payments?limit=5');
            const payments = response.data;
            
            this.renderRecentPayments(payments);
        } catch (error) {
            console.error('Error loading recent payments:', error);
            const container = document.getElementById('recent-payments');
            if (container) {
                container.innerHTML = '<div class="text-muted">Erro ao carregar pagamentos recentes</div>';
            }
        }
    },

    renderRecentPayments(payments) {
        const container = document.getElementById('recent-payments');
        if (!container) {
            console.warn('Elemento #recent-payments não encontrado');
            return;
        }
        
        if (payments.length === 0) {
            container.innerHTML = '<div class="text-muted">Nenhum pagamento registrado</div>';
            return;
        }

        const paymentsHtml = payments.map(payment => `
            <div class="d-flex align-items-center mb-3 p-2 border rounded">
                <div class="me-3">
                    <i class="bi bi-credit-card text-success fs-4"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="fw-bold">${payment.patient_name}</div>
                    <div class="text-muted small">
                        ${window.app.formatDate(payment.data_pagamento)}
                    </div>
                    <div class="text-success fw-bold">
                        ${window.app.formatCurrency(payment.valor_pago)}
                    </div>
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-primary" onclick="Payments.viewPayment(${payment.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = paymentsHtml;
    }
};

