document.addEventListener('DOMContentLoaded', async function() {
    // Verificar se o usuário já está logado via API (mais confiável que localStorage)
    try {
        const response = await fetch('/api/me');
        if (response.ok) {
            // Usuário já está logado - redirecionar baseado na assinatura
            const userResponse = await fetch('/api/subscriptions/my-subscription');
            if (userResponse.ok) {
                const userData = await userResponse.json();
                if (userData.success && userData.subscription && userData.subscription.status === 'active') {
                    window.location.href = '/';
                } else {
                    window.location.href = 'assinaturas.html';
                }
            } else {
                window.location.href = 'assinaturas.html';
            }
            return;
        }
    } catch (error) {
        console.log('Usuário não está logado, continuando com a página de login');
    }

    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');

    // Formulário de login
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const button = this.querySelector('button[type="submit"]');
        const originalText = button.textContent;
        
        // Limpar mensagem de erro anterior
        errorMessage.textContent = '';
        errorMessage.classList.remove('show');
        
        // Efeito de loading no botão
        button.textContent = 'Entrando...';
        button.disabled = true;
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Login bem-sucedido
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userInfo', JSON.stringify(data.user));
                
                // Redirecionar baseado no status da assinatura
                window.location.href = data.redirect || 'index.html';
            } else {
                // Restaurar botão
                button.textContent = originalText;
                button.disabled = false;
                
                // Exibir mensagem de erro específica
                errorMessage.textContent = data.error || 'Erro ao fazer login';
                errorMessage.classList.add('show');
                
                // Remover a classe 'show' após 5 segundos
                setTimeout(() => {
                    errorMessage.classList.remove('show');
                }, 5000);
                
                // Limpar os campos se for erro de senha
                if (data.error && data.error.includes('Senha incorreta')) {
                    document.getElementById('password').value = '';
                    document.getElementById('password').focus();
                } else if (data.error && data.error.includes('Usuário não encontrado')) {
                    document.getElementById('email').focus();
                }
            }
        } catch (error) {
            console.error('Erro:', error);
            
            // Restaurar botão
            button.textContent = originalText;
            button.disabled = false;
            
            errorMessage.textContent = 'Erro de conexão com o servidor. Verifique sua internet e tente novamente.';
            errorMessage.classList.add('show');
            
            // Remover a classe 'show' após 5 segundos
            setTimeout(() => {
                errorMessage.classList.remove('show');
            }, 5000);
        }
    });


});

