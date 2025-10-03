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
        const telefone = document.getElementById('telefone').value.trim();
        const dataNascimento = document.getElementById('data_nascimento').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // Ocultar mensagens anteriores
        hideMessages();
        
        // Validar formulário
        if (!validateForm(username, email, telefone, dataNascimento, password, confirmPassword)) {
            return;
        }
        
        // Mostrar estado de carregamento
        showLoading();
        
        try {
            const requestBody = {
                username: username,
                email: email,
                password: password
            };
            
            // Adicionar campos opcionais apenas se preenchidos
            if (telefone) {
                requestBody.telefone = telefone;
            }
            if (dataNascimento) {
                // Converter DD/MM/YYYY para YYYY-MM-DD para o backend
                const dateRegex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
                const match = dataNascimento.match(dateRegex);
                if (match) {
                    const day = match[1];
                    const month = match[2];
                    const year = match[3];
                    requestBody.data_nascimento = `${year}-${month}-${day}`;
                } else {
                    requestBody.data_nascimento = dataNascimento;
                }
            }
            
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
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
    
    function validateForm(username, email, telefone, dataNascimento, password, confirmPassword) {
        // Verificar se todos os campos obrigatórios estão preenchidos
        if (!username || !email || !password || !confirmPassword) {
            showError('Por favor, preencha todos os campos obrigatórios.');
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
        
        // Validar telefone se preenchido
        if (telefone && telefone.length > 0) {
            const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
            if (!phoneRegex.test(telefone)) {
                showError('Por favor, insira um telefone válido no formato (21) 99999-9999.');
                return false;
            }
        }
        
        // Validar data de nascimento se preenchida
        if (dataNascimento && dataNascimento.length > 0) {
            // Verificar formato DD/MM/YYYY
            const dateRegex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
            const match = dataNascimento.match(dateRegex);
            
            if (!match) {
                showError('Por favor, insira a data no formato DD/MM/YYYY.');
                return false;
            }
            
            const day = parseInt(match[1]);
            const month = parseInt(match[2]);
            const year = parseInt(match[3]);
            
            // Criar data no formato correto (mês é 0-indexado no JavaScript)
            const birthDate = new Date(year, month - 1, day);
            const today = new Date();
            
            // Verificar se a data é válida
            if (birthDate.getDate() !== day || birthDate.getMonth() !== month - 1 || birthDate.getFullYear() !== year) {
                showError('Por favor, insira uma data válida.');
                return false;
            }
            
            if (birthDate > today) {
                showError('A data de nascimento não pode ser no futuro.');
                return false;
            }
            
            const age = today.getFullYear() - birthDate.getFullYear();
            if (age > 120) {
                showError('Por favor, insira uma data de nascimento válida.');
                return false;
            }
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
    
    // Máscara para o campo de telefone
    const telefoneInput = document.getElementById('telefone');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
            
            if (value.length <= 11) {
                if (value.length <= 2) {
                    value = value.replace(/(\d{0,2})/, '($1');
                } else if (value.length <= 6) {
                    value = value.replace(/(\d{2})(\d{0,4})/, '($1) $2');
                } else if (value.length <= 10) {
                    value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
                } else {
                    value = value.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
                }
            }
            
            e.target.value = value;
        });
        
        // Limitar o comprimento máximo
        telefoneInput.addEventListener('keypress', function(e) {
            if (this.value.length >= 15 && e.key !== 'Backspace' && e.key !== 'Delete') {
                e.preventDefault();
            }
        });
    }
});