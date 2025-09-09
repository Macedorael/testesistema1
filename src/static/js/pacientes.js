// Patients JavaScript
window.Patients = {
    patients: [],
    currentPatient: null,

    async init() {
        await this.loadPatients();
        this.setupEventListeners();
    },

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('patient-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterPatients(e.target.value);
            });
        }
    },

    async loadPatients() {
        try {
            // Mostrar loading
            LoadingManager.show('patients-loading', 'Carregando pacientes...');
            
            const response = await window.app.apiCall('/patients');
            this.patients = response.data;
            this.renderPatients(this.patients);
        } catch (error) {
            console.error('Error loading patients:', error);
            window.app.showError('Erro ao carregar pacientes');
        } finally {
            // Esconder loading
            LoadingManager.hide('patients-loading');
        }
    },

    renderPatients(patients) {
        const container = document.getElementById('patients-list');
        
        if (patients.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-people fs-1 text-muted"></i>
                    <h4 class="text-muted mt-3">Nenhum paciente encontrado</h4>
                    <p class="text-muted">Clique em "Novo Paciente" para adicionar o primeiro paciente.</p>
                </div>
            `;
            return;
        }

        const patientsHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Telefone</th>
                            <th>Email</th>
                            <th>Data Nascimento</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${patients.map(patient => `
                            <tr>
                                <td>
                                    <div class="fw-bold">${patient.nome_completo}</div>
                                    ${patient.observacoes ? `<small class="text-muted">${patient.observacoes.substring(0, 50)}${patient.observacoes.length > 50 ? '...' : ''}</small>` : ''}
                                </td>
                                <td>${window.app.formatPhone(patient.telefone)}</td>
                                <td>${patient.email}</td>
                                <td>${window.app.formatDate(patient.data_nascimento)}</td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="Patients.viewPatient(${patient.id})" title="Ver detalhes">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-secondary" onclick="Patients.editPatient(${patient.id})" title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-outline-danger" onclick="Patients.deletePatient(${patient.id})" title="Excluir">
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

        container.innerHTML = patientsHtml;
    },

    filterPatients(searchTerm) {
        if (!searchTerm) {
            this.renderPatients(this.patients);
            return;
        }

        const filtered = this.patients.filter(patient => 
            patient.nome_completo.toLowerCase().includes(searchTerm.toLowerCase()) ||
            patient.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            patient.telefone.includes(searchTerm)
        );

        this.renderPatients(filtered);
    },

    showCreateModal() {
        this.currentPatient = null;
        this.showPatientModal();
    },

    editPatient(patientId) {
        this.currentPatient = this.patients.find(p => p.id === patientId);
        this.showPatientModal();
    },

    showPatientModal() {
        const isEdit = this.currentPatient !== null;
        const title = isEdit ? 'Editar Paciente' : 'Novo Paciente';
        
        const modalHtml = `
            <div class="modal fade" id="patientModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="patientForm">
                                <!-- Dados Pessoais -->
                                <h6 class="mb-3 text-primary">
                                    <i class="bi bi-person-circle me-2"></i>Dados Pessoais
                                </h6>
                                
                                <div class="row">
                                    <div class="col-md-8">
                                        <div class="mb-3">
                                            <label for="nome_completo" class="form-label">Nome Completo *</label>
                                            <input type="text" class="form-control" id="nome_completo" required
                                                value="${isEdit ? this.currentPatient.nome_completo : ''}">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label for="data_nascimento" class="form-label">Data de Nascimento *</label>
                                            <input type="date" class="form-control" id="data_nascimento" required
                                                value="${isEdit ? this.currentPatient.data_nascimento : ''}">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="telefone" class="form-label">Telefone *</label>
                                    <input type="tel" class="form-control" id="telefone" required
                                        value="${isEdit ? this.currentPatient.telefone : ''}"
                                        placeholder="(11) 99999-9999">
                                </div>
                                
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email *</label>
                                    <input type="email" class="form-control" id="email" required
                                        value="${isEdit ? this.currentPatient.email : ''}"
                                        placeholder="paciente@email.com">
                                </div>
                                
                                <!-- Contato de Emergência -->
                                <hr class="my-4">
                                <h6 class="mb-3 text-warning">
                                    <i class="bi bi-telephone-plus me-2"></i>Contato de Emergência
                                </h6>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="nome_contato_emergencia" class="form-label">Nome do Contato</label>
                                            <input type="text" class="form-control" id="nome_contato_emergencia"
                                                value="${isEdit ? (this.currentPatient.nome_contato_emergencia || '') : ''}"
                                                placeholder="Nome completo do contato">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="telefone_contato_emergencia" class="form-label">Telefone do Contato</label>
                                            <input type="tel" class="form-control" id="telefone_contato_emergencia"
                                                value="${isEdit ? (this.currentPatient.telefone_contato_emergencia || '') : ''}"
                                                placeholder="(11) 99999-9999">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="grau_parentesco_emergencia" class="form-label">Grau de Parentesco</label>
                                    <select class="form-select" id="grau_parentesco_emergencia">
                                        <option value="">Selecione o grau de parentesco</option>
                                        <option value="mãe" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'mãe' ? 'selected' : ''}>Mãe</option>
                                        <option value="pai" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'pai' ? 'selected' : ''}>Pai</option>
                                        <option value="irmão" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'irmão' ? 'selected' : ''}>Irmão</option>
                                        <option value="irmã" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'irmã' ? 'selected' : ''}>Irmã</option>
                                        <option value="cônjuge" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'cônjuge' ? 'selected' : ''}>Cônjuge</option>
                                        <option value="filho" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'filho' ? 'selected' : ''}>Filho</option>
                                        <option value="filha" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'filha' ? 'selected' : ''}>Filha</option>
                                        <option value="avô" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'avô' ? 'selected' : ''}>Avô</option>
                                        <option value="avó" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'avó' ? 'selected' : ''}>Avó</option>
                                        <option value="tio" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'tio' ? 'selected' : ''}>Tio</option>
                                        <option value="tia" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'tia' ? 'selected' : ''}>Tia</option>
                                        <option value="primo" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'primo' ? 'selected' : ''}>Primo</option>
                                        <option value="prima" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'prima' ? 'selected' : ''}>Prima</option>
                                        <option value="amigo" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'amigo' ? 'selected' : ''}>Amigo</option>
                                        <option value="amiga" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'amiga' ? 'selected' : ''}>Amiga</option>
                                        <option value="outro" ${isEdit && this.currentPatient.grau_parentesco_emergencia === 'outro' ? 'selected' : ''}>Outro</option>
                                    </select>
                                </div>
                                
                                <!-- Observações -->
                                <hr class="my-4">
                                <div class="mb-3">
                                    <label for="observacoes" class="form-label">Observações</label>
                                    <textarea class="form-control" id="observacoes" rows="3"
                                        placeholder="Observações sobre o paciente...">${isEdit ? (this.currentPatient.observacoes || '') : ''}</textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="Patients.savePatient()">
                                ${isEdit ? 'Atualizar' : 'Salvar'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('patientModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.getElementById('modals-container').innerHTML = modalHtml;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('patientModal'));
        modal.show();

        // Setup form masks
        this.setupFormMasks();
    },

    setupFormMasks() {
        // Phone mask for patient
        const phoneInput = document.getElementById('telefone');
        if (phoneInput) {
            phoneInput.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
                value = value.replace(/(\d{5})(\d)/, '$1-$2');
                e.target.value = value;
            });
        }

        // Phone mask for emergency contact
        const emergencyPhoneInput = document.getElementById('telefone_contato_emergencia');
        if (emergencyPhoneInput) {
            emergencyPhoneInput.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
                value = value.replace(/(\d{5})(\d)/, '$1-$2');
                e.target.value = value;
            });
        }
    },

    async savePatient() {
        const form = document.getElementById('patientForm');
        
        const patientData = {
            nome_completo: document.getElementById('nome_completo').value,
            telefone: document.getElementById('telefone').value,
            email: document.getElementById('email').value,
            data_nascimento: document.getElementById('data_nascimento').value,
            observacoes: document.getElementById('observacoes').value,
            nome_contato_emergencia: document.getElementById('nome_contato_emergencia').value,
            telefone_contato_emergencia: document.getElementById('telefone_contato_emergencia').value,
            grau_parentesco_emergencia: document.getElementById('grau_parentesco_emergencia').value
        };

        // Validation
        if (!patientData.nome_completo || !patientData.telefone || !patientData.email || 
            !patientData.data_nascimento) {
            window.app.showError('Todos os campos obrigatórios devem ser preenchidos');
            return;
        }

        try {
            let response;
            if (this.currentPatient) {
                // Update existing patient
                response = await window.app.apiCall(`/patients/${this.currentPatient.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(patientData)
                });
            } else {
                // Create new patient
                response = await window.app.apiCall('/patients', {
                    method: 'POST',
                    body: JSON.stringify(patientData)
                });
            }

            window.app.showSuccess(response.message);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('patientModal'));
            modal.hide();
            
            // Reload patients
            await this.loadPatients();
            
        } catch (error) {
            console.error('Error saving patient:', error);
            window.app.showError(error.message || 'Erro ao salvar paciente');
        }
    },

    async viewPatient(patientId) {
        try {
            const response = await window.app.apiCall(`/patients/${patientId}`);
            const patient = response.data;
            
            this.showPatientDetailsModal(patient);
        } catch (error) {
            console.error('Error loading patient details:', error);
            window.app.showError('Erro ao carregar detalhes do paciente');
        }
    },

    showPatientDetailsModal(patient) {
        const modalHtml = `
            <div class="modal fade" id="patientDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-person-circle me-2"></i>
                                ${patient.nome_completo}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <!-- Patient Info -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Informações Pessoais</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="row mb-2">
                                                <div class="col-sm-4"><strong>Nome:</strong></div>
                                                <div class="col-sm-8">${patient.nome_completo}</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-4"><strong>Email:</strong></div>
                                                <div class="col-sm-8">${patient.email}</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-4"><strong>Telefone:</strong></div>
                                                <div class="col-sm-8">${window.app.formatPhone(patient.telefone)}</div>
                                            </div>
                                            <div class="row mb-2">
                                                <div class="col-sm-4"><strong>Nascimento:</strong></div>
                                                <div class="col-sm-8">${window.app.formatDate(patient.data_nascimento)}</div>
                                            </div>
                                            ${patient.observacoes ? `
                                                <div class="row">
                                                    <div class="col-sm-4"><strong>Observações:</strong></div>
                                                    <div class="col-sm-8">${patient.observacoes}</div>
                                                </div>
                                            ` : ''}
                                        </div>
                                    </div>
                                    
                                    <!-- Emergency Contact -->
                                    ${patient.nome_contato_emergencia || patient.telefone_contato_emergencia || patient.grau_parentesco_emergencia ? `
                                        <div class="card mt-3">
                                            <div class="card-header">
                                                <h6 class="mb-0 text-warning">
                                                    <i class="bi bi-telephone-plus me-2"></i>Contato de Emergência
                                                </h6>
                                            </div>
                                            <div class="card-body">
                                                ${patient.nome_contato_emergencia ? `
                                                    <div class="row mb-2">
                                                        <div class="col-sm-4"><strong>Nome:</strong></div>
                                                        <div class="col-sm-8">${patient.nome_contato_emergencia}</div>
                                                    </div>
                                                ` : ''}
                                                ${patient.telefone_contato_emergencia ? `
                                                    <div class="row mb-2">
                                                        <div class="col-sm-4"><strong>Telefone:</strong></div>
                                                        <div class="col-sm-8">${window.app.formatPhone(patient.telefone_contato_emergencia)}</div>
                                                    </div>
                                                ` : ''}
                                                ${patient.grau_parentesco_emergencia ? `
                                                    <div class="row">
                                                        <div class="col-sm-4"><strong>Parentesco:</strong></div>
                                                        <div class="col-sm-8">${patient.grau_parentesco_emergencia}</div>
                                                    </div>
                                                ` : ''}
                                            </div>
                                        </div>
                                    ` : ''}
                                </div>
                                
                                <!-- Statistics -->
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Estatísticas</h6>
                                        </div>
                                        <div class="card-body">
                                            ${patient.statistics ? `
                                                <div class="row mb-2">
                                                    <div class="col-sm-6"><strong>Agendamentos:</strong></div>
                                                    <div class="col-sm-6">${patient.statistics.total_appointments}</div>
                                                </div>
                                                <div class="row mb-2">
                                                    <div class="col-sm-6"><strong>Total de Sessões:</strong></div>
                                                    <div class="col-sm-6">${patient.statistics.total_sessions}</div>
                                                </div>
                                                <div class="row mb-2">
                                                    <div class="col-sm-6"><strong>Realizadas:</strong></div>
                                                    <div class="col-sm-6">${patient.statistics.sessions_realizadas}</div>
                                                </div>
                                                <div class="row mb-2">
                                                    <div class="col-sm-6"><strong>Pendentes:</strong></div>
                                                    <div class="col-sm-6">${patient.statistics.sessions_pendentes}</div>
                                                </div>
                                                <div class="row mb-2">
                                                    <div class="col-sm-6"><strong>Total Pago:</strong></div>
                                                    <div class="col-sm-6 text-success fw-bold">${window.app.formatCurrency(patient.statistics.total_pago)}</div>
                                                </div>
                                                <div class="row">
                                                    <div class="col-sm-6"><strong>A Receber:</strong></div>
                                                    <div class="col-sm-6 text-warning fw-bold">${window.app.formatCurrency(patient.statistics.total_a_receber)}</div>
                                                </div>
                                            ` : '<div class="text-muted">Carregando estatísticas...</div>'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <div class="d-flex gap-2">
                                        <button class="btn btn-primary" onclick="Appointments.showCreateModalForPatient(${patient.id})">
                                            <i class="bi bi-calendar-plus me-1"></i>Novo Agendamento
                                        </button>
                                        <button class="btn btn-outline-secondary" onclick="Patients.editPatient(${patient.id})">
                                            <i class="bi bi-pencil me-1"></i>Editar
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
        const existingModal = document.getElementById('patientDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.getElementById('modals-container').innerHTML = modalHtml;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('patientDetailsModal'));
        modal.show();
    },

    async deletePatient(patientId) {
        const patient = this.patients.find(p => p.id === patientId);
        if (!patient) return;

        if (!confirm(`Tem certeza que deseja excluir o paciente "${patient.nome_completo}"?\n\nEsta ação não pode ser desfeita.`)) {
            return;
        }

        try {
            const response = await window.app.apiCall(`/patients/${patientId}`, {
                method: 'DELETE'
            });

            window.app.showSuccess(response.message);
            await this.loadPatients();
            
        } catch (error) {
            console.error('Error deleting patient:', error);
            window.app.showError(error.message || 'Erro ao excluir paciente');
        }
    }
};


