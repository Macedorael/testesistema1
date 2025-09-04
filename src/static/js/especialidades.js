// Variáveis globais
let especialidades = [];
let filteredEspecialidades = [];
let especialidadeToDelete = null;
let searchTimeout = null;
let currentPage = 1;
const itemsPerPage = 20; // Paginação para melhor performance

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // A inicialização agora é feita via app.js quando a página é carregada
    // Este código é mantido para compatibilidade, mas a inicialização principal
    // acontece através do objeto window.Especialidades.init()
});

function setupEventListeners() {
    // Aguardar um pouco para garantir que os elementos estejam no DOM
    setTimeout(() => {
        // Event listener para o formulário
        const form = document.getElementById('especialidadeForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                saveEspecialidade();
            });
        }
        
        // Event listener para busca com debounce
        const searchInput = document.getElementById('especialidade-search');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                
                // Limpar timeout anterior
                if (searchTimeout) {
                    clearTimeout(searchTimeout);
                }
                
                // Aplicar debounce de 300ms
                searchTimeout = setTimeout(() => {
                    filterEspecialidades(searchTerm);
                }, 300);
            });
        }
        
        // Reset form when modal is hidden
        const especialidadeModal = document.getElementById('especialidadeModal');
        if (especialidadeModal) {
            especialidadeModal.addEventListener('hidden.bs.modal', function() {
                resetForm();
            });
        }
    }, 100);
}

// Carregar especialidades
async function loadEspecialidades() {
    try {
        const response = await fetch('/api/especialidades');
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'entrar.html';
                return;
            }
            throw new Error('Erro ao carregar especialidades');
        }
        
        especialidades = await response.json();
        renderEspecialidadesTable();
    } catch (error) {
        console.error('Erro:', error);
        showAlert('Erro ao carregar especialidades: ' + error.message, 'danger');
    }
}

// Renderizar tabela de especialidades com paginação otimizada
function renderEspecialidadesTable(dataToRender = null) {
    const tbody = document.getElementById('especialidadesTableBody');
    
    if (!tbody) {
        console.error('Elemento especialidadesTableBody não encontrado');
        return;
    }
    
    const data = dataToRender || (filteredEspecialidades.length > 0 ? filteredEspecialidades : especialidades);
    
    if (data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    <i class="bi bi-tags" style="font-size: 3rem; margin-bottom: 1rem; display: block;"></i>
                    <p>Nenhuma especialidade cadastrada</p>
                </td>
            </tr>
        `;
        updatePaginationInfo(0, 0);
        renderPaginationControls(0);
        return;
    }
    
    // Implementar paginação para melhor performance
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = data.slice(startIndex, endIndex);
    
    // Usar DocumentFragment para melhor performance
    const fragment = document.createDocumentFragment();
    
    paginatedData.forEach(especialidade => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${especialidade.id}</td>
            <td>${especialidade.nome}</td>
            <td>${especialidade.descricao || '-'}</td>
            <td>${formatDate(especialidade.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="editEspecialidade(${especialidade.id})" title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteEspecialidade(${especialidade.id})" title="Excluir">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        fragment.appendChild(row);
    });
    
    // Limpar e adicionar novo conteúdo de uma vez
    tbody.innerHTML = '';
    tbody.appendChild(fragment);
    
    // Atualizar controles de paginação
     updatePaginationInfo(data.length, paginatedData.length);
     renderPaginationControls(data.length);
}

// Resetar formulário
function resetForm() {
    const form = document.getElementById('especialidadeForm');
    const idField = document.getElementById('especialidadeId');
    const titleField = document.getElementById('modalTitle');
    
    if (form) form.reset();
    if (idField) idField.value = '';
    if (titleField) titleField.textContent = 'Nova Especialidade';
}

// Salvar especialidade
async function saveEspecialidade() {
    const form = document.getElementById('especialidadeForm');
    const idField = document.getElementById('especialidadeId');
    const nomeField = document.getElementById('nome');
    const descricaoField = document.getElementById('descricao');
    
    if (!form || !idField || !nomeField || !descricaoField) {
        console.error('Elementos do formulário não encontrados');
        showAlert('Erro interno: elementos do formulário não encontrados', 'danger');
        return;
    }
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const especialidadeId = idField.value;
    const data = {
        nome: nomeField.value.trim(),
        descricao: descricaoField.value.trim()
    };
    
    try {
        const url = especialidadeId ? `/api/especialidades/${especialidadeId}` : '/api/especialidades';
        const method = especialidadeId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao salvar especialidade');
        }
        
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('especialidadeModal'));
        modal.hide();
        
        // Recarregar lista
        await loadEspecialidades();
        
        showAlert(
            especialidadeId ? 'Especialidade atualizada com sucesso!' : 'Especialidade criada com sucesso!',
            'success'
        );
    } catch (error) {
        console.error('Erro:', error);
        showAlert('Erro ao salvar especialidade: ' + error.message, 'danger');
    }
}

// Editar especialidade
function editEspecialidade(id) {
    const especialidade = especialidades.find(e => e.id === id);
    
    if (!especialidade) {
        showAlert('Especialidade não encontrada', 'danger');
        return;
    }
    
    // Verificar se os elementos existem
    const idField = document.getElementById('especialidadeId');
    const nomeField = document.getElementById('nome');
    const descricaoField = document.getElementById('descricao');
    const titleField = document.getElementById('modalTitle');
    const modalElement = document.getElementById('especialidadeModal');
    
    if (!idField || !nomeField || !descricaoField || !titleField || !modalElement) {
        console.error('Elementos do modal não encontrados');
        showAlert('Erro interno: elementos do modal não encontrados', 'danger');
        return;
    }
    
    // Preencher formulário
    idField.value = especialidade.id;
    nomeField.value = especialidade.nome;
    descricaoField.value = especialidade.descricao || '';
    titleField.textContent = 'Editar Especialidade';
    
    // Abrir modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

// Deletar especialidade
function deleteEspecialidade(id) {
    const especialidade = especialidades.find(e => e.id === id);
    
    if (!especialidade) {
        showAlert('Especialidade não encontrada', 'danger');
        return;
    }
    
    especialidadeToDelete = id;
    
    // Abrir modal de confirmação
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Confirmar exclusão
async function confirmDelete() {
    if (!especialidadeToDelete) return;
    
    try {
        const response = await fetch(`/api/especialidades/${especialidadeToDelete}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao deletar especialidade');
        }
        
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
        modal.hide();
        
        // Recarregar lista
        await loadEspecialidades();
        
        showAlert('Especialidade deletada com sucesso!', 'success');
        
        especialidadeToDelete = null;
    } catch (error) {
        console.error('Erro:', error);
        showAlert('Erro ao deletar especialidade: ' + error.message, 'danger');
    }
}

