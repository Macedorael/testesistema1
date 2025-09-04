document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('resetPasswordForm');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const tokenInput = document.getElementById('token');

    // Extrair token da URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (!token) {
        showError('Token de recuperação não encontrado. Solicite uma nova recuperação de senha.');
        setTimeout(() => {
            window.location.href = 'esqueci-senha.html';
        }, 3000);
        return;
    }
    
    tokenInput.value = token;

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
        
        if (password.length < 6) {
            showError('A senha deve ter pelo menos 6 caracteres.');
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
                    token: token,
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
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    });
    
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