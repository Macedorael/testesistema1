document.addEventListener('DOMContentLoaded', function() {
    // Verificar se o usuário está logado
    fetch('/api/me')
        .then(response => {
            if (!response.ok) {
                // Se não estiver logado, redirecionar para a página de login
                window.location.href = '/entrar.html';
                throw new Error('Usuário não autenticado');
            }
            return response.json();
        })
        .then(userData => {
            // Verificar se o usuário é um paciente
            if (userData.role !== 'patient') {
                // Se não for paciente, redirecionar para a página apropriada
                window.location.href = '/';
                throw new Error('Acesso não autorizado');
            }
            
            // Verificar se é o primeiro login
            if (!userData.first_login) {
                // Se não for o primeiro login, redirecionar para a página de agendamentos
                window.location.href = '/paciente-dashboard.html';
                throw new Error('Não é o primeiro login');
            }
        })
        .catch(error => {
            console.error('Erro ao verificar usuário:', error);
        });
    
    // Manipular o envio do formulário de alteração de senha
    const passwordForm = document.getElementById('passwordChangeForm');
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');
    const submitBtn = document.getElementById('submitBtn');
    
    passwordForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Esconder alertas anteriores
        errorAlert.style.display = 'none';
        successAlert.style.display = 'none';
        
        // Obter valores dos campos
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // Validações básicas no lado do cliente
        if (!currentPassword || !newPassword || !confirmPassword) {
            showError('Todos os campos são obrigatórios');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            showError('As novas senhas não coincidem');
            return;
        }
        
        if (newPassword.length < 6) {
            showError('A nova senha deve ter pelo menos 6 caracteres');
            return;
        }
        
        // Mostrar estado de carregamento no botão
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processando...';
        submitBtn.disabled = true;
        
        // Enviar requisição para alterar a senha
        fetch('/api/first-login-change-password', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        })
        .then(response => response.json())
        .then(data => {
            // Restaurar estado do botão
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            if (data.success) {
                showSuccess(data.message);
                
                // Redirecionar após 2 segundos
                setTimeout(() => {
                    window.location.href = data.redirect || '/paciente-dashboard.html';
                }, 2000);
            }
        })
        .catch(error => {
            // Restaurar estado do botão
            submitBtn.innerHTML = originalBtnText;
            submitBtn.disabled = false;
            
            showError('Erro ao conectar com o servidor. Por favor, tente novamente.');
            console.error('Erro:', error);
        });
    });
    
    // Função para mostrar mensagem de erro
    function showError(message) {
        errorAlert.textContent = message;
        errorAlert.style.display = 'block';
    }
    
    // Função para mostrar mensagem de sucesso
    function showSuccess(message) {
        successAlert.textContent = message;
        successAlert.style.display = 'block';
    }
});