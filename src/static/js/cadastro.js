document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const btnRegister = document.querySelector('.btn-register');
    const btnText = document.querySelector('.btn-text');
    const btnLoading = document.querySelector('.btn-loading');

    // Add focus effects to inputs
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    // Form submission
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // Ocultar mensagens anteriores
        hideMessages();
        
        // Validar formulário
        if (!validateForm(username, email, password, confirmPassword)) {
            return;
        }
        
        // Mostrar estado de carregamento
        showLoading();
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showSuccess('Conta criada com sucesso! Redirecionando para o login...');
                
                // Limpar formulário
                registerForm.reset();
                
                // Redirecionar para login após 2 segundos
                setTimeout(() => {
                    window.location.href = 'entrar.html';
                }, 2000);
            } else {
                showError(data.error || 'Erro ao criar conta. Tente novamente.');
            }
        } catch (error) {
            console.error('Erro:', error);
            showError('Erro de conexão. Verifique sua internet e tente novamente.');
        } finally {
            hideLoading();
        }
    });
    
    function validateForm(username, email, password, confirmPassword) {
        // Verificar se todos os campos estão preenchidos
        if (!username || !email || !password || !confirmPassword) {
            showError('Por favor, preencha todos os campos.');
            return false;
        }
        
        // Validar comprimento do nome de usuário
        if (username.length < 3) {
            showError('O nome de usuário deve ter pelo menos 3 caracteres.');
            return false;
        }
        
        // Validar formato do email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showError('Por favor, insira um e-mail válido.');
            return false;
        }
        
        // Validar comprimento da senha
        if (password.length < 6) {
            showError('A senha deve ter pelo menos 6 caracteres.');
            return false;
        }
        
        // Verificar se as senhas coincidem
        if (password !== confirmPassword) {
            showError('As senhas não coincidem.');
            return false;
        }
        
        return true;
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        successMessage.style.display = 'none';
        
        // Rolar para mensagem de erro
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.style.display = 'block';
        errorMessage.style.display = 'none';
        
        // Rolar para mensagem de sucesso
        successMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    function hideMessages() {
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';
    }
    
    function showLoading() {
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
        btnRegister.disabled = true;
    }
    
    function hideLoading() {
        btnText.style.display = 'block';
        btnLoading.style.display = 'none';
        btnRegister.disabled = false;
    }
    
    // Validação de confirmação de senha em tempo real
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    function checkPasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.style.borderColor = '#e53e3e';
            confirmPasswordInput.style.boxShadow = '0 0 0 3px rgba(229, 62, 62, 0.1)';
        } else {
            confirmPasswordInput.style.borderColor = '#e2e8f0';
            confirmPasswordInput.style.boxShadow = 'none';
        }
    }
    
    passwordInput.addEventListener('input', checkPasswordMatch);
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    
    // Verificar se o usuário já está logado
    const token = localStorage.getItem('token');
    if (token) {
        // Verificar se o token ainda é válido
        fetch('/api/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                // Usuário já está logado, redirecionar para dashboard
                window.location.href = 'index.html';
            }
        })
        .catch(error => {
            // Token é inválido, removê-lo
            localStorage.removeItem('token');
            localStorage.removeItem('user');
        });
    }
});