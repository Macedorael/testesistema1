// Patients JavaScript
window.Patients = {
    patients: [],
    currentPatient: null,
    isSaving: false,

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
                                    <div class="fw-bold d-flex align-items-center gap-2">
                                        <span>${patient.nome_completo}</span>
                                        ${patient.ativo === false ? '<span class="badge bg-secondary">Inativo</span>' : '<span class="badge bg-success">Ativo</span>'}
                                    </div>
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
                                        ${patient.ativo === false
                                            ? `<button class="btn btn-outline-danger btn-toggle-status" onclick="Patients.toggleActive(${patient.id}, true)" title="Ativar">
                                                    <i class="bi bi-toggle2-off text-danger"></i>
                                               </button>`
                                            : `<button class="btn btn-outline-success btn-toggle-status" onclick="Patients.toggleActive(${patient.id}, false)" title="Inativar">
                                                    <i class="bi bi-toggle2-on text-success"></i>
                                               </button>`}
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
                                        placeholder="(21) 99999-9999">
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
                                                placeholder="(21) 99999-9999">
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
                            <button id="savePatientBtn" type="button" class="btn btn-primary" onclick="Patients.savePatient()">
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
        if (this.isSaving) return; // evita cliques repetidos
        const saveBtn = document.getElementById('savePatientBtn');
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.dataset.originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Salvando...';
        }
        this.isSaving = true;
        const form = document.getElementById('patientForm');
        if (form && !form.reportValidity()) {
            // Restabelece estado do botão se validação falhar
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = saveBtn.dataset.originalText || 'Salvar';
            }
            this.isSaving = false;
            return;
        }
        
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
        } finally {
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = saveBtn.dataset.originalText || 'Salvar';
            }
            this.isSaving = false;
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
        const statusBadge = (patient.ativo === false)
            ? '<span class="badge bg-secondary ms-2">Inativo</span>'
            : '<span class="badge bg-success ms-2">Ativo</span>';
        const modalHtml = `
            <div class="modal fade" id="patientDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-person-circle me-2"></i>
                                ${patient.nome_completo}
                                ${statusBadge}
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
                                            ` : '<div class="text-muted">Carregando estatísticas...</div>'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <div class="d-flex flex-wrap gap-2">
                                        <button class="btn btn-outline-primary btn-sm" ${patient.ativo === false ? 'disabled' : ''} onclick="Appointments.showCreateModalForPatient(${patient.id})">
                                            <i class="bi bi-calendar-plus me-1"></i>Novo Agendamento
                                        </button>
                                        ${patient.diario_tcc_ativo ? `
                                            <button class="btn btn-outline-primary btn-sm" onclick="Patients.viewDiaryEntries(${patient.id})">
                                                <i class="bi bi-journal-text me-1"></i>Ver todos os pensamentos
                                            </button>
                                            <button class="btn btn-outline-primary btn-sm" onclick="Patients.showEmotionsChart(${patient.id})">
                                                <i class="bi bi-graph-up-arrow me-1"></i>Gráfico de Emoções
                                            </button>
                                        ` : ''}
                                        ${patient.diario_tcc_ativo
                                            ? `<button class="btn btn-warning btn-sm" onclick="Patients.toggleCbtDiary(${patient.id}, false)">
                                                    <i class="bi bi-journal-x me-1"></i>Desativar Diário TCC
                                               </button>`
                                            : `<button class="btn btn-success btn-sm" onclick="Patients.toggleCbtDiary(${patient.id}, true)">
                                                    <i class="bi bi-journal-check me-1"></i>Ativar Diário TCC
                                               </button>`}
                                        ${patient.ativo === false
                                            ? `<button class="btn btn-outline-danger btn-toggle-status btn-sm" onclick="Patients.toggleActive(${patient.id}, true)">
                                                    <i class="bi bi-toggle2-off text-danger me-1"></i>Ativar
                                               </button>`
                                            : `<button class="btn btn-outline-success btn-toggle-status btn-sm" onclick="Patients.toggleActive(${patient.id}, false)">
                                                    <i class="bi bi-toggle2-on text-success me-1"></i>Inativar
                                               </button>`}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-outline-secondary" onclick="Patients.editPatient(${patient.id})">
                                <i class="bi bi-pencil me-1"></i>Editar
                            </button>
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

    async toggleCbtDiary(patientId, newState) {
        try {
            const patient = this.patients.find(p => p.id === patientId);
            const name = patient ? patient.nome_completo : 'o paciente';
            const actionText = newState ? 'ativar' : 'desativar';
            if (!confirm(`Tem certeza que deseja ${actionText} o Diário TCC de ${name}?`)) {
                return;
            }
            const resp = await window.app.apiCall(`/patients/${patientId}/toggle-cbt-diary`, {
                method: 'POST',
                body: JSON.stringify({ ativo: !!newState })
            });
            window.app.showSuccess('Diário TCC atualizado');
            // Recarregar lista
            await this.loadPatients();
            // Se o modal de detalhes estiver aberto, atualizar seu conteúdo
            const openModal = document.getElementById('patientDetailsModal');
            if (openModal) {
                try {
                    const fresh = await window.app.apiCall(`/patients/${patientId}`);
                    this.showPatientDetailsModal(fresh.data);
                } catch (_) {}
            }
        } catch (error) {
            console.error('Erro ao atualizar Diário TCC:', error);
            window.app.showError(error.message || 'Erro ao atualizar Diário TCC');
        }
    },

    async toggleActive(patientId, newStatus) {
        try {
            const patient = this.patients.find(p => p.id === patientId);
            const name = patient ? patient.nome_completo : 'o paciente';
            const actionText = newStatus ? 'ativar' : 'desativar';
            if (!confirm(`Tem certeza que deseja ${actionText} ${name}?`)) {
                return;
            }
            const resp = await window.app.apiCall(`/patients/${patientId}/status`, {
                method: 'PATCH',
                body: JSON.stringify({ ativo: !!newStatus })
            });
            window.app.showSuccess(resp.message || 'Status atualizado');
            // Recarregar lista
            await this.loadPatients();
            // Se o modal de detalhes estiver aberto, atualizar elementos em tempo real (sem reabrir)
            const openModal = document.getElementById('patientDetailsModal');
            if (openModal) {
                // Atualiza badge de status no título
                const badgeEl = openModal.querySelector('.modal-title .badge');
                if (badgeEl) {
                    if (newStatus) {
                        badgeEl.classList.remove('bg-secondary');
                        badgeEl.classList.add('bg-success');
                        badgeEl.textContent = 'Ativo';
                    } else {
                        badgeEl.classList.remove('bg-success');
                        badgeEl.classList.add('bg-secondary');
                        badgeEl.textContent = 'Inativo';
                    }
                }

                // Atualiza botão de novo agendamento (habilita somente quando ativo)
                const novoAgendamentoBtnIcon = openModal.querySelector('.modal-body i.bi-calendar-plus');
                const novoAgendamentoBtn = novoAgendamentoBtnIcon ? novoAgendamentoBtnIcon.closest('button') : null;
                if (novoAgendamentoBtn) {
                    novoAgendamentoBtn.disabled = !newStatus;
                }

                // Atualiza botão de ativar/inativar dentro da área de ações
                const actionsContainer = openModal.querySelector('.modal-body .d-flex.gap-2');
                if (actionsContainer) {
                    const currentToggleIcon = actionsContainer.querySelector('i.bi-toggle2-on, i.bi-toggle2-off');
                    const toggleBtn = currentToggleIcon ? currentToggleIcon.closest('button') : null;
                    if (toggleBtn) {
                        if (newStatus) {
                            // Paciente ficou ativo: botão verde e ícone verde
                            toggleBtn.classList.remove('btn-outline-danger');
                            toggleBtn.classList.add('btn-outline-success');
                            toggleBtn.classList.add('btn-toggle-status');
                            toggleBtn.innerHTML = '<i class="bi bi-toggle2-on text-success me-1"></i>Inativar';
                            toggleBtn.setAttribute('onclick', `Patients.toggleActive(${patientId}, false)`);
                        } else {
                            // Paciente ficou inativo: botão vermelho e ícone vermelho
                            toggleBtn.classList.remove('btn-outline-success');
                            toggleBtn.classList.add('btn-outline-danger');
                            toggleBtn.classList.add('btn-toggle-status');
                            toggleBtn.innerHTML = '<i class="bi bi-toggle2-off text-danger me-1"></i>Ativar';
                            toggleBtn.setAttribute('onclick', `Patients.toggleActive(${patientId}, true)`);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao atualizar status do paciente:', error);
            window.app.showError(error.message || 'Erro ao atualizar status do paciente');
        }
    },

    async viewDiaryEntries(patientId) {
        try {
            const response = await window.app.apiCall(`/patients/${patientId}/diary-entries`);
            const entries = response.data || [];
            const patient = this.patients.find(p => p.id === patientId);
            this.showDiaryEntriesModal(patient, entries);
        } catch (error) {
            console.error('Erro ao carregar pensamentos:', error);
            window.app.showError('Erro ao carregar pensamentos do paciente');
        }
    },

    showDiaryEntriesModal(patient, entries) {
        const patientName = patient ? patient.nome_completo : 'Paciente';
        const modalHtml = `
            <div class="modal fade" id="diaryEntriesModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-journal-text me-2"></i>Pensamentos de ${patientName}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="d-flex justify-content-end mb-3">
                                <button type="button" class="btn btn-primary" onclick="Patients.showEmotionsChart(${patient ? patient.id : 'null'})">
                                    <i class="bi bi-graph-up-arrow me-1"></i>Gráfico de Emoções
                                </button>
                            </div>
                            ${entries.length === 0 ? `
                                <div class="text-muted">Nenhum pensamento registrado.</div>
                            ` : `
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Data</th>
                                                <th>Situação</th>
                                                <th>Pensamento</th>
                                                <th>Emoções</th>
                                                <th>Comportamento</th>
                                                <th>Consequência</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${entries.map(e => {
                                                const dIso = e.data_registro || e.created_at;
                                                const dataStr = dIso ? window.app.formatDateTime(dIso) : '-';
                                                let emoccoes = '';
                                                try {
                                                    const arr = typeof e.emocao_intensidades === 'string'
                                                        ? JSON.parse(e.emocao_intensidades)
                                                        : (e.emocao_intensidades || []);
                                                    emoccoes = Array.isArray(arr) && arr.length
                                                        ? arr.map(p => `${p.emocao} (${p.intensidade})`).join(', ')
                                                        : (e.emocao ? `${e.emocao} (${e.intensidade ?? '-'})` : '-');
                                                } catch (_) {
                                                    emoccoes = e.emocao ? `${e.emocao} (${e.intensidade ?? '-'})` : '-';
                                                }
                                                return `
                                                    <tr>
                                                        <td>${dataStr}</td>
                                                        <td>${e.situacao || '-'}</td>
                                                        <td>${e.pensamento || '-'}</td>
                                                        <td>${emoccoes}</td>
                                                        <td>${e.comportamento || '-'}</td>
                                                        <td>${e.consequencia || '-'}</td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            `}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const existingModal = document.getElementById('diaryEntriesModal');
        if (existingModal) existingModal.remove();
        document.getElementById('modals-container').innerHTML = modalHtml;
        const modal = new bootstrap.Modal(document.getElementById('diaryEntriesModal'));
        modal.show();
    },

    showEmotionsChart(patientId) {
        if (!patientId) {
            window.app.showError('Paciente inválido para gráfico de emoções');
            return;
        }

        const currentYear = new Date().getFullYear();
        const modalHtml = `
            <div class="modal fade" id="emotionsChartModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"><i class="bi bi-graph-up-arrow me-2"></i>Gráfico de Emoções</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row g-3 mb-3">
                                <div class="col-md-3">
                                    <label class="form-label">Ano</label>
                                    <select class="form-select" id="emotionsYear"></select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Período</label>
                                    <select class="form-select" id="emotionsPeriod">
                                        <option value="day">Dia</option>
                                        <option value="week" selected>Semana</option>
                                        <option value="month">Mês</option>
                                        <option value="year">Ano</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Métrica</label>
                                    <select class="form-select" id="emotionsMetric">
                                        <option value="avg" selected>Média</option>
                                        <option value="max">Máximo</option>
                                        <option value="sum">Soma</option>
                                    </select>
                                </div>
                            </div>
                            <div class="position-relative" id="emotionsChartWrapper">
                                <div id="emotionsLoading" class="d-none" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.6);">
                                    <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div>
                                </div>
                                <canvas id="emotionsChart" height="120"></canvas>
                                <div id="emotionsNoData" class="text-muted d-none mt-2">Sem dados para o período.</div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-primary" id="emotionsExportBtn"><i class="bi bi-download me-1"></i>Exportar PNG</button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        </div>
                    </div>
                </div>
            </div>`;

        const container = document.getElementById('modals-container');
        if (!container) {
            window.app.showError('Container de modais não encontrado');
            return;
        }
        container.innerHTML = modalHtml;
        const modalEl = document.getElementById('emotionsChartModal');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        // Popular anos (últimos 5 anos)
        const yearSel = modalEl.querySelector('#emotionsYear');
        for (let y = currentYear; y >= currentYear - 4; y--) {
            const opt = document.createElement('option');
            opt.value = y;
            opt.textContent = y;
            if (y === currentYear) opt.selected = true;
            yearSel.appendChild(opt);
        }

        const metricSel = modalEl.querySelector('#emotionsMetric');
        const periodSel = modalEl.querySelector('#emotionsPeriod');
        const loadingEl = modalEl.querySelector('#emotionsLoading');
        const noDataEl = modalEl.querySelector('#emotionsNoData');
        const canvasEl = modalEl.querySelector('#emotionsChart');
        const exportBtn = modalEl.querySelector('#emotionsExportBtn');

        const setLoading = (on) => {
            if (on) {
                loadingEl.classList.remove('d-none');
            } else {
                loadingEl.classList.add('d-none');
            }
        };

        const formatLabelBR = (key, period) => {
            try {
                if (period === 'day') {
                    const [y, m, d] = key.split('-').map(Number);
                    const dt = new Date(y, (m || 1) - 1, d || 1);
                    return dt.toLocaleDateString('pt-BR');
                }
                if (period === 'month') {
                    const [y, m] = key.split('-').map(Number);
                    const months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
                    const mm = Math.max(1, Math.min(12, m || 1));
                    return `${months[mm - 1]}/${y}`;
                }
                if (period === 'year') {
                    return String(key);
                }
                const [y, w] = key.split('-');
                return `Semana ${String(Number(w || 1)).padStart(2,'0')}/${y}`;
            } catch (_) {
                return key;
            }
        };

        const renderChart = (labelsRaw, datasets) => {
            if (!window.Chart) {
                noDataEl.classList.remove('d-none');
                noDataEl.textContent = 'Biblioteca de gráficos não disponível.';
                return;
            }
            noDataEl.classList.toggle('d-none', datasets && datasets.length > 0);
            const ctx = canvasEl.getContext('2d');
            // Destruir gráfico anterior se existir
            if (this._emotionsChart) {
                try { this._emotionsChart.destroy(); } catch (e) {}
            }
            const palette = [
                '#0d6efd','#dc3545','#198754','#ffc107','#6610f2','#20c997','#fd7e14','#6c757d','#0dcaf0','#8b5cf6'
            ];
            const chartDatasets = (datasets || []).map((ds, i) => ({
                label: ds.emotion,
                data: ds.values,
                borderColor: palette[i % palette.length],
                backgroundColor: palette[i % palette.length],
                tension: 0.25,
                spanGaps: true
            }));
            // Ajustar escala do eixo Y conforme a métrica selecionada
            const metric = metricSel.value;
            // Encontrar o maior valor das séries para métrica "sum"
            let maxSeriesValue = 0;
            try {
                (datasets || []).forEach(ds => {
                    (ds.values || []).forEach(v => {
                        if (v != null && !isNaN(v)) {
                            const num = Number(v);
                            if (num > maxSeriesValue) maxSeriesValue = num;
                        }
                    });
                });
            } catch (_) {}

            const yScaleOptions = metric === 'sum'
                ? { beginAtZero: true, suggestedMax: Math.max(10, Math.ceil(maxSeriesValue)), title: { display: true, text: 'Soma das intensidades' } }
                : { beginAtZero: true, min: 0, max: 10, suggestedMax: 10, title: { display: true, text: 'Intensidade (0–10)' } };
            const period = periodSel.value;
            const labels = (labelsRaw || []).map(k => formatLabelBR(k, period));
            const xTitle = period === 'day' ? 'Dia' : (period === 'month' ? 'Mês' : (period === 'year' ? 'Ano' : 'Semana'));
            this._emotionsChart = new Chart(ctx, {
                type: 'line',
                data: { labels, datasets: chartDatasets },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        y: yScaleOptions,
                        x: { title: { display: true, text: xTitle } }
                    }
                }
            });
        };

        const fetchData = async () => {
            try {
                setLoading(true);
                const year = yearSel.value;
                const period = periodSel.value;
                const metric = metricSel.value;
                const resp = await window.app.apiCall(`/patients/${patientId}/emotions/weekly?year=${year}&metric=${metric}&period=${period}`);
                const data = resp.data;
                renderChart((data.labels || data.weeks || []), data.datasets || []);
            } catch (err) {
                console.error('Erro ao carregar gráfico de emoções:', err);
                noDataEl.classList.remove('d-none');
                noDataEl.textContent = 'Erro ao carregar dados.';
            } finally {
                setLoading(false);
            }
        };

        // Bind de eventos
        yearSel.addEventListener('change', fetchData);
        periodSel.addEventListener('change', fetchData);
        metricSel.addEventListener('change', fetchData);
        exportBtn.addEventListener('click', () => {
            if (this._emotionsChart) {
                const link = document.createElement('a');
                link.href = this._emotionsChart.toBase64Image();
                link.download = `emocoes_${periodSel.value}_${patientId}_${yearSel.value}.png`;
                link.click();
            }
        });

        // Primeira carga
        fetchData();
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


