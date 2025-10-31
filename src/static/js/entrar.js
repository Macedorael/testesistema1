document.addEventListener('DOMContentLoaded', async function() {
    // Detectar contexto da página para restringir login por papel
    const urlParams = new URLSearchParams(window.location.search);
    const isPatientLoginPage = (
        window.location.pathname.endsWith('entrar-paciente.html') ||
        urlParams.has('paciente')
    );
    const loginScope = isPatientLoginPage ? 'patient' : 'professional';
    // Verificar se o usuário já está logado via API (mais confiável que localStorage)
    try {
        const response = await fetch('/api/me');
        if (response.ok) {
            const userData = await response.json();
            
            // Verificar se é um paciente
            if (userData.role === 'patient') {
                // Verificar se é o primeiro login
                if (userData.first_login) {
                    window.location.href = '/paciente-primeiro-login.html';
                } else {
                    window.location.href = '/paciente-dashboard.html';
                }
                return;
            }
            
            // Para outros usuários, redirecionar baseado na assinatura
            const userResponse = await fetch('/api/subscriptions/my-subscription');
            if (userResponse.ok) {
                const subscriptionData = await userResponse.json();
                if (subscriptionData.success && subscriptionData.subscription && subscriptionData.subscription.status === 'active') {
                    window.location.href = '/index.html';
                } else {
                    // Sem assinatura ativa: seguir para a tela inicial
                    window.location.href = '/index.html';
                }
            } else {
                // Em caso de erro na verificação da assinatura: seguir para a tela inicial
                window.location.href = '/index.html';
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
                body: JSON.stringify({ email, password, login_scope: loginScope })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Login bem-sucedido
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userInfo', JSON.stringify(data.user));
                // Marcar que acabou de logar (usado pelo dashboard do paciente)
                try {
                    if (loginScope === 'patient' || (data.user && data.user.role === 'patient')) {
                        sessionStorage.setItem('justLoggedIn', 'patient');
                    } else {
                        sessionStorage.setItem('justLoggedIn', 'other');
                    }
                } catch (_) {}
                
                // Redirecionar baseado no status da assinatura (normaliza dashboard -> index)
                const normalizeRedirect = (path) => {
                    if (!path) return null;
                    const p = path.trim();
                    if (p === '/dashboard.html' || p === 'dashboard.html') return '/index.html';
                    return p;
                };
                let target = normalizeRedirect(data.redirect) || 'index.html';
                // Garantir que paciente vá para o dashboard do paciente
                if (loginScope === 'patient' || (data.user && data.user.role === 'patient')) {
                    target = '/paciente-dashboard.html';
                }
                window.location.href = target;
            } else {
                // Restaurar botão
                button.textContent = originalText;
                button.disabled = false;
                
                // Exibir mensagem de erro específica
                // Mensagens claras quando o papel não corresponde ao contexto
                if (response.status === 403 && data && data.error) {
                    errorMessage.textContent = data.error;
                } else {
                    errorMessage.textContent = data.error || 'Erro ao fazer login';
                }
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

