// Dashboard Payments JavaScript
window.DashboardPayments = {
    initialized: false,
    currentData: {
        stats: {},
        modalidades: [],
        recentPayments: [],
        pendingSessions: []
    },

    init() {
        // Verificar se não estamos no processo de logout
        if (window.isLoggingOut) {
            console.log('[DEBUG] DashboardPayments.init() cancelado - logout em progresso');
            return;
        }
        
        console.log('[DEBUG] DashboardPayments.init() iniciado');
        if (!this.initialized) {
            this.setupEventListeners();
            this.initialized = true;
        }
        this.loadDashboard();
    },

    setupEventListeners() {
        // Filtros de data
        const dateFromInput = document.getElementById('payments-date-from');
        const dateToInput = document.getElementById('payments-date-to');
        const filterBtn = document.getElementById('payments-filter-btn');
        const clearBtn = document.getElementById('payments-clear-btn');

        if (filterBtn) {
            filterBtn.addEventListener('click', () => {
                this.loadDashboard();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (dateFromInput) dateFromInput.value = '';
                if (dateToInput) dateToInput.value = '';
                this.loadDashboard();
            });
        }

        // Refresh automático a cada 5 minutos
        setInterval(() => {
            this.loadDashboard();
        }, 300000);
    },

    async loadDashboard() {
        try {
            await Promise.all([
                this.loadStats(),
                this.loadModalidades(),
                this.loadRecentPayments(),
                this.loadPendingSessions()
            ]);
        } catch (error) {
            console.error('Erro ao carregar dashboard de pagamentos:', error);
            this.showError('Erro ao carregar dados do dashboard');
        }
    },

    async loadStats() {
        try {
            const params = this.getDateFilters();
            const response = await fetch(`/api/dashboard/payments/stats?${params}`);
            const result = await response.json();

            if (result.success) {
                this.currentData.stats = result.data;
                this.renderStats();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
            // Fallback visual
            const totalRecebidoEl = document.getElementById('total-recebido');
            if (totalRecebidoEl) totalRecebidoEl.textContent = this.formatCurrency(0);
            const totalReceberEl = document.getElementById('total-receber');
            if (totalReceberEl) totalReceberEl.textContent = this.formatCurrency(0);
            const totalPagamentosEl = document.getElementById('total-pagamentos');
            if (totalPagamentosEl) totalPagamentosEl.textContent = '0';
            const sessoesPendentesEl = document.getElementById('sessoes-pendentes');
            if (sessoesPendentesEl) sessoesPendentesEl.textContent = '0';
            throw error;
        }
    },

    async loadModalidades() {
        try {
            const params = this.getDateFilters();
            const response = await fetch(`/api/dashboard/payments/by-modality?${params}`);
            const result = await response.json();

            if (result.success) {
                this.currentData.modalidades = result.data;
                this.renderModalidades();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar modalidades:', error);
            const container = document.getElementById('modalidades-container');
            if (container) {
                container.innerHTML = '<p class="text-gray-500">Erro ao carregar modalidades.</p>';
            }
            throw error;
        }
    },

    async loadRecentPayments() {
        try {
            const response = await fetch('/api/dashboard/payments/recent?limit=10');
            const result = await response.json();

            if (result.success) {
                this.currentData.recentPayments = result.data;
                this.renderRecentPayments();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar pagamentos recentes:', error);
            const container = document.getElementById('recent-payments-container');
            if (container) {
                container.innerHTML = '<p class="text-gray-500">Erro ao carregar pagamentos recentes.</p>';
            }
            throw error;
        }
    },

    async loadPendingSessions() {
        try {
            const response = await fetch('/api/dashboard/payments/pending-sessions?limit=10');
            const result = await response.json();

            if (result.success) {
                this.currentData.pendingSessions = result.data;
                this.renderPendingSessions();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Erro ao carregar sessões pendentes:', error);
            const container = document.getElementById('pending-sessions-container');
            if (container) {
                container.innerHTML = '<p class="text-gray-500">Erro ao carregar sessões pendentes.</p>';
            }
            throw error;
        }
    },

    getDateFilters() {
        const dateFrom = document.getElementById('payments-date-from')?.value;
        const dateTo = document.getElementById('payments-date-to')?.value;
        
        const params = new URLSearchParams();
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);
        
        return params.toString();
    },

    renderStats() {
        const stats = this.currentData.stats;
        
        // Total recebido
        const totalRecebidoEl = document.getElementById('total-recebido');
        if (totalRecebidoEl) {
            totalRecebidoEl.textContent = this.formatCurrency(stats.total_recebido || 0);
        }

        // Total a receber
        const totalReceberEl = document.getElementById('total-receber');
        if (totalReceberEl) {
            totalReceberEl.textContent = this.formatCurrency(stats.total_a_receber || 0);
        }

        // Total de pagamentos
        const totalPagamentosEl = document.getElementById('total-pagamentos');
        if (totalPagamentosEl) {
            totalPagamentosEl.textContent = stats.total_pagamentos || 0;
        }

        // Sessões pendentes
        const sessoesPendentesEl = document.getElementById('sessoes-pendentes');
        if (sessoesPendentesEl) {
            sessoesPendentesEl.textContent = stats.total_sessoes_pendentes || 0;
        }
    },

    renderModalidades() {
        const data = this.currentData.modalidades;
        const container = document.getElementById('modalidades-container');
        
        if (!container) return;

        if (!data.modalidades || data.modalidades.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Nenhum pagamento encontrado no período.</p>';
            return;
        }

        // Modalidade com maior volume
        const maiorVolumeEl = document.getElementById('modalidade-maior-volume');
        if (maiorVolumeEl && data.modalidade_maior_volume) {
            const maior = data.modalidade_maior_volume;
            maiorVolumeEl.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-medium">${maior.modalidade}</span>
                    <span class="text-green-600 font-bold">${this.formatCurrency(maior.total_valor)}</span>
                </div>
                <div class="text-sm text-gray-500">${maior.quantidade} pagamento(s)</div>
            `;
        }

        // Lista de modalidades
        let html = '';
        data.modalidades.forEach(modalidade => {
            const percentage = data.total_geral > 0 ? (modalidade.total_valor / data.total_geral * 100).toFixed(1) : 0;
            
            html += `
                <div class="bg-white p-4 rounded-lg border border-gray-200">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900">${modalidade.modalidade}</span>
                        <span class="text-sm text-gray-500">${percentage}%</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-2xl font-bold text-green-600">${this.formatCurrency(modalidade.total_valor)}</span>
                        <span class="text-sm text-gray-500">${modalidade.quantidade} pag.</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                        <div class="bg-blue-600 h-2 rounded-full" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    },

    renderRecentPayments() {
        const payments = this.currentData.recentPayments;
        const container = document.getElementById('recent-payments-container');
        
        if (!container) return;

        if (!payments || payments.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Nenhum pagamento recente encontrado.</p>';
            return;
        }

        let html = '';
        payments.forEach(payment => {
            const modalidadeBadge = payment.modalidade_pagamento ? 
                `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${payment.modalidade_pagamento}
                </span>` : '';

            html += `
                <div class="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900">${payment.patient_name}</span>
                        <span class="text-sm text-gray-500">${this.formatDate(payment.data_pagamento)}</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-lg font-bold text-green-600">${this.formatCurrency(payment.valor_pago)}</span>
                        ${modalidadeBadge}
                    </div>
                    ${payment.observacoes ? `<div class="text-sm text-gray-500 mt-1">${payment.observacoes}</div>` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
    },

    renderPendingSessions() {
        const sessions = this.currentData.pendingSessions;
        const container = document.getElementById('pending-sessions-container');
        
        if (!container) return;

        if (!sessions || sessions.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Nenhuma sessão pendente encontrada.</p>';
            return;
        }

        let html = '';
        sessions.forEach(session => {
            html += `
                <div class="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900">${session.patient_name}</span>
                        <span class="text-sm text-gray-500">${this.formatDateTime(session.data_sessao)}</span>
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-lg font-bold text-orange-600">${this.formatCurrency(session.valor)}</span>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            Sessão ${session.numero_sessao}
                        </span>
                    </div>
                    ${session.observacoes ? `<div class="text-sm text-gray-500 mt-1">${session.observacoes}</div>` : ''}
                </div>
            `;
        });

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
    if (window.location.hash === '#dashboard-payments') {
        window.DashboardPayments.init();
    }
});

// Reinicializar quando navegar para a página
window.addEventListener('hashchange', function() {
    if (window.location.hash === '#dashboard-payments') {
        window.DashboardPayments.init();
    }
});

