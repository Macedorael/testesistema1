// Perfil JavaScript
$(document).ready(function() {
    // Carregar dados do perfil ao inicializar a página
    loadUserProfile();
    
    // Aplicar máscaras aos campos
    applyMasks();
    
    // Event listeners
    $('#profileForm').on('submit', handleProfileSubmit);
    $('#changePasswordForm').on('submit', handlePasswordSubmit);
    $('#changePasswordBtn').on('click', showChangePasswordForm);
    $('#cancelPasswordBtn').on('click', hideChangePasswordForm);
    
    // Event listener para o botão de sair do modal
    $('#exitToSystemBtn').on('click', function() {
        window.location.href = '/paciente-dashboard.html';
    });
});

/**
 * Carrega os dados do perfil do usuário
 */
function loadUserProfile() {
    showLoading();
    
    $.ajax({
            url: '/api/profile',
            method: 'GET',
        success: function(response) {
            if (response.success) {
                populateForm(response.user);
            } else {
                showToast('Erro ao carregar perfil', 'error');
            }
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON?.error || 'Erro ao carregar dados do perfil';
            showToast(errorMsg, 'error');
            
            // Se não autenticado, redirecionar para login
            if (xhr.status === 401) {
                setTimeout(() => {
            window.location.href = '/entrar.html';
                }, 2000);
            }
        },
        complete: function() {
            hideLoading();
        }
    });
}

/**
 * Preenche o formulário com os dados do usuário
 */
function populateForm(user) {
    $('#username').val(user.username || '');
    $('#email').val(user.email || '');
    $('#telefone').val(user.telefone || '');
    $('#data_nascimento').val(user.data_nascimento || '');
}

/**
 * Aplica máscaras aos campos do formulário
 */
function applyMasks() {
    // Máscara para telefone
    $('#telefone').on('input', function() {
        let value = this.value.replace(/\D/g, '');
        if (value.length <= 11) {
            if (value.length <= 10) {
                value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
            } else {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            }
        }
        this.value = value;
    });
    
    // Máscara para data de nascimento
    $('#data_nascimento').on('input', function() {
        let value = this.value.replace(/\D/g, '');
        if (value.length <= 8) {
            value = value.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');
        }
        this.value = value;
    });
    
    // Máscara para CRP
    $('#crp').on('input', function() {
        let value = this.value.replace(/[^0-9\/]/g, '');
        if (value.length <= 9) {
            value = value.replace(/(\d{2})(\d{6})/, '$1/$2');
        }
        this.value = value;
    });
}

/**
 * Manipula o envio do formulário de perfil
 */
function handleProfileSubmit(e) {
    e.preventDefault();
    
    if (!validateProfileForm()) {
        return;
    }
    
    const formData = {
        username: $('#username').val().trim(),
        email: $('#email').val().trim(),
        telefone: $('#telefone').val().trim(),
        data_nascimento: $('#data_nascimento').val().trim()
    };
    
    showLoading();
    $('#saveProfileBtn').prop('disabled', true);
    
    $.ajax({
            url: '/api/profile',
            method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                showToast(response.message, 'success');
                // Atualizar os dados no formulário
                populateForm(response.user);
                
                // Mostrar modal de confirmação após salvar
                $('#confirmationModal').modal('show');
            } else {
                showToast(response.error || 'Erro ao atualizar perfil', 'error');
            }
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON?.error || 'Erro ao atualizar perfil';
            showToast(errorMsg, 'error');
        },
        complete: function() {
            hideLoading();
            $('#saveProfileBtn').prop('disabled', false);
        }
    });
}

/**
 * Valida o formulário de perfil
 */