// Filtrar especialidades (otimizada com paginação e lazy loading)
function filterEspecialidades(searchTerm) {
    currentPage = 1; // Reset para primeira página ao filtrar
    
    if (!searchTerm) {
        // Se não há termo de busca, limpar filtro
        filteredEspecialidades = [];
        renderEspecialidadesTable();
        return;
    }
    
    // Filtrar dados em memória com otimização
    filteredEspecialidades = especialidades.filter(especialidade => {
        const nome = especialidade.nome.toLowerCase();
        const descricao = (especialidade.descricao || '').toLowerCase();
        return nome.includes(searchTerm) || descricao.includes(searchTerm);
    });
    
    // Renderizar resultados filtrados com paginação
    renderEspecialidadesTable(filteredEspecialidades);
}

// Atualizar informações de paginação
function updatePaginationInfo(totalItems, currentItems) {
    const startItem = totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, totalItems);
    
    let infoContainer = document.getElementById('pagination-info');
    if (!infoContainer) {
        infoContainer = document.createElement('div');
        infoContainer.id = 'pagination-info';
        infoContainer.className = 'pagination-info mt-2';
        
        const tableContainer = document.querySelector('.table-responsive');
        if (tableContainer && tableContainer.parentNode) {
            tableContainer.parentNode.insertBefore(infoContainer, tableContainer.nextSibling);
        }
    }
    
    if (totalItems > 0) {
        infoContainer.innerHTML = `<small class="text-muted">Mostrando ${startItem}-${endItem} de ${totalItems} registros</small>`;
        infoContainer.style.display = 'block';
    } else {
        infoContainer.style.display = 'none';
    }
}

// Renderizar controles de paginação
function renderPaginationControls(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    let paginationContainer = document.getElementById('pagination-controls');
    if (!paginationContainer) {
        paginationContainer = document.createElement('nav');
        paginationContainer.id = 'pagination-controls';
        paginationContainer.className = 'pagination-controls mt-3 d-flex justify-content-center';
        
        const infoContainer = document.getElementById('pagination-info');
        if (infoContainer && infoContainer.parentNode) {
            infoContainer.parentNode.insertBefore(paginationContainer, infoContainer.nextSibling);
        }
    }
    
    if (totalPages <= 1) {
        paginationContainer.style.display = 'none';
        return;
    }
    
    paginationContainer.style.display = 'flex';
    
    paginationContainer.innerHTML = `
        <ul class="pagination pagination-sm mb-0">
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <button class="page-link" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
                    <i class="bi bi-chevron-left"></i>
                </button>
            </li>
            ${generatePageNumbers(currentPage, totalPages)}
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <button class="page-link" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
                    <i class="bi bi-chevron-right"></i>
                </button>
            </li>
        </ul>
    `;
}

// Gerar números das páginas
function generatePageNumbers(current, total) {
    let pages = [];
    const maxVisible = 5;
    
    let start = Math.max(1, current - Math.floor(maxVisible / 2));
    let end = Math.min(total, start + maxVisible - 1);
    
    if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1);
    }
    
    for (let i = start; i <= end; i++) {
        pages.push(`
            <li class="page-item ${i === current ? 'active' : ''}">
                <button class="page-link" onclick="changePage(${i})">${i}</button>
            </li>
        `);
    }
    
    return pages.join('');
}

// Mudar página
function changePage(page) {
    const dataToRender = filteredEspecialidades.length > 0 ? filteredEspecialidades : especialidades;
    const totalPages = Math.ceil(dataToRender.length / itemsPerPage);
    
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    renderEspecialidadesTable();
}

// Função para formatar data
function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Função duplicada removida - usando a definição anterior

// Função duplicada removida - usando a definição anterior

// Função para mostrar alertas
function showAlert(message, type = 'info') {
    // Remove alertas existentes
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Criar novo alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Inserir no início do main-content
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
        
        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    } else {
        console.log(message);
    }
}

// Função de logout
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        fetch('/api/logout', { method: 'POST' })
            .then(() => {
                window.location.href = 'entrar.html';
            })
            .catch(() => {
                window.location.href = 'entrar.html';
            });
    }
}

// Objeto global para integração com app.js
window.Especialidades = {
    init: function() {
        loadEspecialidades();
        setupEventListeners();
    },
    
    showCreateModal: function() {
        resetForm();
        const modalTitle = document.getElementById('modalTitle');
        if (modalTitle) {
            modalTitle.textContent = 'Nova Especialidade';
        }
        const modalElement = document.getElementById('especialidadeModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }
};