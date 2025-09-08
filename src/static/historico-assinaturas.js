// Variáveis globais
let currentPage = 1;
const itemsPerPage = 10;

// Inicialização da página
document.addEventListener('DOMContentLoaded', function() {
    loadSubscriptionHistory();
});

// Função para carregar o histórico de assinaturas
async function loadSubscriptionHistory(page = 1) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/subscriptions/history?page=${page}&per_page=${itemsPerPage}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro ao carregar histórico');
        }
        
        if (data.success) {
            displayHistory(data.history);
            displayPagination(data.pagination);
            currentPage = page;
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// Função para exibir o histórico
function displayHistory(historyItems) {
    const timeline = document.getElementById('historyTimeline');
    const emptyState = document.querySelector('.empty-state');
    
    if (!historyItems || historyItems.length === 0) {
        timeline.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    timeline.style.display = 'block';
    
    timeline.innerHTML = historyItems.map(item => createHistoryItem(item)).join('');
}

// Função para criar um item do histórico
function createHistoryItem(item) {
    const actionDate = new Date(item.action_date);
    const formattedDate = actionDate.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const startDate = item.start_date ? new Date(item.start_date).toLocaleDateString('pt-BR') : null;
    const endDate = item.end_date ? new Date(item.end_date).toLocaleDateString('pt-BR') : null;
    
    const actionIcon = getActionIcon(item.action);
    const actionClass = `action-${item.action}`;
    
    return `
        <div class="timeline-item">
            <div class="card history-card ${actionClass} mb-3">
                <div class="card-body">
                    <div class="d-flex align-items-start">
                        <div class="action-icon me-3">
                            <i class="${actionIcon}"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title mb-1">
                                    ${item.action_description}
                                </h5>
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>
                                    ${formattedDate}
                                </small>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    ${item.previous_plan_type && item.action === 'renewed' ? `
                                    <p class="card-text mb-1">
                                        <strong>Plano Anterior:</strong> ${getPlanName(item.previous_plan_type)}
                                        <small class="text-muted">(R$ ${item.previous_price.toFixed(2).replace('.', ',')})</small>
                                    </p>
                                    <p class="card-text mb-1">
                                        <strong>Novo Plano:</strong> ${item.plan_name}
                                        <small class="text-success">(R$ ${item.price.toFixed(2).replace('.', ',')})</small>
                                    </p>
                                    ` : `
                                    <p class="card-text mb-1">
                                        <strong>Plano:</strong> ${item.plan_name}
                                    </p>
                                    <p class="card-text mb-1">
                                        <strong>Valor:</strong> R$ ${item.price.toFixed(2).replace('.', ',')}
                                    </p>
                                    `}
                                </div>
                                ${startDate && endDate ? `
                                <div class="col-md-6">
                                    <p class="card-text mb-1">
                                        <strong>Período:</strong> ${startDate} a ${endDate}
                                    </p>
                                </div>
                                ` : ''}
                            </div>
                            
                            ${item.details ? `
                            <div class="mt-2">
                                <small class="text-muted">
                                    <i class="fas fa-info-circle me-1"></i>
                                    ${item.details}
                                </small>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Função para obter o ícone da ação
function getActionIcon(action) {
    const icons = {
        'created': 'fas fa-plus',
        'cancelled': 'fas fa-times',
        'renewed': 'fas fa-redo',
        'updated': 'fas fa-edit',
        'expired': 'fas fa-clock'
    };
    return icons[action] || 'fas fa-question';
}

// Função para obter o nome amigável do plano
function getPlanName(planType) {
    const planNames = {
        'monthly': 'Mensal',
        'quarterly': 'Trimestral',
        'biannual': 'Semestral',
        'annual': 'Anual'
    };
    return planNames[planType] || planType;
}

// Função para exibir a paginação
function displayPagination(pagination) {
    const container = document.getElementById('paginationContainer');
    
    if (pagination.pages <= 1) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    
    let paginationHTML = '<nav><ul class="pagination">';
    
    // Botão Anterior
    if (pagination.has_prev) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadSubscriptionHistory(${pagination.page - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
    } else {
        paginationHTML += `
            <li class="page-item disabled">
                <span class="page-link">
                    <i class="fas fa-chevron-left"></i>
                </span>
            </li>
        `;
    }
    
    // Números das páginas
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);
    
    if (startPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadSubscriptionHistory(1)">1</a>
            </li>
        `;
        if (startPage > 2) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === pagination.page) {
            paginationHTML += `
                <li class="page-item active">
                    <span class="page-link">${i}</span>
                </li>
            `;
        } else {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="loadSubscriptionHistory(${i})">${i}</a>
                </li>
            `;
        }
    }
    
    if (endPage < pagination.pages) {
        if (endPage < pagination.pages - 1) {
            paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadSubscriptionHistory(${pagination.pages})">${pagination.pages}</a>
            </li>
        `;
    }
    
    // Botão Próximo
    if (pagination.has_next) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadSubscriptionHistory(${pagination.page + 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    } else {
        paginationHTML += `
            <li class="page-item disabled">
                <span class="page-link">
                    <i class="fas fa-chevron-right"></i>
                </span>
            </li>
        `;
    }
    
    paginationHTML += '</ul></nav>';
    container.innerHTML = paginationHTML;
}

// Função para mostrar/ocultar loading
function showLoading(show) {
    const spinner = document.querySelector('.loading-spinner');
    const timeline = document.getElementById('historyTimeline');
    const emptyState = document.querySelector('.empty-state');
    const pagination = document.getElementById('paginationContainer');
    
    if (show) {
        spinner.style.display = 'block';
        timeline.style.display = 'none';
        emptyState.style.display = 'none';
        pagination.style.display = 'none';
    } else {
        spinner.style.display = 'none';
    }
}

// Função para mostrar erro
function showError(message) {
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    document.getElementById('errorMessage').textContent = message;
    errorModal.show();
}

// Função de logout
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        fetch('/api/logout', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(() => {
            window.location.href = '/entrar.html';
        }).catch(() => {
            window.location.href = '/entrar.html';
        });
    }
}

// Função para atualizar a página
function refreshHistory() {
    loadSubscriptionHistory(currentPage);
}

// Event listeners para atalhos de teclado
document.addEventListener('keydown', function(e) {
    // F5 para atualizar
    if (e.key === 'F5') {
        e.preventDefault();
        refreshHistory();
    }
    
    // Escape para fechar modais
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});

// Auto-refresh a cada 5 minutos
setInterval(refreshHistory, 5 * 60 * 1000);