function validateProfileForm() {
    const username = $('#username').val().trim();
    const email = $('#email').val().trim();
    const dataNascimento = $('#data_nascimento').val().trim();
    
    // Validar campos obrigatórios
    if (!username) {
        showToast('Nome de usuário é obrigatório', 'error');
        $('#username').focus();
        return false;
    }
    
    if (!email) {
        showToast('Email é obrigatório', 'error');
        $('#email').focus();
        return false;
    }
    
    // Validar formato do email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showToast('Formato de email inválido', 'error');
        $('#email').focus();
        return false;
    }
    
    // Validar data de nascimento se preenchida
    if (dataNascimento && !isValidDate(dataNascimento)) {
        showToast('Data de nascimento inválida. Use o formato DD/MM/AAAA', 'error');
        $('#data_nascimento').focus();
        return false;
    }
    
    return true;
}

/**
 * Valida se a data está no formato correto e é válida
 */
function isValidDate(dateString) {
    const regex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
    const match = dateString.match(regex);
    
    if (!match) return false;
    
    const day = parseInt(match[1], 10);
    const month = parseInt(match[2], 10);
    const year = parseInt(match[3], 10);
    
    const date = new Date(year, month - 1, day);
    
    return date.getFullYear() === year &&
           date.getMonth() === month - 1 &&
           date.getDate() === day &&
           year >= 1900 &&
           year <= new Date().getFullYear();
}

/**
 * Mostra o formulário de alteração de senha
 */
function showChangePasswordForm() {
    $('#changePasswordCard').removeClass('d-none');
    $('#changePasswordBtn').addClass('d-none');
    $('#current_password').focus();
}

/**
 * Esconde o formulário de alteração de senha
 */
function hideChangePasswordForm() {
    $('#changePasswordCard').addClass('d-none');
    $('#changePasswordBtn').removeClass('d-none');
    $('#changePasswordForm')[0].reset();
}

/**
 * Manipula o envio do formulário de alteração de senha
 */
function handlePasswordSubmit(e) {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
        return;
    }
    
    const formData = {
        current_password: $('#current_password').val(),
        new_password: $('#new_password').val(),
        confirm_password: $('#confirm_password').val()
    };
    
    showLoading();
    
    $.ajax({
        url: '/api/change-password',
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                showToast(response.message, 'success');
                hideChangePasswordForm();
            } else {
                showToast(response.error || 'Erro ao alterar senha', 'error');
            }
        },
        error: function(xhr) {
            const errorMsg = xhr.responseJSON?.error || 'Erro ao alterar senha';
            showToast(errorMsg, 'error');
        },
        complete: function() {
            hideLoading();
        }
    });
}

/**
 * Valida o formulário de alteração de senha
 */
function validatePasswordForm() {
    const currentPassword = $('#current_password').val();
    const newPassword = $('#new_password').val();
    const confirmPassword = $('#confirm_password').val();
    
    if (!currentPassword) {
        showToast('Senha atual é obrigatória', 'error');
        $('#current_password').focus();
        return false;
    }
    
    if (!newPassword) {
        showToast('Nova senha é obrigatória', 'error');
        $('#new_password').focus();
        return false;
    }
    
    if (newPassword.length < 6) {
        showToast('A nova senha deve ter pelo menos 6 caracteres', 'error');
        $('#new_password').focus();
        return false;
    }
    
    if (newPassword !== confirmPassword) {
        showToast('As senhas não coincidem', 'error');
        $('#confirm_password').focus();
        return false;
    }
    
    return true;
}

/**
 * Mostra o spinner de carregamento
 */
function showLoading() {
    $('#loading-spinner').removeClass('d-none');
}

/**
 * Esconde o spinner de carregamento
 */
function hideLoading() {
    $('#loading-spinner').addClass('d-none');
}

/**
 * Exibe uma mensagem toast
 */
function showToast(message, type = 'info') {
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : 
                   type === 'error' ? 'bg-danger' : 
                   type === 'warning' ? 'bg-warning' : 'bg-info';
    
    const toastHtml = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                <strong class="me-auto">Sistema</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    $('#toast-container').append(toastHtml);
    
    const toastElement = new bootstrap.Toast(document.getElementById(toastId));
    toastElement.show();
    
    // Remover o toast após ser escondido
    document.getElementById(toastId).addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}