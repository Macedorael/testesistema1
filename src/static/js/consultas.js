// Appointments JavaScript
window.Appointments = {
    appointments: [],
    patients: [],

    currentAppointment: null,

    async init() {
        await this.loadPatients();
        await this.loadMedicos();
        await this.loadAppointments();
        this.setupEventListeners();
    },

    setupEventListeners() {
        // Filter functionality
        const appointmentFilter = document.getElementById('appointment-filter');
        const patientFilter = document.getElementById('patient-filter');
        
        if (appointmentFilter) {
            appointmentFilter.addEventListener('change', () => this.applyFilters());
        }
        
        if (patientFilter) {
            patientFilter.addEventListener('change', () => this.applyFilters());
        }
    },

    async loadPatients() {
        try {
            LoadingManager.show('appointments-loading', 'Carregando pacientes...');
            // Carregar apenas pacientes ativos para criação de agendamentos
            const response = await window.app.apiCall('/patients?only_active=1');
            this.patients = response.data || [];
            this.populatePatientFilters();
        } catch (error) {
            console.error('Error loading patients:', error);
        } finally {
            LoadingManager.hide('appointments-loading');
        }
    },

    async loadMedicos() {
        try {
            LoadingManager.show('appointments-loading', 'Carregando profissionais...');
            const response = await window.app.apiCall('/medicos');
            // O endpoint /medicos retorna uma lista diretamente, não um objeto com data
            this.medicos = Array.isArray(response) ? response : (response.data || []);
            console.log('Profissionais carregados:', this.medicos);
        } catch (error) {
            console.error('Error loading profissionais:', error);
            this.medicos = [];
        } finally {
            LoadingManager.hide('appointments-loading');
        }
    },



    populatePatientFilters() {
        const patientFilter = document.getElementById('patient-filter');
        if (patientFilter) {
            const options = (this.patients || []).map(patient => 
                `<option value="${patient.id}">${patient.nome_completo}${patient.ativo === false ? ' (Inativo)' : ''}</option>`
            ).join('');
            patientFilter.innerHTML = '<option value="">Todos os pacientes</option>' + options;
        }
    },

    async loadAppointments() {
        try {
            LoadingManager.show('appointments-loading', 'Carregando agendamentos...');
            const response = await window.app.apiCall('/appointments');
            this.appointments = response.data;
            this.renderAppointments(this.appointments);
        } catch (error) {
            console.error('Error loading appointments:', error);
            window.app.showError('Erro ao carregar agendamentos');
        } finally {
            LoadingManager.hide('appointments-loading');
        }
    },

    renderAppointments(appointments) {
        const container = document.getElementById('appointments-list');
        
        if (appointments.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-calendar-x fs-1 text-muted"></i>
                    <h4 class="text-muted mt-3">Nenhum agendamento encontrado</h4>
                    <p class="text-muted">Clique em "Novo Agendamento" para criar o primeiro agendamento.</p>
                </div>
            `;
            return;
        }

        const appointmentsHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Paciente</th>

                            <th>Primeira Sessão</th>
                            <th>Frequência</th>
                            <th>Sessões</th>
                            <th>Valor/Sessão</th>
                            <th>Total</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${appointments.map(appointment => {
                            const totalValue = appointment.quantidade_sessoes * appointment.valor_por_sessao;
                            return `
                                <tr>
                                    <td>
                                        <div class="fw-bold">${appointment.patient_name}</div>
                                        ${appointment.observacoes ? `<small class="text-muted">${appointment.observacoes.substring(0, 50)}${appointment.observacoes.length > 50 ? '...' : ''}</small>` : ''}
                                    </td>

                                    <td>${window.app.formatDateTime(appointment.data_primeira_sessao)}</td>
                                    <td>
                                        <span class="badge bg-secondary">${appointment.frequencia}</span>
                                    </td>
                                    <td>
                                        <span class="badge bg-primary">${appointment.quantidade_sessoes}</span>
                                        <small class="text-muted d-block">(${appointment.sessions_restantes || appointment.quantidade_sessoes} restantes)</small>
                                    </td>
                                    <td>${window.app.formatCurrency(appointment.valor_por_sessao)}</td>
                                    <td class="fw-bold">${window.app.formatCurrency(totalValue)}</td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <button class="btn btn-outline-primary" onclick="Appointments.viewAppointment(${appointment.id})" title="Ver detalhes">
                                                <i class="bi bi-eye"></i>
                                            </button>
                                            <button class="btn btn-outline-secondary" onclick="Appointments.editAppointment(${appointment.id})" title="Editar">
                                                <i class="bi bi-pencil"></i>
                                            </button>
                                            <button class="btn btn-outline-danger" onclick="Appointments.deleteAppointment(${appointment.id})" title="Excluir">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = appointmentsHtml;
    },

    applyFilters() {
        const appointmentFilter = document.getElementById('appointment-filter')?.value;
        const patientFilter = document.getElementById('patient-filter')?.value;
        
        let filtered = [...this.appointments];
        
        if (appointmentFilter) {
            const now = new Date();
            filtered = filtered.filter(appointment => {
                const firstSession = new Date(appointment.data_primeira_sessao);
                switch (appointmentFilter) {
                    case 'upcoming':
                        return firstSession >= now;
                    case 'completed':
                        return firstSession < now;
                    default:
                        return true;
                }
            });
        }
        
        if (patientFilter) {
            filtered = filtered.filter(appointment => 
                appointment.patient_id.toString() === patientFilter
            );
        }
        
        this.renderAppointments(filtered);
    },

    showCreateModal() {
        this.currentAppointment = null;
        this.showAppointmentModal();
    },

    showCreateModalForPatient(patientId) {
        this.currentAppointment = null;
        this.showAppointmentModal(patientId);
    },

    editAppointment(appointmentId) {
        this.currentAppointment = this.appointments.find(a => a.id === appointmentId);
        this.showAppointmentModal();
    },

    async showAppointmentModal(preselectedPatientId = null) {
        const isEdit = this.currentAppointment !== null;
        const title = isEdit ? 'Editar Agendamento' : 'Novo Agendamento';
        // Garantir que o paciente do agendamento (caso inativo) apareça no select ao editar
        if (isEdit && this.currentAppointment?.patient_id) {
            const exists = (this.patients || []).some(p => p.id === this.currentAppointment.patient_id);
            if (!exists) {
                try {
                    const resp = await window.app.apiCall(`/patients/${this.currentAppointment.patient_id}`);
                    if (resp && resp.data) {
                        const p = resp.data;
                        if (!this.patients) this.patients = [];
                        // Evitar duplicados
                        if (!this.patients.some(x => x.id === p.id)) this.patients.push(p);
                    }
                } catch (e) {
                    console.warn('Não foi possível carregar paciente inativo vinculado ao agendamento.', e);
                }
            }
        }
        
        const modalHtml = `
            <div class="modal fade" id="appointmentModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="appointmentForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="patient_id" class="form-label">Paciente *</label>
                                            <select class="form-select" id="patient_id" required>
                                                <option value="">Selecione um paciente</option>
                                                ${(this.patients || []).map(patient => `
                                                    <option value="${patient.id}" 
                                                        ${isEdit && this.currentAppointment.patient_id === patient.id ? 'selected' : ''}
                                                        ${preselectedPatientId === patient.id ? 'selected' : ''}>
                                                        ${patient.nome_completo}${patient.ativo === false ? ' (Inativo)' : ''}
                                                    </option>
                                                `).join('')}
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="funcionario_id" class="form-label">Profissional</label>
                                        <select class="form-select" id="funcionario_id">
                                            <option value="">Selecione um profissional</option>
                                                ${(this.medicos || []).map(medico => `
                                    <option value="${medico.id}" 
                                        ${isEdit && this.currentAppointment.funcionario_id === medico.id ? 'selected' : ''}>
                                        ${medico.nome} - ${medico.especialidade}
                                    </option>
                                `).join('')}
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-12">
                                        <div class="mb-3">
                                            <label for="data_primeira_sessao" class="form-label">Data/Hora da Primeira Sessão *</label>
                                            <input type="datetime-local" class="form-control" id="data_primeira_sessao" required
                                                value="${isEdit ? this.formatDateTimeForInput(this.currentAppointment.data_primeira_sessao) : ''}">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label for="quantidade_sessoes" class="form-label">Quantidade de Sessões *</label>
                                            <input type="number" class="form-control" id="quantidade_sessoes" required min="1" max="100"
                                                value="${isEdit ? this.currentAppointment.quantidade_sessoes : '8'}">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label for="frequencia" class="form-label">Frequência *</label>
                                            <select class="form-select" id="frequencia" required>
                                                <option value="semanal" ${isEdit && this.currentAppointment.frequencia === 'semanal' ? 'selected' : ''}>Semanal</option>
                                                <option value="quinzenal" ${isEdit && this.currentAppointment.frequencia === 'quinzenal' ? 'selected' : ''}>Quinzenal</option>
                                                <option value="mensal" ${isEdit && this.currentAppointment.frequencia === 'mensal' ? 'selected' : ''}>Mensal</option>
                                            </select>
                                            <div class="form-text">
                                                <small class="text-muted">
                                                    <i class="bi bi-info-circle me-1"></i>
                                                    <strong>Mensal:</strong> Mesmo dia da semana (ex: primeira segunda-feira do mês)
                                                </small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label for="valor_por_sessao" class="form-label">Valor por Sessão *</label>
                                            <div class="input-group">
                                                <span class="input-group-text">R$</span>
                                                <input type="number" class="form-control" id="valor_por_sessao" required min="0" step="0.01"
                                                    value="${isEdit ? this.currentAppointment.valor_por_sessao : '150.00'}">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="observacoes" class="form-label">Observações</label>
                                    <textarea class="form-control" id="observacoes" rows="3"
                                        placeholder="Observações sobre o agendamento...">${isEdit ? (this.currentAppointment.observacoes || '') : ''}</textarea>
                                </div>
                                
                                <!-- Preview -->
                                <div class="alert alert-info">
                                    <h6><i class="bi bi-info-circle me-1"></i>Resumo do Agendamento</h6>
                                    <div id="appointment-preview">
                                        <p class="mb-1"><strong>Total de sessões:</strong> <span id="preview-sessions">8</span></p>
                                        <p class="mb-1"><strong>Valor total:</strong> <span id="preview-total">R$ 1.200,00</span></p>
                                        <p class="mb-0"><strong>Última sessão:</strong> <span id="preview-last-date">-</span></p>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="Appointments.saveAppointment()">
                                ${isEdit ? 'Atualizar' : 'Salvar'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('appointmentModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.getElementById('modals-container').innerHTML = modalHtml;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('appointmentModal'));
        modal.show();

        // Setup preview updates
        this.setupAppointmentPreview();
    },

    setupAppointmentPreview() {
        const inputs = ['quantidade_sessoes', 'valor_por_sessao', 'data_primeira_sessao', 'frequencia'];
        
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('input', () => this.updateAppointmentPreview());
            }
        });
        
        // Initial preview
        this.updateAppointmentPreview();
    },

    updateAppointmentPreview() {
        const quantidade = parseInt(document.getElementById('quantidade_sessoes')?.value) || 0;
        const valor = parseFloat(document.getElementById('valor_por_sessao')?.value) || 0;
        const dataInicial = document.getElementById('data_primeira_sessao')?.value;
        const frequencia = document.getElementById('frequencia')?.value;
        
        // Update sessions count
        document.getElementById('preview-sessions').textContent = quantidade;
        
        // Update total value
        const total = quantidade * valor;
        document.getElementById('preview-total').textContent = window.app.formatCurrency(total);
        
        // Calculate last session date
        if (dataInicial && quantidade > 0) {
            const firstDate = new Date(dataInicial);
            let intervalDays = 7; // default weekly
            
            switch (frequencia) {
                case 'quinzenal':
                    intervalDays = 14;
                    break;
                case 'mensal':
                    intervalDays = 30;
                    break;
            }
            
            const lastDate = new Date(firstDate);
            lastDate.setDate(lastDate.getDate() + (quantidade - 1) * intervalDays);
            
            document.getElementById('preview-last-date').textContent = window.app.formatDateTime(lastDate.toISOString());
        } else {
            document.getElementById('preview-last-date').textContent = '-';
        }
    },

    // Utility functions for date handling
    formatDateTimeForInput(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toISOString().slice(0, 16);
    },

    formatDateForBrazilian(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    },

    parseBrazilianDate(dateStr) {
        // Convert DD/MM/YYYY to YYYY-MM-DD
        if (!dateStr) return '';
        
        // If already in ISO format, return as is
        if (dateStr.includes('-') && dateStr.length >= 10) {
            return dateStr;
        }
        
        // Parse DD/MM/YYYY format
        const parts = dateStr.split('/');
        if (parts.length === 3) {
            const [day, month, year] = parts;
            return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        }
        
        return dateStr;
    },

    async saveAppointment() {
        const funcionarioId = document.getElementById('funcionario_id').value;
        const appointmentData = {
            patient_id: parseInt(document.getElementById('patient_id').value),
            data_primeira_sessao: document.getElementById('data_primeira_sessao').value,
            quantidade_sessoes: parseInt(document.getElementById('quantidade_sessoes').value),
            frequencia: document.getElementById('frequencia').value,
            valor_por_sessao: parseFloat(document.getElementById('valor_por_sessao').value),
            observacoes: document.getElementById('observacoes').value
        };
        
        // Add funcionario_id if selected
        if (funcionarioId) {
            appointmentData.funcionario_id = parseInt(funcionarioId);
        }

        // Validation
        if (!appointmentData.patient_id || !appointmentData.data_primeira_sessao || 
            !appointmentData.quantidade_sessoes || !appointmentData.frequencia || 
            !appointmentData.valor_por_sessao) {
            window.app.showError('Todos os campos obrigatórios devem ser preenchidos');
            return;
        }

        // Show loading screen baseado no tipo de operação
        const loadingType = this.currentAppointment ? 'edit' : 'create';
        this.showLoadingScreen(loadingType);

        try {
            let response;
            if (this.currentAppointment) {
                // Update existing appointment
                response = await window.app.apiCall(`/appointments/${this.currentAppointment.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(appointmentData)
                });
            } else {
                // Create new appointment
                response = await window.app.apiCall('/appointments', {
                    method: 'POST',
                    body: JSON.stringify(appointmentData)
                });
            }

            window.app.showSuccess(response.message);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('appointmentModal'));
            modal.hide();
            
            // Reload appointments
            await this.loadAppointments();
            
        } catch (error) {
            console.error('Error saving appointment:', error);
            window.app.showError(error.message || 'Erro ao salvar agendamento');
        } finally {
            // Hide loading screen
            this.hideLoadingScreen();
        }
    },

    async viewAppointment(appointmentId) {
        try {
            const response = await window.app.apiCall(`/appointments/${appointmentId}`);
            const appointment = response.data;
            
            console.log('Dados do agendamento carregados:', appointment);
            console.log('funcionario_nome:', appointment.funcionario_nome);
            
            // Guardar sessões atuais para operações de edição inline
            this.currentAppointmentSessions = appointment.sessions || [];
            this.showAppointmentDetailsModal(appointment);
        } catch (error) {
            console.error('Error loading appointment details:', error);
            window.app.showError('Erro ao carregar detalhes do agendamento');
        }
    },

    showAppointmentDetailsModal(appointment) {
        // Store current appointment ID for easier access
        this.currentAppointmentId = appointment.id;
        
        const modalHtml = `
            <div class="modal fade" id="appointmentDetailsModal" tabindex="-1" data-appointment-id="${appointment.id}">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-calendar-check me-2"></i>
                                Agendamento - ${appointment.patient_name}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <!-- Appointment Info -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Informações do Agendamento</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="row mb-2">
                                                <div class="col-sm-5"><strong>Paciente:</strong></div>
                                                <div class="col-sm-7">${appointment.patient_name}</div>
                                            </div>
                                            ${appointment.funcionario_nome ? `
                                                <div class="row mb-2">
                                                    <div class="col-sm-5"><strong>Profissional:</strong></div>
                                                    <div class="col-sm-7"><span class="badge bg-info">${appointment.funcionario_nome}</span></div>
                                                </div>
                                            ` : ''}
                                            <div class="row mb-2">
                                                <div class="col-sm-5"><strong>Primeira Sessão:</strong></div>
                                                <div class="col-sm-7">${window.app.formatDateTime(appointment.data_primeira_sessao)}</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-5"><strong>Frequência:</strong></div>
                                                <div class="col-sm-7"><span class="badge bg-secondary">${appointment.frequencia}</span></div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-5"><strong>Quantidade:</strong></div>
                                                <div class="col-sm-7">${appointment.quantidade_sessoes} sessões</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-5"><strong>Valor/Sessão:</strong></div>
                                                <div class="col-sm-7">${window.app.formatCurrency(appointment.valor_por_sessao)}</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-5"><strong>Valor Total:</strong></div>
                                                <div class="col-sm-7 fw-bold text-primary">${window.app.formatCurrency(appointment.quantidade_sessoes * appointment.valor_por_sessao)}</div>
                                            </div>
                                            ${appointment.observacoes ? `
                                                <div class="row">
                                                    <div class="col-sm-5"><strong>Observações:</strong></div>
                                                    <div class="col-sm-7">${appointment.observacoes}</div>
                                                </div>
                                            ` : ''}
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Statistics -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Estatísticas</h6>
                                        </div>
                                        <div class="card-body">
                                            ${appointment.statistics ? `
                                                <div class="row mb-2">
                                                    <div class="col-sm-6"><strong>Realizadas:</strong></div>
                                                    <div class="col-sm-6">${appointment.statistics.sessions_realizadas}</div>
                                                </div>
                                                <div class="row mb-2">
                                                    <div class="col-sm-6"><strong>Pendentes:</strong></div>
                                                    <div class="col-sm-6">${appointment.statistics.sessions_pendentes}</div>
                                                </div>
                                            ` : '<div class="text-muted">Carregando estatísticas...</div>'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Legend between Info and Sessions -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <div class="alert alert-light border rounded py-2 px-3 mb-0">
                                        <div class="fw-semibold mb-1">Legenda de ações</div>
                                        <div class="d-flex flex-wrap gap-3 small">
                                            <span class="d-inline-flex align-items-center"><i class="bi bi-check text-success me-1"></i>Marcar como realizada</span>
                                            <span class="d-inline-flex align-items-center"><i class="bi bi-x text-warning me-1"></i>Marcar como falta</span>
                                            <span class="d-inline-flex align-items-center"><i class="bi bi-arrow-clockwise text-info me-1"></i>Reagendar sessão</span>
                                            <span class="d-inline-flex align-items-center"><i class="bi bi-journal-text text-primary me-1"></i>Pensamentos do período</span>
                                            <span class="d-inline-flex align-items-center"><i class="bi bi-card-text text-secondary me-1"></i>Observação da sessão</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Sessions List -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Sessões</h6>
                                        </div>
                                        <div class="card-body">
                                            ${this.renderSessionsList(appointment.sessions)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <div class="d-flex gap-2">
                                        <button class="btn btn-outline-secondary" onclick="Appointments.editAppointment(${appointment.id})">
                                            <i class="bi bi-pencil me-1"></i>Editar
                                        </button>
                                        <button class="btn btn-outline-primary" onclick="Appointments.resendConfirmationEmail(${appointment.id})">
                                            <i class="bi bi-envelope me-1"></i>Reenviar E-mail
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('appointmentDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.getElementById('modals-container').innerHTML = modalHtml;
        // Initialize tooltips inside the modal content
        try {
            document.querySelectorAll('#appointmentDetailsModal [data-bs-toggle="tooltip"]').forEach(el => {
                new bootstrap.Tooltip(el);
            });
        } catch (e) { /* ignore init errors */ }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('appointmentDetailsModal'));
        modal.show();
    },

    renderSessionsList(sessions) {
        if (!sessions || sessions.length === 0) {
            return '<div class="text-muted">Nenhuma sessão encontrada</div>';
        }

        // Ordenar sessões por data cronológica (data_sessao ou data_reagendamento se reagendada)
        const sortedSessions = [...sessions].sort((a, b) => {
            const dateA = new Date(a.data_sessao);
            const dateB = new Date(b.data_sessao);
            return dateA - dateB;
        });

        return `
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Data/Hora</th>
                            <th>Status</th>
                            <th>Pagamento</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${sortedSessions.map(session => `
                            <tr>
                                <td>${session.numero_sessao}</td>
                                <td>
                                    ${window.app.formatDateTime(session.data_sessao)}
                                    ${session.status === 'reagendada' && session.data_original ? 
                                        `<br><small class="text-muted">Original: ${window.app.formatDateTime(session.data_original)}</small>` : ''}
                                    ${session.observacoes ? 
                                        `<br><small class="text-secondary"><i class="bi bi-card-text"></i> ${session.observacoes}</small>` : ''}
                                </td>
                                <td><span class="status-badge status-${session.status}">${session.status}</span></td>
                                <td>
                                    ${(() => {
                                        try {
                                            const paid = session.status_pagamento === 'pago';
                                            const d = new Date(session.data_sessao);
                                            const today = new Date();
                                            const onlyDate = (dt) => new Date(dt.getFullYear(), dt.getMonth(), dt.getDate());
                                            const overdue = !paid && d && (onlyDate(d) < onlyDate(today)) && session.status !== 'cancelada';
                                            if (paid) return '<span class="badge rounded-pill bg-success">PAGA</span>';
                                            if (overdue) return '<span class="badge rounded-pill bg-danger">EM ATRASO</span>';
                                            return '<span class="badge rounded-pill bg-secondary">PENDENTE</span>';
                                        } catch (e) {
                                            return '<span class="badge rounded-pill bg-secondary">PENDENTE</span>';
                                        }
                                    })()}
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-success btn-sm" onclick="Appointments.updateSessionStatus(${session.id}, 'realizada')" title="Marcar como realizada">
                                            <i class="bi bi-check"></i>
                                        </button>
                                        <button class="btn btn-outline-warning btn-sm" onclick="Appointments.updateSessionStatus(${session.id}, 'faltou')" title="Marcar como falta">
                                            <i class="bi bi-x"></i>
                                        </button>
                                        <button class="btn btn-outline-info btn-sm" onclick="Appointments.updateSessionStatus(${session.id}, 'reagendada')" title="Marcar como reagendada">
                                            <i class="bi bi-arrow-clockwise"></i>
                                        </button>
                                        <button class="btn btn-outline-primary btn-sm" onclick="Appointments.showPeriodThoughts(${this.currentAppointmentId}, ${session.id})" title="Ver pensamentos do período">
                                            <i class="bi bi-journal-text"></i>
                                        </button>
                                        <button class="btn btn-outline-secondary btn-sm" onclick="Appointments.showSessionObservationModal(${session.id})" title="Adicionar/editar observação">
                                            <i class="bi bi-card-text"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },

    async updateSessionStatus(sessionId, status) {
        if (status === 'reagendada') {
            // Mostrar modal para inserir nova data
            this.showRescheduleModal(sessionId);
            return;
        }
        
        try {
            const response = await window.app.apiCall(`/sessions/${sessionId}`, {
                method: 'PUT',
                body: JSON.stringify({ status })
            });

            window.app.showSuccess(response.message);
            
            // Reload current appointment details if modal is open
            const modal = document.getElementById('appointmentDetailsModal');
            if (modal) {
                // Find appointment ID from the modal and reload
                // This is a simplified approach - in a real app you'd track this better
                window.location.reload();
            }
            
        } catch (error) {
            console.error('Error updating session status:', error);
            window.app.showError(error.message || 'Erro ao atualizar status da sessão');
        }
    },

    showRescheduleModal(sessionId) {
        const modalHtml = `
            <div class="modal fade" id="rescheduleModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-arrow-clockwise me-2"></i>
                                Reagendar Sessão
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="rescheduleForm">
                                <div class="mb-3">
                                    <label for="nova_data_sessao" class="form-label">Nova Data/Hora da Sessão *</label>
                                    <input type="datetime-local" class="form-control" id="nova_data_sessao" required>
                                    <div class="form-text">Selecione a nova data e horário para a sessão.</div>
                                </div>
                                <div class="mb-3">
                                    <label for="observacoes_reagendamento" class="form-label">Observações (opcional)</label>
                                    <textarea class="form-control" id="observacoes_reagendamento" rows="3"
                                        placeholder="Motivo do reagendamento ou outras observações..."></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="Appointments.confirmReschedule(${sessionId})">
                                Reagendar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('rescheduleModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.getElementById('modals-container').innerHTML = modalHtml;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('rescheduleModal'));
        modal.show();
    },

    async confirmReschedule(sessionId) {
        const novaDataSessaoInput = document.getElementById('nova_data_sessao');
        const observacoes = document.getElementById('observacoes_reagendamento').value;

        if (!novaDataSessaoInput.value) {
            window.app.showError('Nova data da sessão é obrigatória');
            return;
        }

        // O valor do datetime-local já está no formato correto YYYY-MM-DDTHH:MM
        const novaDataSessao = novaDataSessaoInput.value;

        try {
            const response = await window.app.apiCall(`/sessions/${sessionId}`, {
                method: 'PUT',
                body: JSON.stringify({ 
                    status: 'reagendada',
                    nova_data_sessao: novaDataSessao,
                    observacoes: observacoes
                })
            });

            window.app.showSuccess(response.message);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('rescheduleModal'));
            modal.hide();
            
            // Reload current appointment details if modal is open
            if (this.currentAppointmentId) {
                this.viewAppointment(this.currentAppointmentId);
            }
            
        } catch (error) {
            console.error('Error rescheduling session:', error);
            window.app.showError(error.message || 'Erro ao reagendar sessão');
        }
    },

    showSessionObservationModal(sessionId) {
        // Encontrar sessão atual para preencher observação existente
        const session = (this.currentAppointmentSessions || []).find(s => s.id === sessionId) || {};
        const existing = session.observacoes || '';

        const modalHtml = `
            <div class="modal fade" id="sessionObservationModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-card-text me-2"></i>
                                Observação da Sessão #${session.numero_sessao || ''}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="session_observacoes" class="form-label">Observação</label>
                                <textarea class="form-control" id="session_observacoes" rows="4" placeholder="Escreva observações sobre esta sessão...">${existing}</textarea>
                                <div class="form-text">Ex.: pontos discutidos, alertas, próximos passos.</div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="Appointments.confirmSessionObservation(${sessionId})">Salvar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remover modal existente
        const existingModal = document.getElementById('sessionObservationModal');
        if (existingModal) existingModal.remove();

        // Injetar e mostrar
        const container = document.getElementById('modals-container');
        if (container) {
            container.innerHTML = modalHtml;
            const modal = new bootstrap.Modal(document.getElementById('sessionObservationModal'));
            modal.show();
        } else {
            window.app.showError('Container de modais não encontrado');
        }
    },

    async confirmSessionObservation(sessionId) {
        const textarea = document.getElementById('session_observacoes');
        const texto = textarea ? textarea.value : '';

        try {
            const response = await window.app.apiCall(`/sessions/${sessionId}`, {
                method: 'PUT',
                body: JSON.stringify({ observacoes: texto })
            });

            window.app.showSuccess(response.message || 'Observação salva');

            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('sessionObservationModal'));
            if (modal) modal.hide();

            // Recarregar detalhes do agendamento para refletir alteração
            if (this.currentAppointmentId) {
                this.viewAppointment(this.currentAppointmentId);
            } else {
                window.location.reload();
            }
        } catch (error) {
            console.error('Error saving session observation:', error);
            window.app.showError(error.message || 'Erro ao salvar observação da sessão');
        }
    },

    async resendConfirmationEmail(appointmentId) {
        const appointment = this.appointments.find(a => a.id === appointmentId);
        if (!appointment) return;

        if (!confirm(`Reenviar e-mail de confirmação para o paciente "${appointment.patient_name}"?`)) {
            return;
        }

        try {
            const response = await window.app.apiCall(`/appointments/${appointmentId}/resend-email`, {
                method: 'POST'
            });

            window.app.showSuccess(response.message);
            
        } catch (error) {
            console.error('Error resending confirmation email:', error);
            window.app.showError(error.message || 'Erro ao reenviar e-mail de confirmação');
        }
    },

    async deleteAppointment(appointmentId) {
        const appointment = this.appointments.find(a => a.id === appointmentId);
        if (!appointment) return;

        if (!confirm(`Tem certeza que deseja excluir o agendamento do paciente "${appointment.patient_name}"?\n\nTodas as sessões relacionadas também serão excluídas.\nEsta ação não pode ser desfeita.`)) {
            return;
        }

        // Mostrar loading específico para exclusão
        this.showLoadingScreen('delete');

        try {
            const response = await window.app.apiCall(`/appointments/${appointmentId}`, {
                method: 'DELETE'
            });

            window.app.showSuccess(response.message);
            await this.loadAppointments();
            
        } catch (error) {
            console.error('Error deleting appointment:', error);
            window.app.showError(error.message || 'Erro ao excluir agendamento');
        } finally {
            // Esconder loading após operação
            this.hideLoadingScreen();
        }
    },

    showLoadingScreen(type = 'create') {
        // Remove existing loading screen if any
        this.hideLoadingScreen();
        
        // Definir mensagens baseadas no tipo de operação
        let title, message, spinnerColor;
        switch(type) {
            case 'delete':
                title = 'Excluindo Agendamento';
                message = 'Por favor, aguarde enquanto excluímos o agendamento...';
                spinnerColor = 'text-danger';
                break;
            case 'edit':
                title = 'Atualizando Agendamento';
                message = 'Por favor, aguarde enquanto atualizamos o agendamento...';
                spinnerColor = 'text-warning';
                break;
            case 'fetch':
                title = 'Carregando Pensamentos do Período';
                message = 'Por favor, aguarde enquanto buscamos os registros...';
                spinnerColor = 'text-primary';
                break;
            default:
                title = 'Processando Agendamento';
                message = 'Por favor, aguarde enquanto criamos seu agendamento...';
                spinnerColor = 'text-primary';
        }
        
        const loadingHtml = `
            <div id="appointment-loading-screen" class="position-fixed top-0 start-0 w-100 h-100" 
                 style="background-color: rgba(0, 0, 0, 0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
                <div class="bg-white rounded p-4 text-center" style="min-width: 300px;">
                    <div class="spinner-border ${spinnerColor} mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    <h5 class="mb-2">${title}</h5>
                    <p class="text-muted mb-0">${message}</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    },

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('appointment-loading-screen');
        if (loadingScreen) {
            loadingScreen.remove();
        }
    },

    async showPeriodThoughts(appointmentId, sessionId) {
        try {
            // Mostrar loading enquanto busca os dados
            this.showLoadingScreen('fetch');
            
            // Buscar dados da consulta para obter o patient_id
            const appointment = this.appointments.find(app => app.id === appointmentId) || { id: appointmentId };
            if (!appointment) {
                window.app.showError('Consulta não encontrada');
                return;
            }

            // Garantir que temos as sessões atuais do modal
            const modalEl = document.getElementById('appointmentDetailsModal');
            if (modalEl) {
                const modalAppointmentId = Number(modalEl.getAttribute('data-appointment-id'));
                if (modalAppointmentId === appointmentId) {
                    // Reusar dados renderizados no modal: extrair do HTML não é viável; confiar no appointment atual passado
                }
            }

            // Calcular período: da sessão anterior até a atual
            const sessions = appointment.sessions || [];
            const sortedSessions = [...sessions].sort((a, b) => new Date(a.data_sessao) - new Date(b.data_sessao));
            const currentSessionIndex = sortedSessions.findIndex(s => s.id === sessionId);
            
            if (currentSessionIndex === -1) {
                // Fallback: se não temos sessions anexadas ao objeto em memória, refazer o fetch do appointment
                try {
                    const fresh = await window.app.apiCall(`/appointments/${appointmentId}`);
                    appointment.patient_id = fresh.data.patient_id;
                    appointment.patient_name = fresh.data.patient_name;
                    const fsessions = fresh.data.sessions || [];
                    const sorted = [...fsessions].sort((a, b) => new Date(a.data_sessao) - new Date(b.data_sessao));
                    const idx = sorted.findIndex(s => s.id === sessionId);
                    if (idx === -1) {
                        throw new Error('Sessão não encontrada no agendamento');
                    }
                    const currentDate = new Date(sorted[idx].data_sessao);
                    let startDate;
                    if (idx > 0) {
                        startDate = new Date(sorted[idx - 1].data_sessao);
                    } else {
                        startDate = new Date(currentDate);
                        startDate.setDate(startDate.getDate() - 7);
                    }
                    const startDateStr = startDate.toISOString().split('T')[0];
                    const endDateStr = currentDate.toISOString().split('T')[0];
                    const response = await window.app.apiCall(`/patients/${fresh.data.patient_id}/diary-entries/period?start_date=${startDateStr}&end_date=${endDateStr}`);
                    this.showPeriodThoughtsModal(response.data, startDateStr, endDateStr, fresh.data.patient_name);
                    return;
                } finally {
                    this.hideLoadingScreen();
                }
            }

            let startDate;
            if (currentSessionIndex > 0) {
                // Usar data da sessão anterior
                startDate = new Date(sortedSessions[currentSessionIndex - 1].data_sessao);
            } else {
                // Para a primeira sessão, usar 7 dias antes
                const currentDate = new Date(sortedSessions[currentSessionIndex].data_sessao);
                startDate = new Date(currentDate);
                startDate.setDate(startDate.getDate() - 7);
            }

            // Formatar datas para a API (YYYY-MM-DD)
            const startDateStr = startDate.toISOString().split('T')[0];
            const endDateStr = new Date(sortedSessions[currentSessionIndex].data_sessao).toISOString().split('T')[0];

            // Fazer chamada para a API
            const response = await window.app.apiCall(`/patients/${appointment.patient_id}/diary-entries/period?start_date=${startDateStr}&end_date=${endDateStr}`);
            
            this.showPeriodThoughtsModal(response.data, startDateStr, endDateStr, appointment.patient_name);

        } catch (error) {
            console.error('Error loading period thoughts:', error);
            window.app.showError(error.message || 'Erro ao carregar pensamentos do período');
        } finally {
            this.hideLoadingScreen();
        }
    },

    showPeriodThoughtsModal(diaryEntries, startDate, endDate, patientName) {
        const modalHtml = `
            <div class="modal fade" id="periodThoughtsModal" tabindex="-1" aria-labelledby="periodThoughtsModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="periodThoughtsModalLabel">
                                <i class="bi bi-journal-text me-2"></i>
                                Pensamentos do Período - ${patientName}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <small class="text-muted">
                                    <i class="bi bi-calendar-range me-1"></i>
                                    Período: ${window.app.formatDate(startDate)} até ${window.app.formatDate(endDate)}
                                </small>
                            </div>
                            <div class="d-flex justify-content-end mb-2">
                              <button type="button" class="btn btn-outline-primary btn-sm" id="togglePeriodChartBtn">
                                <i class="bi bi-bar-chart"></i> Ver gráfico
                              </button>
                            </div>
                            <div id="periodChartContainer" class="mb-3 d-none">
                              ${this.renderDiaryChart(diaryEntries)}
                            </div>
                            ${this.renderDiaryEntries(diaryEntries)}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="bi bi-x-circle me-1"></i>
                                Fechar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove modal anterior se existir
        const existingModal = document.getElementById('periodThoughtsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Adiciona novo modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Mostra o modal
        const modal = new bootstrap.Modal(document.getElementById('periodThoughtsModal'));
        modal.show();

        // Toggle do gráfico
        const toggleBtn = document.getElementById('togglePeriodChartBtn');
        const chartContainer = document.getElementById('periodChartContainer');
        if (toggleBtn && chartContainer) {
            toggleBtn.addEventListener('click', () => {
                chartContainer.classList.toggle('d-none');
                toggleBtn.innerHTML = chartContainer.classList.contains('d-none')
                  ? '<i class="bi bi-pie-chart"></i> Ver gráfico'
                  : '<i class="bi bi-pie-chart"></i> Ocultar gráfico';

                // Desenhar gráfico de pizza (proporção por emoção) quando exibido
                if (!chartContainer.classList.contains('d-none')) {
                    const canvas = document.getElementById('periodEmotionChartCanvas');
                    const pie = this.computeEmotionPieData(diaryEntries);
                    this.drawEmotionPieChart(canvas, pie);
                }
            });
        }

        // Remove modal do DOM quando fechado
        document.getElementById('periodThoughtsModal').addEventListener('hidden.bs.modal', function () {
            this.remove();
        });
    },

    renderDiaryChart(entries) {
        if (!entries || entries.length === 0) {
            return `<div class="text-muted">Sem dados para o gráfico.</div>`;
        }
        const items = this.computeEmotionTimeSeries(entries);
        if (!items || items.length === 0) {
            return `<div class="text-muted">Sem dados de emoções.</div>`;
        }
        return `
          <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0"><i class="bi bi-pie-chart me-2"></i>Gráfico de Pizza de Emoções</h6>
              <small class="text-muted">Proporção por emoção (soma de intensidades 0–10)</small>
            </div>
            <div class="card-body">
              <canvas id="periodEmotionChartCanvas" width="720" height="320"></canvas>
              <div id="periodEmotionLegendBadges" class="mt-2">
                ${items.map(it => `<span class="badge bg-${it.color} me-1">${it.label}</span>`).join('')}
              </div>
            </div>
          </div>
        `;
    },
    computeEmotionTimeSeries(entries) {
        // Aggrega intensidade por emoção por dia
        const byEmotionDay = {};
        const addPoint = (emotionLabel, dayStr, intensity) => {
            const key = (emotionLabel || '').toLowerCase();
            if (!key) return;
            if (!byEmotionDay[key]) byEmotionDay[key] = { label: emotionLabel, color: this.getEmotionColor(emotionLabel), days: {} };
            if (!byEmotionDay[key].days[dayStr]) byEmotionDay[key].days[dayStr] = [];
            byEmotionDay[key].days[dayStr].push(Number(intensity) || 0);
        };

        entries.forEach(entry => {
            const dt = new Date(entry.data_registro || entry.created_at);
            if (isNaN(dt)) return;
            const dayStr = dt.toISOString().split('T')[0];
            const pairs = Array.isArray(entry.emocao_intensidades) ? entry.emocao_intensidades : [];
            if (pairs.length > 0) {
                pairs.forEach(p => addPoint(p.emocao, dayStr, p.intensidade));
            } else if (entry.emocao) {
                addPoint(entry.emocao, dayStr, entry.intensidade);
            }
        });

        // Converte em séries com média por dia
        const series = Object.values(byEmotionDay).map(group => {
            const points = Object.entries(group.days).map(([dayStr, vals]) => {
                const avg = vals.length ? vals.reduce((a,b)=>a+b,0) / vals.length : 0;
                return { x: new Date(dayStr + 'T00:00:00'), y: Math.max(0, Math.min(10, avg)) };
            }).sort((a,b) => a.x - b.x);
            return { label: group.label, color: group.color, points };
        }).filter(s => s.points.length > 0);

        return series;
    },

    // Dados para gráfico de pizza: proporção por emoção (soma de intensidades)
    computeEmotionPieData(entries) {
        const totals = new Map();
        const addVal = (emotionLabel, val) => {
            const emo = (emotionLabel || '').trim();
            if (!emo) return;
            const v = Number(val) || 0;
            totals.set(emo, (totals.get(emo) || 0) + Math.max(0, Math.min(10, v)));
        };

        entries.forEach(entry => {
            const pairs = Array.isArray(entry.emocao_intensidades) ? entry.emocao_intensidades : [];
            if (pairs.length > 0) {
                pairs.forEach(p => addVal(p.emocao, p.intensidade));
            } else if (entry.emocao) {
                addVal(entry.emocao, entry.intensidade);
            }
        });

        // Ordenar por maior intensidade total
        const sorted = Array.from(totals.entries()).sort((a,b)=>b[1]-a[1]);
        const labels = sorted.map(([emo]) => emo);
        const values = sorted.map(([,val]) => val);

        const total = values.reduce((s,v)=>s+v,0);
        return { labels, values, total };
    },

    // Resolve cor real de fundo a partir da classe Bootstrap (ou gera uma cor estável)
    resolveEmotionSliceColor(label) {
        try {
            const clsRaw = (typeof getEmotionColor === 'function') ? getEmotionColor(label) : null;
            const bgClass = clsRaw ? (clsRaw.includes('bg-') ? clsRaw : `bg-${clsRaw}`) : null;
            if (bgClass && typeof window !== 'undefined' && document && document.body) {
                const temp = document.createElement('span');
                temp.className = `badge ${bgClass}`;
                temp.style.position = 'absolute';
                temp.style.left = '-9999px';
                document.body.appendChild(temp);
                const color = window.getComputedStyle(temp).backgroundColor;
                document.body.removeChild(temp);
                if (color) return color;
            }
        } catch (_) {}
        // Fallback: paleta estável por hash do label
        const palette = ['#0d6efd','#dc3545','#198754','#ffc107','#6f42c1','#20c997','#fd7e14','#0dcaf0','#6610f2','#343a40','#6c757d'];
        let hash = 0;
        for (let i = 0; i < label.length; i++) {
            hash = ((hash << 5) - hash) + label.charCodeAt(i);
            hash |= 0;
        }
        return palette[Math.abs(hash) % palette.length];
    },

    drawEmotionPieChart(canvas, pie) {
        if (!canvas || !pie || !pie.values || pie.values.length === 0) return;
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        ctx.clearRect(0, 0, width, height);

        const margin = { left: 16, right: 220, top: 16, bottom: 16 };
        const chartW = width - margin.left - margin.right;
        const chartH = height - margin.top - margin.bottom;
        const radius = Math.min(chartW, chartH) / 2 - 4;
        const cx = margin.left + chartW / 2;
        const cy = margin.top + chartH / 2;

        const total = pie.total || pie.values.reduce((s,v)=>s+v,0);
        if (total <= 0) {
            ctx.fillStyle = '#6c757d';
            ctx.textAlign = 'center';
            ctx.font = '14px Arial';
            ctx.fillText('Sem dados suficientes para gráfico de pizza', cx, cy);
            return;
        }

        // Preparar cores por emoção (prioriza cores dos badges renderizados)
        const badgeColors = {};
        try {
            const legend = document.getElementById('periodEmotionLegendBadges');
            if (legend) {
                const nodes = legend.querySelectorAll('span.badge');
                nodes.forEach(el => {
                    const lbl = (el.textContent || '').trim();
                    const bg = window.getComputedStyle(el).backgroundColor;
                    if (lbl && bg) badgeColors[lbl] = bg;
                });
            }
        } catch (_) {}
        const sliceColors = pie.labels.map(lbl => badgeColors[lbl] || this.resolveEmotionSliceColor(lbl));

        // Desenhar fatias
        let start = -Math.PI / 2; // começar no topo
        pie.values.forEach((val, idx) => {
            const frac = val / total;
            const end = start + frac * Math.PI * 2;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, radius, start, end);
            ctx.closePath();
            ctx.fillStyle = sliceColors[idx] || '#0d6efd';
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1;
            ctx.stroke();
            start = end;
        });

        // Legenda ao lado direito
        const legendX = margin.left + chartW + 16;
        let legendY = margin.top + 4;
        ctx.font = '12px Arial';
        pie.labels.forEach((lbl, idx) => {
            const color = sliceColors[idx] || '#0d6efd';
            const val = pie.values[idx];
            const pct = ((val / total) * 100).toFixed(0) + '%';
            // swatch
            ctx.fillStyle = color;
            ctx.fillRect(legendX, legendY, 14, 14);
            // texto
            ctx.fillStyle = '#212529';
            ctx.textAlign = 'left';
            ctx.fillText(`${lbl} — ${pct}`, legendX + 20, legendY + 11);
            legendY += 18;
        });
    },

    renderDiaryEntries(entries) {
        if (!entries || entries.length === 0) {
            return `
                <div class="text-center py-4">
                    <i class="bi bi-journal-x text-muted" style="font-size: 3rem;"></i>
                    <p class="text-muted mt-2">Nenhum pensamento registrado neste período</p>
                </div>
            `;
        }

        return `
            <div class="diary-entries">
                ${entries.map(entry => {
                    const pairs = Array.isArray(entry.emocao_intensidades) ? entry.emocao_intensidades : [];
                    const maxIntensity = pairs.length > 0
                        ? Math.max(...pairs.map(p => Number(p.intensidade) || 0))
                        : (Number(entry.intensidade) || 0);
                    const emotionsBadges = pairs.length > 0
                        ? pairs.map(p => `
                            <span class="badge bg-${this.getEmotionColor(p.emocao)} me-2">${p.emocao || 'Emoção'}: ${p.intensidade || 0}</span>
                          `).join('')
                        : `<span class="badge bg-${this.getEmotionColor(entry.emocao)} me-2">${entry.emocao || 'Emoção'}: ${entry.intensidade || 0}</span>`;
                    return `
                    <div class="card mb-3">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div>
                                <i class="bi bi-calendar3 me-1"></i>
                                <strong>${window.app.formatDateTime(entry.data_registro)}</strong>
                            </div>
                            <span class="badge bg-danger rounded-pill">Intensidade máx: ${maxIntensity}</span>
                        </div>
                        <div class="card-body">
                            ${entry.situacao ? `
                                <div class="mb-2">
                                    <h6 class="card-subtitle mb-2 text-muted">
                                        <i class="bi bi-geo-alt me-1"></i>
                                        Situação
                                    </h6>
                                    <p class="card-text">${entry.situacao}</p>
                                </div>
                            ` : ''}
                            <div class="mb-2">
                                <h6 class="card-subtitle mb-2 text-muted">
                                    <i class="bi bi-chat-quote me-1"></i>
                                    Pensamento
                                </h6>
                                <p class="card-text">${entry.pensamento || 'Não informado'}</p>
                            </div>
                            <div class="mb-2">
                                <h6 class="card-subtitle mb-2 text-muted">
                                    <i class="bi bi-emoji-smile me-1"></i>
                                    Emoções
                                </h6>
                                <div>${emotionsBadges}</div>
                            </div>
                            <div class="mb-2">
                                <h6 class="card-subtitle mb-2 text-muted">
                                    <i class="bi bi-activity me-1"></i>
                                    Comportamento
                                </h6>
                                <p class="card-text">${entry.comportamento || 'Não informado'}</p>
                            </div>
                            ${entry.consequencia ? `
                                <div class="mb-2">
                                    <h6 class="card-subtitle mb-2 text-muted">
                                        <i class="bi bi-arrow-right-circle me-1"></i>
                                        Consequência
                                    </h6>
                                    <p class="card-text">${entry.consequencia}</p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `}).join('')}
            </div>
        `;
    },

    getEmotionColor(emotion) {
        const emotionColors = {
            'alegria': 'success',
            'tristeza': 'primary',
            'raiva': 'danger',
            'medo': 'warning',
            'ansiedade': 'info',
            'nojo': 'secondary',
            'surpresa': 'light'
        };
        return emotionColors[emotion?.toLowerCase()] || 'secondary';
    }
};

