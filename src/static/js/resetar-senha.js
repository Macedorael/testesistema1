document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('resetPasswordForm');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const tokenInput = document.getElementById('token');
    // Não exigir mais token na URL; backend lerá do cookie (HttpOnly).
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (tokenInput) {
        tokenInput.value = token || '';
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Limpar mensagens anteriores
        clearMessages();
        
        // Validar campos
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (!password) {
            showError('Por favor, digite sua nova senha.');
            passwordInput.focus();
            return;
        }
        
        // Validar força da senha: mínimo 8 caracteres, 1 maiúscula e 1 especial
        const strongPasswordRegex = /^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$/;
        if (!strongPasswordRegex.test(password)) {
            showError('A senha deve ter no mínimo 8 caracteres, conter 1 letra maiúscula e 1 caractere especial.');
            passwordInput.focus();
            return;
        }
        
        if (!confirmPassword) {
            showError('Por favor, confirme sua nova senha.');
            confirmPasswordInput.focus();
            return;
        }
        
        if (password !== confirmPassword) {
            showError('As senhas não coincidem. Verifique e tente novamente.');
            confirmPasswordInput.focus();
            confirmPasswordInput.select();
            return;
        }
        
        // Mostrar loading
        setLoading(true);
        
        try {
            const response = await fetch('/api/resetar-senha', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    // token opcional: se vier na URL, envia; caso contrário, backend usa cookie
                    token: token || undefined,
                    password: password 
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showSuccess(data.message);
                form.reset();
                
                // Redirecionar para login após 3 segundos
                setTimeout(() => {
                    window.location.href = 'entrar.html';
                }, 3000);
            } else {
                showError(data.error || 'Erro ao resetar senha.');
                
                // Se token inválido, redirecionar para solicitar novo
                if (data.error && data.error.includes('inválido') || data.error.includes('expirado')) {
                    setTimeout(() => {
                        window.location.href = 'esqueci-senha.html';
                    }, 3000);
                }
            }
        } catch (error) {
            console.error('Erro:', error);
            showError('Erro de conexão com o servidor. Verifique sua internet e tente novamente.');
        } finally {
            setLoading(false);
        }
    });
    
    // Validação em tempo real para confirmação de senha
    confirmPasswordInput.addEventListener('input', function() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.setCustomValidity('As senhas não coincidem');
            confirmPasswordInput.classList.add('input-invalid');
        } else {
            confirmPasswordInput.setCustomValidity('');
            confirmPasswordInput.classList.remove('input-invalid');
        }
    });

    // Validação em tempo real para força da senha + indicadores
    const criteriaItems = document.querySelectorAll('#passwordCriteriaReset .requirement');
    function updateResetPasswordIndicators() {
        const value = passwordInput.value || '';
        const hasLength = value.length >= 8;
        const hasUpper = /[A-Z]/.test(value);
        const hasSpecial = /[^A-Za-z0-9]/.test(value);

        criteriaItems.forEach(function(item) {
            const req = item.getAttribute('data-req');
            let ok = false;
            if (req === 'length') ok = hasLength;
            if (req === 'uppercase') ok = hasUpper;
            if (req === 'special') ok = hasSpecial;
            item.classList.toggle('valid', ok);
            item.classList.toggle('invalid', !ok && value.length > 0);
        });

        const allOk = hasLength && hasUpper && hasSpecial;
        if (allOk) {
            passwordInput.classList.add('input-valid');
            passwordInput.classList.remove('input-invalid');
            passwordInput.setCustomValidity('');
        } else {
            passwordInput.classList.remove('input-valid');
            passwordInput.classList.toggle('input-invalid', value.length > 0);
            if (value.length > 0) {
                passwordInput.setCustomValidity('Use 8+ caracteres, 1 maiúscula e 1 especial.');
            } else {
                passwordInput.setCustomValidity('');
            }
        }
    }

    passwordInput.addEventListener('input', function() {
        updateResetPasswordIndicators();
        // também atualiza match quando digita a principal
        const confirmPassword = confirmPasswordInput.value;
        if (confirmPassword) {
            const mismatch = passwordInput.value !== confirmPassword;
            confirmPasswordInput.classList.toggle('input-invalid', mismatch);
            confirmPasswordInput.setCustomValidity(mismatch ? 'As senhas não coincidem' : '');
        }
    });
    passwordInput.addEventListener('blur', updateResetPasswordIndicators);
    confirmPasswordInput.addEventListener('blur', function(){
        const mismatch = confirmPasswordInput.value && passwordInput.value !== confirmPasswordInput.value;
        confirmPasswordInput.classList.toggle('input-invalid', mismatch);
        confirmPasswordInput.setCustomValidity(mismatch ? 'As senhas não coincidem' : '');
    });

    // Inicializa indicadores ao carregar
    updateResetPasswordIndicators();
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
        
        // Remover mensagem após 5 segundos
        setTimeout(() => {
            errorMessage.classList.remove('show');
        }, 5000);
    }
    
    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.classList.add('show');
        
        // Remover mensagem após 10 segundos
        setTimeout(() => {
            successMessage.classList.remove('show');
        }, 10000);
    }
    
    function clearMessages() {
        errorMessage.classList.remove('show');
        successMessage.classList.remove('show');
        errorMessage.textContent = '';
        successMessage.textContent = '';
    }
    
    function setLoading(loading) {
        if (loading) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Alterando Senha...';
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Alterar Senha';
        }
    }
});