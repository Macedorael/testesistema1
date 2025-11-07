document.addEventListener('DOMContentLoaded', async function() {
    // Sanitizar URL caso algum submit GET tenha ocorrido acidentalmente (evitar vazamento)
    try {
        const qs = window.location.search || '';
        if (qs.includes('password=') || qs.includes('email=')) {
            history.replaceState(null, '', window.location.pathname);
        }
    } catch (_) {}
    // Detectar contexto da página para restringir login por papel
    const urlParams = new URLSearchParams(window.location.search);
    // Suprimir redirecionamentos automáticos somente quando explicitamente solicitado
    const suppressAutoRedirect = urlParams.has('stay');
    // Fazer logout automático quando vindo de acesso expirado
    const shouldAutoLogout = urlParams.get('from') === 'expired' || urlParams.has('logout');
    const isPatientLoginPage = (
        window.location.pathname.endsWith('entrar-paciente.html') ||
        urlParams.has('paciente')
    );
    const loginScope = isPatientLoginPage ? 'patient' : 'professional';

    // Se solicitado, efetuar logout imediato antes de qualquer verificação
    if (shouldAutoLogout) {
        try {
            await fetch('/api/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
        } catch (_) {}
        try {
            localStorage.clear();
            sessionStorage.clear();
        } catch (_) {}
    }

    // Helper: mostrar mensagem visível quando staying estiver ativo
    function showStayInfo(message, targetLabel, targetHref) {
        try {
            const container = document.querySelector('.login-container');
            if (!container) return;
            // Remover mensagem anterior se existir
            const existing = document.getElementById('stayMessage');
            if (existing) existing.remove();
            const box = document.createElement('div');
            box.id = 'stayMessage';
            box.style.marginTop = '16px';
            box.style.padding = '12px 14px';
            box.style.borderRadius = '10px';
            box.style.border = '1px solid #9ae6b4';
            box.style.background = '#c6f6d5';
            box.style.color = '#22543d';
            box.style.fontWeight = '600';
            box.style.textAlign = 'center';
            box.style.boxShadow = '0 4px 10px rgba(0,0,0,0.06)';
            box.innerHTML = `${message} <a href="${targetHref}" style="margin-left:8px;color:#2f855a;text-decoration:underline;">${targetLabel}</a>`;
            container.appendChild(box);
        } catch (e) {
            console.warn('Falha ao exibir mensagem stay:', e);
        }
    }

    // Helper: modal de aviso de renovação de assinatura (exibido somente após login)
    function showRenewalModal(daysRemaining, onContinue) {
        try {
            // Evitar duplicar modal
            if (document.getElementById('renewalModalOverlay')) return;

            const overlay = document.createElement('div');
            overlay.id = 'renewalModalOverlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.background = 'rgba(0,0,0,0.45)';
            overlay.style.zIndex = '9999';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';

            const modal = document.createElement('div');
            modal.id = 'renewalModal';
            modal.style.background = '#ffffff';
            modal.style.borderRadius = '14px';
            modal.style.boxShadow = '0 12px 28px rgba(0,0,0,0.18)';
            modal.style.maxWidth = '480px';
            modal.style.width = '90%';
            modal.style.padding = '20px 22px';
            modal.style.fontFamily = 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial';

            const title = document.createElement('h3');
            const nearExpiry = typeof daysRemaining === 'number' && daysRemaining >= 1 && daysRemaining <= 5;
            title.textContent = nearExpiry ? 'Assinatura próxima do vencimento' : 'Status da assinatura';
            title.style.margin = '0 0 10px 0';
            title.style.fontSize = '20px';
            title.style.color = '#1a202c';

            const info = document.createElement('p');
            const dias = Number(daysRemaining) === 1 ? '1 dia' : `${Number(daysRemaining)} dias`;
            if (nearExpiry) {
                info.textContent = `Faltam ${dias} para o término da sua assinatura.`;
            } else if (typeof daysRemaining === 'number') {
                info.textContent = `Assinatura ativa. Faltam ${dias} para o vencimento.`;
            } else {
                info.textContent = 'Não foi possível calcular os dias restantes da assinatura.';
            }
            info.style.margin = '0 0 16px 0';
            info.style.color = '#2d3748';
            info.style.fontSize = '14px';

            const actions = document.createElement('div');
            actions.style.display = 'flex';
            actions.style.gap = '10px';
            actions.style.justifyContent = 'flex-end';

            const continueBtn = document.createElement('button');
            continueBtn.textContent = 'Continuar';
            continueBtn.style.background = '#edf2f7';
            continueBtn.style.color = '#2d3748';
            continueBtn.style.border = '1px solid #cbd5e0';
            continueBtn.style.padding = '10px 14px';
            continueBtn.style.borderRadius = '8px';
            continueBtn.style.cursor = 'pointer';

            actions.appendChild(continueBtn);

            modal.appendChild(title);
            modal.appendChild(info);
            modal.appendChild(actions);
            overlay.appendChild(modal);
            document.body.appendChild(overlay);

            continueBtn.addEventListener('click', () => {
                try { sessionStorage.setItem('seenRenewalModal', '1'); } catch (_) {}
                overlay.remove();
                if (typeof onContinue === 'function') onContinue();
            });
        } catch (e) {
            console.warn('Falha ao exibir modal de renovação:', e);
            if (typeof onContinue === 'function') onContinue();
        }
    }
    // Verificar se o usuário já está logado via API (mais confiável que localStorage)
    try {
        const response = await fetch('/api/me');
        if (response.ok) {
            const userData = await response.json();
            // Se pedido para permanecer na tela de login, não redirecionar
            if (suppressAutoRedirect) {
                // Calcular destino apropriado e exibir mensagem com link
                if (userData.role === 'patient') {
                    const target = userData.first_login ? '/paciente-primeiro-login.html' : '/paciente-dashboard.html';
                    showStayInfo('Você já está logado.', 'Ir para o Dashboard do Paciente', target);
                } else {
                    // Para outros usuários, usar página inicial como destino padrão
                    let target = '/index.html';
                    try {
                        const userResponse = await fetch('/api/subscriptions/my-subscription');
                        if (userResponse.ok) {
                            // Independente da assinatura, manter destino como index
                            target = '/index.html';
                        }
                    } catch (_) {}
                    showStayInfo('Você já está logado.', 'Ir para o Dashboard', target);
                }
                return;
            }
            
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

    // Helper: exibe aviso de verificação pendente + botão de reenvio
    function showVerificationPrompt(email) {
        try {
            const container = document.querySelector('.login-container');
            if (!container) return;
            // Remover bloco anterior se existir
            const existing = document.getElementById('verificationPrompt');
            if (existing) existing.remove();

            const box = document.createElement('div');
            box.id = 'verificationPrompt';
            box.style.marginTop = '16px';
            box.style.padding = '14px 16px';
            box.style.borderRadius = '10px';
            box.style.border = '1px solid #fbd38d';
            box.style.background = '#FEEBC8';
            box.style.color = '#7B341E';
            box.style.fontWeight = '600';
            box.style.textAlign = 'left';
            box.style.boxShadow = '0 4px 10px rgba(0,0,0,0.06)';

            const title = document.createElement('div');
            title.textContent = 'Seu email ainda não foi verificado.';
            title.style.marginBottom = '8px';

            const desc = document.createElement('div');
            desc.textContent = 'Confirme sua caixa de entrada ou reenvie o email de verificação.';
            desc.style.fontWeight = '500';
            desc.style.marginBottom = '12px';

            const actions = document.createElement('div');
            actions.style.display = 'flex';
            actions.style.gap = '10px';
            actions.style.alignItems = 'center';

            const emailInput = document.createElement('input');
            emailInput.type = 'email';
            emailInput.placeholder = 'seu@email.com';
            emailInput.value = (email || '').trim();
            emailInput.style.flex = '1';
            emailInput.style.padding = '10px 12px';
            emailInput.style.border = '1px solid #E2E8F0';
            emailInput.style.borderRadius = '8px';

            const resendBtn = document.createElement('button');
            resendBtn.type = 'button';
            resendBtn.textContent = 'Reenviar verificação';
            resendBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            resendBtn.style.color = '#fff';
            resendBtn.style.border = 'none';
            resendBtn.style.borderRadius = '8px';
            resendBtn.style.padding = '10px 14px';
            resendBtn.style.cursor = 'pointer';

            const feedback = document.createElement('div');
            feedback.id = 'verificationPromptFeedback';
            feedback.style.marginTop = '10px';
            feedback.style.fontWeight = '500';
            feedback.style.display = 'none';

            actions.appendChild(emailInput);
            actions.appendChild(resendBtn);

            box.appendChild(title);
            box.appendChild(desc);
            box.appendChild(actions);
            box.appendChild(feedback);
            container.appendChild(box);

            resendBtn.addEventListener('click', async function() {
                const targetEmail = (emailInput.value || '').trim();
                if (!targetEmail) {
                    feedback.style.display = 'block';
                    feedback.style.color = '#7B341E';
                    feedback.textContent = 'Informe seu email para reenviar.';
                    return;
                }
                resendBtn.disabled = true;
                const original = resendBtn.textContent;
                resendBtn.textContent = 'Enviando...';
                feedback.style.display = 'none';
                try {
                    const resp = await fetch('/api/resend-verification', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: targetEmail }),
                        credentials: 'same-origin'
                    });
                    const payload = await resp.json();
                    feedback.style.display = 'block';
                    if (resp.ok && payload && payload.success) {
                        feedback.style.color = '#22543d';
                        feedback.textContent = 'Email reenviado com sucesso. Verifique sua caixa de entrada!';
                    } else {
                        feedback.style.color = '#7B341E';
                        feedback.textContent = (payload && payload.error) ? payload.error : 'Falha ao reenviar email.';
                    }
                } catch (err) {
                    feedback.style.display = 'block';
                    feedback.style.color = '#7B341E';
                    feedback.textContent = 'Erro de conexão. Tente novamente.';
                } finally {
                    resendBtn.textContent = original;
                    resendBtn.disabled = false;
                }
            });
        } catch (e) {
            console.warn('Falha ao exibir prompt de verificação:', e);
        }
    }

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
                body: JSON.stringify({ email, password, login_scope: loginScope }),
                credentials: 'same-origin'
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
                
                // Se pedido para permanecer na tela de login, não redirecionar
                if (suppressAutoRedirect) {
                    // Restaurar botão e permanecer na página
                    button.textContent = originalText;
                    button.disabled = false;
                    // Calcular destino e mostrar mensagem com link
                    const normalizeRedirect = (path) => {
                        if (!path) return null;
                        const p = path.trim();
                        if (p === '/dashboard.html' || p === 'dashboard.html') return '/index.html';
                        return p;
                    };
                    let target = normalizeRedirect(data.redirect) || 'index.html';
                    if (loginScope === 'patient' || (data.user && data.user.role === 'patient')) {
                        target = '/paciente-dashboard.html';
                    }
                    showStayInfo('Login efetuado com sucesso.', 'Ir para o destino', target);
                    return;
                }
                
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

                // Aviso de renovação: 1 a 5 dias restantes, apenas para usuários
                console.log('[LOGIN] Usuário logado:', data.user.role, 'Verificando modal de renovação...');
                if (data && data.user && data.user.role === 'user') {
                console.log('[LOGIN] Usuário é "user", verificando assinatura...');
                // Garantir que o indicador de "já visto" não bloqueie após novo login
                try { sessionStorage.removeItem('seenRenewalModal'); } catch (_) {}
                try {
                    const urlParams = new URLSearchParams(window.location.search);
                    const forceRenewal = urlParams.get('forceRenewalModal') === '1';
                    const subResp = await fetch('/api/subscriptions/my-subscription', { credentials: 'same-origin' });
                    if (subResp.ok) {
                        const payload = await subResp.json();
                        const sub = payload && payload.subscription;
                        // Aceitar diferentes formatos e calcular por end_date como fallback
                        let days = null;
                        if (sub) {
                            if (typeof sub.days_remaining === 'number') {
                                days = sub.days_remaining;
                            } else if (typeof sub.daysRemaining === 'number') {
                                days = sub.daysRemaining;
                            } else if (sub.end_date) {
                                const end = new Date(sub.end_date);
                                const now = new Date();
                                const diffMs = end.getTime() - now.getTime();
                                days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                            }
                        }
                        const isActive = !!(sub && (sub.is_active === true || sub.status === 'active'));
                        const shouldShow = (isActive && days !== null && days >= 1 && days <= 5) || forceRenewal;
                        const alreadySeen = sessionStorage.getItem('seenRenewalModal') === '1';
                        console.log('[RenewalModal] role=user isActive=', isActive, 'days=', days, 'shouldShow=', shouldShow, 'alreadySeen=', alreadySeen, 'forceRenewal=', forceRenewal, 'payload=', payload);
                        if (shouldShow && (!alreadySeen || forceRenewal)) {
                            // Restaurar botão para estado normal antes de exibir modal
                            button.textContent = originalText;
                            button.disabled = false;
                            showRenewalModal(days, () => { window.location.href = target; });
                            return; // Não prosseguir até fechar o modal
                        }
                        if (!shouldShow) {
                            console.warn('[RenewalModal] Condições não atendidas: isActive=', isActive, 'days=', days);
                        }
                    } else {
                        console.warn('[RenewalModal] Falha na API my-subscription. Status=', subResp.status);
                    }
                } catch (e) { console.warn('[RenewalModal] erro ao obter assinatura:', e); }
                }

                // Prosseguir com redirecionamento normal
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
                
                // Caso seja bloqueio por email não verificado, mostrar prompt de reenvio
                if (data && data.need_verification) {
                    showVerificationPrompt(email);
                }

                // Tratamento genérico: para erros de credenciais (401), limpar apenas a senha
                // sem revelar qual campo está incorreto.
                if (response.status === 401) {
                    const pwdInput = document.getElementById('password');
                    if (pwdInput) pwdInput.value = '';
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

