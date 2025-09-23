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
            const response = await window.app.apiCall('/patients');
            this.patients = response.data;
            this.populatePatientFilters();
        } catch (error) {
            console.error('Error loading patients:', error);
        } finally {
            LoadingManager.hide('appointments-loading');
        }
    },

    async loadMedicos() {
        try {
            LoadingManager.show('appointments-loading', 'Carregando médicos...');
            const response = await window.app.apiCall('/medicos');
            // O endpoint /medicos retorna uma lista diretamente, não um objeto com data
            this.medicos = Array.isArray(response) ? response : (response.data || []);
            console.log('Médicos carregados:', this.medicos);
        } catch (error) {
            console.error('Error loading médicos:', error);
            this.medicos = [];
        } finally {
            LoadingManager.hide('appointments-loading');
        }
    },



    populatePatientFilters() {
        const patientFilter = document.getElementById('patient-filter');
        if (patientFilter) {
            const options = this.patients.map(patient => 
                `<option value="${patient.id}">${patient.nome_completo}</option>`
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

    showAppointmentModal(preselectedPatientId = null) {
        const isEdit = this.currentAppointment !== null;
        const title = isEdit ? 'Editar Agendamento' : 'Novo Agendamento';
        
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
                                                ${this.patients.map(patient => `
                                                    <option value="${patient.id}" 
                                                        ${isEdit && this.currentAppointment.patient_id === patient.id ? 'selected' : ''}
                                                        ${preselectedPatientId === patient.id ? 'selected' : ''}>
                                                        ${patient.nome_completo}
                                                    </option>
                                                `).join('')}
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="funcionario_id" class="form-label">Médico</label>
                                        <select class="form-select" id="funcionario_id">
                                            <option value="">Selecione um médico</option>
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
                                                    <div class="col-sm-5"><strong>Médico:</strong></div>
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
                                    ${session.observacoes_reagendamento ? 
                                        `<br><small class="text-info"><i class="bi bi-info-circle"></i> ${session.observacoes_reagendamento}</small>` : ''}
                                </td>
                                <td><span class="status-badge status-${session.status}">${session.status}</span></td>
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
    }
};

