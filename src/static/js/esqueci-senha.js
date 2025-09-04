document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('forgotPasswordForm');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const emailInput = document.getElementById('email');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Limpar mensagens anteriores
        clearMessages();
        
        // Validar email
        const email = emailInput.value.trim();
        if (!email) {
            showError('Por favor, digite seu email.');
            emailInput.focus();
            return;
        }
        
        if (!isValidEmail(email)) {
            showError('Por favor, digite um email válido.');
            emailInput.focus();
            return;
        }
        
        // Mostrar loading
        setLoading(true);
        
        try {
            const response = await fetch('/api/esqueci-senha', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showSuccess(data.message);
                form.reset();
            } else {
                showError(data.error || 'Erro ao processar solicitação.');
                if (data.error && data.error.includes('não encontrado')) {
                    emailInput.focus();
                }
            }
        } catch (error) {
            console.error('Erro:', error);
            showError('Erro de conexão com o servidor. Verifique sua internet e tente novamente.');
        } finally {
            setLoading(false);
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
        
        // Remover mensagem após 10 segundos (mais tempo para ler)
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
            submitBtn.textContent = 'Enviando...';
        } else {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Enviar Email de Recuperação';
        }
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});