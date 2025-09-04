// JavaScript de Pagamentos
window.Payments = {
    payments: [],
    patients: [],
    currentPayment: null,

    async init() {
        await this.loadPatients();
        await this.loadPayments();
        this.setupEventListeners();
    },

    setupEventListeners() {
        // Filtros de data
        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        
        if (dateFrom) {
            dateFrom.addEventListener('change', () => this.applyFilters());
        }
        
        if (dateTo) {
            dateTo.addEventListener('change', () => this.applyFilters());
        }
    },

    async loadPatients() {
        try {
            const response = await window.app.apiCall('/patients');
            this.patients = response.data;
            this.populatePatientFilters();
        } catch (error) {
            console.error('Erro ao carregar pacientes:', error);
        }
    },

    populatePatientFilters() {
        const patientFilter = document.getElementById('payment-patient-filter');
        if (patientFilter) {
            const options = this.patients.map(patient => 
                `<option value="${patient.id}">${patient.nome_completo}</option>`
            ).join('');
            patientFilter.innerHTML = '<option value="">Todos os pacientes</option>' + options;
        }
    },

    async loadPayments() {
        try {
            const response = await window.app.apiCall('/payments');
            this.payments = response.data;
            this.renderPayments(this.payments);
        } catch (error) {
            console.error('Erro ao carregar pagamentos:', error);
            window.app.showError('Erro ao carregar pagamentos');
        }
    },

    renderPayments(payments) {
        const container = document.getElementById('payments-list');
        
        if (payments.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-credit-card-2-front fs-1 text-muted"></i>
                    <h4 class="text-muted mt-3">Nenhum pagamento encontrado</h4>
                    <p class="text-muted">Clique em "Registrar Pagamento" para adicionar o primeiro pagamento.</p>
                </div>
            `;
            return;
        }

        const paymentsHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Paciente</th>
                            <th>Data</th>
                            <th>Valor</th>
                            <th>Modalidade</th>
                            <th>Sessões</th>
                            <th>Observações</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${payments.map(payment => `
                            <tr>
                                <td>
                                    <div class="fw-bold">${payment.patient_name}</div>
                                </td>
                                <td>${window.app.formatDate(payment.data_pagamento)}</td>
                                <td class="fw-bold text-success">${window.app.formatCurrency(payment.valor_pago)}</td>
                                <td>
                                    ${payment.modalidade_pagamento ? `
                                        <span class="badge bg-info">${payment.modalidade_pagamento}</span>
                                    ` : '-'}
                                </td>
                                <td>
                                    <span class="badge bg-primary">${payment.sessions ? payment.sessions.length : 0}</span>
                                </td>
                                <td>
                                    ${payment.observacoes ? `
                                        <small class="text-muted">${payment.observacoes.substring(0, 50)}${payment.observacoes.length > 50 ? '...' : ''}</small>
                                    ` : '-'}
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="Payments.viewPayment(${payment.id})" title="Ver detalhes">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-secondary" onclick="Payments.editPayment(${payment.id})" title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-outline-danger" onclick="Payments.deletePayment(${payment.id})" title="Excluir">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = paymentsHtml;
    },

    applyFilters() {
        const dateFrom = document.getElementById('date-from')?.value;
        const dateTo = document.getElementById('date-to')?.value;
        const patientFilter = document.getElementById('payment-patient-filter')?.value;
        
        let filtered = [...this.payments];
        
        if (dateFrom) {
            filtered = filtered.filter(payment => 
                payment.data_pagamento >= dateFrom
            );
        }
        
        if (dateTo) {
            filtered = filtered.filter(payment => 
                payment.data_pagamento <= dateTo
            );
        }
        
        if (patientFilter) {
            filtered = filtered.filter(payment => 
                payment.patient_id.toString() === patientFilter
            );
        }
        
        this.renderPayments(filtered);
    },

    showCreateModal() {
        this.currentPayment = null;
        this.showPaymentModal();
    },

    showCreateModalForPatient(patientId) {
        this.currentPayment = null;
        this.showPaymentModal(patientId);
    },

    showCreateModalForAppointment(appointmentId) {
        this.currentPayment = null;
        this.showPaymentModal(null, appointmentId);
    },

    editPayment(paymentId) {
        this.currentPayment = this.payments.find(p => p.id === paymentId);
        this.showPaymentModal();
    },

    async showPaymentModal(preselectedPatientId = null, preselectedAppointmentId = null) {
        const isEdit = this.currentPayment !== null;
        const title = isEdit ? 'Editar Pagamento' : 'Registrar Pagamento';
        
        // Carregar sessões não pagas para o paciente selecionado
        let unpaidSessions = [];
        if (preselectedPatientId || (isEdit && this.currentPayment.patient_id)) {
            const patientId = preselectedPatientId || this.currentPayment.patient_id;
            try {
                const response = await window.app.apiCall(`/patients/${patientId}/sessions/unpaid`);
                unpaidSessions = response.data;
            } catch (error) {
                console.error('Erro ao carregar sessões não pagas:', error);
            }
        }
        
        const modalHtml = `
            <div class="modal fade" id="paymentModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="paymentForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="payment_patient_id" class="form-label">Paciente *</label>
                                            <select class="form-select" id="payment_patient_id" required onchange="Payments.onPatientChange()">
                                                <option value="">Selecione um paciente</option>
                                                ${this.patients.map(patient => `
                                                    <option value="${patient.id}" 
                                                        ${isEdit && this.currentPayment.patient_id === patient.id ? 'selected' : ''}
                                                        ${preselectedPatientId === patient.id ? 'selected' : ''}>
                                                        ${patient.nome_completo}
                                                    </option>
                                                `).join('')}
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="mb-3">
                                            <label for="data_pagamento" class="form-label">Data do Pagamento *</label>
                                            <input type="date" class="form-control" id="data_pagamento" required
                                                value="${isEdit ? this.currentPayment.data_pagamento : new Date().toISOString().split('T')[0]}">
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="mb-3">
                                            <label for="valor_pago" class="form-label">Valor Pago *</label>
                                            <div class="input-group">
                                                <span class="input-group-text">R$</span>
                                                <input type="number" class="form-control" id="valor_pago" required min="0" step="0.01"
                                                    value="${isEdit ? this.currentPayment.valor_pago : ''}"
                                                    readonly title="Valor preenchido automaticamente baseado nas sessões selecionadas">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="modalidade_pagamento" class="form-label">Modalidade de Pagamento</label>
                                            <select class="form-select" id="modalidade_pagamento">
                                                <option value="">Selecione a modalidade</option>
                                                <option value="PIX" ${isEdit && this.currentPayment.modalidade_pagamento === 'PIX' ? 'selected' : ''}>Pix</option>
                                                <option value="DINHEIRO" ${isEdit && this.currentPayment.modalidade_pagamento === 'DINHEIRO' ? 'selected' : ''}>Dinheiro</option>
                                                <option value="CARTAO_CREDITO" ${isEdit && this.currentPayment.modalidade_pagamento === 'CARTAO_CREDITO' ? 'selected' : ''}>Cartão de crédito</option>
                                                <option value="CARTAO_DEBITO" ${isEdit && this.currentPayment.modalidade_pagamento === 'CARTAO_DEBITO' ? 'selected' : ''}>Cartão de débito</option>
                                                <option value="LINK_PAGAMENTO" ${isEdit && this.currentPayment.modalidade_pagamento === 'LINK_PAGAMENTO' ? 'selected' : ''}>Link de pagamento</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="observacoes_payment" class="form-label">Observações</label>
                                            <textarea class="form-control" id="observacoes_payment" rows="2"
                                                placeholder="Observações sobre o pagamento...">${isEdit ? (this.currentPayment.observacoes || '') : ''}</textarea>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Sessions Selection -->
                                <div class="mb-3">
                                    <label class="form-label">Sessões a Pagar *</label>
                                    <div id="sessions-container">
                                        ${this.renderSessionsSelection(unpaidSessions)}
                                    </div>
                                </div>
                                
                                <!-- Summary -->
                                <div class="alert alert-info">
                                    <h6><i class="bi bi-info-circle me-1"></i>Resumo</h6>
                                    <div id="payment-summary">
                                        <p class="mb-1"><strong>Sessões selecionadas:</strong> <span id="summary-sessions">0</span></p>
                                        <p class="mb-1"><strong>Valor das sessões:</strong> <span id="summary-sessions-value">R$ 0,00</span></p>
                                        <p class="mb-0"><strong>Valor do pagamento:</strong> <span id="summary-payment-value">R$ 0,00</span></p>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="Payments.savePayment()">
                                ${isEdit ? 'Atualizar' : 'Registrar'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remover modal existente
        const existingModal = document.getElementById('paymentModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Adicionar novo modal
        document.getElementById('modals-container').innerHTML = modalHtml;
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
        modal.show();

        // Atualizar resumo
        this.updatePaymentSummary();
    },

    renderSessionsSelection(sessions) {
        if (!sessions || sessions.length === 0) {
            return '<div class="text-muted">Nenhuma sessão pendente encontrada. Selecione um paciente primeiro.</div>';
        }

        return `
            <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th width="50">
                                <input type="checkbox" id="select-all-sessions" onchange="Payments.toggleAllSessions()">
                            </th>
                            <th>Sessão</th>
                            <th>Data</th>
                            <th>Valor</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${sessions.map(session => {
                            const isPaid = session.status_pagamento === 'pago';
                            const rowClass = isPaid ? 'table-secondary opacity-50' : '';
                            const checkboxDisabled = isPaid ? 'disabled' : '';
                            const checkboxClass = isPaid ? 'session-checkbox-paid' : 'session-checkbox';
                            
                            return `
                                <tr class="${rowClass}">
                                    <td>
                                        <input type="checkbox" class="${checkboxClass}" value="${session.id}" 
                                            data-value="${session.valor}" ${checkboxDisabled}
                                            onchange="Payments.updatePaymentSummary()" 
                                            ${isPaid ? 'title="Sessão já paga"' : ''}>
                                    </td>
                                    <td>Sessão ${session.numero_sessao} ${isPaid ? '<i class="bi bi-check-circle text-success ms-1" title="Paga"></i>' : ''}</td>
                                    <td>${window.app.formatDateTime(session.data_sessao)}</td>
                                    <td>${window.app.formatCurrency(session.valor)}</td>
                                    <td><span class="status-badge status-${session.status}">${session.status}</span></td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    async onPatientChange() {
        const patientId = document.getElementById('payment_patient_id').value;
        
        if (!patientId) {
            document.getElementById('sessions-container').innerHTML = 
                '<div class="text-muted">Selecione um paciente primeiro.</div>';
            this.updatePaymentSummary();
            return;
        }

        try {
            // Carregar todas as sessões do paciente (pagas e não pagas)
            const response = await window.app.apiCall(`/patients/${patientId}/sessions/all`);
            const sessions = response.data;
            
            document.getElementById('sessions-container').innerHTML = this.renderSessionsSelection(sessions);
            this.updatePaymentSummary();
        } catch (error) {
            console.error('Erro ao carregar sessões do paciente:', error);
            // Fallback para carregar apenas sessões não pagas se a nova rota não existir
            try {
                const response = await window.app.apiCall(`/patients/${patientId}/sessions/unpaid`);
                const sessions = response.data;
                
                document.getElementById('sessions-container').innerHTML = this.renderSessionsSelection(sessions);
                this.updatePaymentSummary();
            } catch (fallbackError) {
                console.error('Erro ao carregar sessões não pagas:', fallbackError);
                document.getElementById('sessions-container').innerHTML = 
                    '<div class="text-danger">Erro ao carregar sessões.</div>';
            }
        }
    },

    toggleAllSessions() {
        const selectAll = document.getElementById('select-all-sessions');
        const checkboxes = document.querySelectorAll('.session-checkbox'); // Apenas sessões não pagas
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll.checked;
        });
        
        this.updatePaymentSummary();
    },

    updatePaymentSummary() {
        const checkboxes = document.querySelectorAll('.session-checkbox:checked');
        const paymentValueInput = document.getElementById('valor_pago');
        
        let sessionsCount = checkboxes.length;
        let sessionsValue = 0;
        
        checkboxes.forEach(checkbox => {
            sessionsValue += parseFloat(checkbox.dataset.value) || 0;
        });
        
        // Preenchimento automático do valor quando sessões são selecionadas
        if (sessionsCount > 0) {
            paymentValueInput.value = sessionsValue.toFixed(2);
        } else {
            // Remove o valor quando nenhuma sessão está selecionada
            paymentValueInput.value = '';
        }
        
        const paymentValue = parseFloat(paymentValueInput.value) || 0;
        
        document.getElementById('summary-sessions').textContent = sessionsCount;
        document.getElementById('summary-sessions-value').textContent = window.app.formatCurrency(sessionsValue);
        document.getElementById('summary-payment-value').textContent = window.app.formatCurrency(paymentValue);
    },

    updateSelectedSessionsValue() {
        const checkboxes = document.querySelectorAll('.session-checkbox:checked');
        let totalValue = 0;
        
        checkboxes.forEach(checkbox => {
            totalValue += parseFloat(checkbox.dataset.value) || 0;
        });
        
        if (totalValue > 0) {
            document.getElementById('valor_pago').value = totalValue.toFixed(2);
        }
        
        this.updatePaymentSummary();
    },

    async savePayment() {
        const patientId = parseInt(document.getElementById('payment_patient_id').value);
        const dataPagamento = document.getElementById('data_pagamento').value;
        const valorPago = parseFloat(document.getElementById('valor_pago').value);
        const modalidadePagamento = document.getElementById('modalidade_pagamento').value;
        const observacoes = document.getElementById('observacoes_payment').value;
        
        const selectedSessions = Array.from(document.querySelectorAll('.session-checkbox:checked'))
            .map(checkbox => parseInt(checkbox.value));

        // Validation
        if (!patientId || !dataPagamento || !valorPago || selectedSessions.length === 0) {
            window.app.showError('Todos os campos obrigatórios devem ser preenchidos e pelo menos uma sessão deve ser selecionada');
            return;
        }

        const paymentData = {
            patient_id: patientId,
            data_pagamento: dataPagamento,
            valor_pago: valorPago,
            modalidade_pagamento: modalidadePagamento,
            observacoes: observacoes,
            session_ids: selectedSessions
        };

        try {
            let response;
            if (this.currentPayment) {
                // Update existing payment
                response = await window.app.apiCall(`/payments/${this.currentPayment.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(paymentData)
                });
            } else {
                // Create new payment
                response = await window.app.apiCall('/payments', {
                    method: 'POST',
                    body: JSON.stringify(paymentData)
                });
            }

            window.app.showSuccess(response.message);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            modal.hide();
            
            // Reload payments
            await this.loadPayments();
            
        } catch (error) {
            console.error('Erro ao salvar pagamento:', error);
            window.app.showError(error.message || 'Erro ao registrar pagamento');
        }
    },

    async quickPayment(sessionId) {
        const valorPago = prompt('Digite o valor do pagamento:');
        if (!valorPago || isNaN(valorPago) || parseFloat(valorPago) <= 0) {
            window.app.showError('Valor inválido');
            return;
        }

        try {
            const response = await window.app.apiCall('/payments/quick', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId,
                    valor_pago: parseFloat(valorPago)
                })
            });

            window.app.showSuccess(response.message);
            
            // Reload current view
            if (window.app.currentPage === 'payments') {
                await this.loadPayments();
            }
            
        } catch (error) {
            console.error('Error creating quick payment:', error);
            window.app.showError(error.message || 'Erro ao registrar pagamento');
        }
    },

    async viewPayment(paymentId) {
        try {
            const response = await window.app.apiCall(`/payments/${paymentId}`);
            const payment = response.data;
            
            this.showPaymentDetailsModal(payment);
        } catch (error) {
            console.error('Error loading payment details:', error);
            window.app.showError('Erro ao carregar detalhes do pagamento');
        }
    },

    showPaymentDetailsModal(payment) {
        const modalHtml = `
            <div class="modal fade" id="paymentDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-credit-card me-2"></i>
                                Detalhes do Pagamento
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <!-- Payment Info -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Informações do Pagamento</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="row mb-2">
                                                <div class="col-sm-4"><strong>Paciente:</strong></div>
                                                <div class="col-sm-8">${payment.patient_name}</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-4"><strong>Data:</strong></div>
                                                <div class="col-sm-8">${window.app.formatDate(payment.data_pagamento)}</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-4"><strong>Valor:</strong></div>
                                                <div class="col-sm-8 fw-bold text-success">${window.app.formatCurrency(payment.valor_pago)}</div>
                                            </div>
                                            ${payment.modalidade_pagamento ? `
                                                <div class="row mb-2">
                                                    <div class="col-sm-4"><strong>Modalidade:</strong></div>
                                                    <div class="col-sm-8"><span class="badge bg-info">${payment.modalidade_pagamento}</span></div>
                                                </div>
                                            ` : ''}
                                            ${payment.observacoes ? `
                                                <div class="row">
                                                    <div class="col-sm-4"><strong>Observações:</strong></div>
                                                    <div class="col-sm-8">${payment.observacoes}</div>
                                                </div>
                                            ` : ''}
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Patient Info -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Informações do Paciente</h6>
                                        </div>
                                        <div class="card-body">
                                            ${payment.patient ? `
                                                <div class="row mb-2">
                                                    <div class="col-sm-4"><strong>Email:</strong></div>
                                                    <div class="col-sm-8">${payment.patient.email}</div>
                                                </div>
                                                <div class="row mb-2">
                                                    <div class="col-sm-4"><strong>Telefone:</strong></div>
                                                    <div class="col-sm-8">${window.app.formatPhone(payment.patient.telefone)}</div>
                                                </div>
                                                <div class="row">
                                                    <div class="col-sm-4"><strong>CPF:</strong></div>
                                                    <div class="col-sm-8">${window.app.formatCPF(payment.patient.cpf)}</div>
                                                </div>
                                            ` : '<div class="text-muted">Carregando informações...</div>'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Sessions List -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Sessões Pagas</h6>
                                        </div>
                                        <div class="card-body">
                                            ${this.renderPaymentSessions(payment.sessions)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" onclick="Payments.editPayment(${payment.id})">
                                <i class="bi bi-pencil me-1"></i>Editar
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('paymentDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.getElementById('modals-container').innerHTML = modalHtml;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('paymentDetailsModal'));
        modal.show();
    },

    renderPaymentSessions(sessions) {
        if (!sessions || sessions.length === 0) {
            return '<div class="text-muted">Nenhuma sessão associada</div>';
        }

        return `
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Sessão</th>
                            <th>Data</th>
                            <th>Valor</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${sessions.map(session => `
                            <tr>
                                <td>Sessão ${session.numero_sessao}</td>
                                <td>${window.app.formatDateTime(session.data_sessao)}</td>
                                <td>${window.app.formatCurrency(session.valor)}</td>
                                <td><span class="status-badge status-${session.status}">${session.status}</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    async deletePayment(paymentId) {
        if (!confirm('Tem certeza que deseja excluir este pagamento? As sessões associadas voltarão ao status pendente.')) {
            return;
        }

        try {
            const response = await window.app.apiCall(`/payments/${paymentId}`, {
                method: 'DELETE'
            });

            window.app.showSuccess(response.message);
            await this.loadPayments();
            
        } catch (error) {
            console.error('Erro ao deletar pagamento:', error);
            window.app.showError(error.message || 'Erro ao excluir pagamento');
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.app && window.app.currentPage === 'payments') {
        window.Payments.init();
    }
});

