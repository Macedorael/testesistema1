// Modal Fix JavaScript
// Corrige problemas de renderização dos botões de cancelar e modais

document.addEventListener('DOMContentLoaded', function() {
    // Fix para modais que não renderizam corretamente após cancelar
    document.addEventListener('hidden.bs.modal', function (event) {
        // Remove backdrop residual
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Remove modal-open class do body
        document.body.classList.remove('modal-open');
        
        // Restaura scroll do body
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Remove modal do DOM para evitar conflitos
        const modal = event.target;
        if (modal && modal.id && modal.id.includes('Modal')) {
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300);
        }
    });
    
    // Fix para botões de cancelar que não funcionam corretamente
    document.addEventListener('click', function(event) {
        const target = event.target;
        
        // Se é um botão de cancelar ou fechar modal
        if (target.matches('[data-bs-dismiss="modal"]') || 
            target.closest('[data-bs-dismiss="modal"]')) {
            
            const button = target.matches('[data-bs-dismiss="modal"]') ? 
                          target : target.closest('[data-bs-dismiss="modal"]');
            
            const modal = button.closest('.modal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                } else {
                    // Fallback: criar nova instância e fechar
                    const newModalInstance = new bootstrap.Modal(modal);
                    newModalInstance.hide();
                }
            }
        }
    });
    
    // Fix para ESC key não funcionando em modais
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length > 0) {
                const lastModal = openModals[openModals.length - 1];
                const modalInstance = bootstrap.Modal.getInstance(lastModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
    });
    
    // Fix para overlay click não funcionando
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            const modalInstance = bootstrap.Modal.getInstance(event.target);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    });
    
    // Fix específico para problema de blur e página não responsiva
    document.addEventListener('click', function(event) {
        // Se clicou no backdrop do modal
        if (event.target.classList.contains('modal-backdrop')) {
            // Encontra o modal ativo
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                const modalInstance = bootstrap.Modal.getInstance(activeModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
            // Force remove backdrop se ainda existir
            setTimeout(() => {
                const remainingBackdrops = document.querySelectorAll('.modal-backdrop');
                remainingBackdrops.forEach(backdrop => {
                    backdrop.remove();
                });
                // Restaura funcionalidade da página
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }, 100);
        }
    });
    
    // Previne múltiplos modais abertos simultaneamente
    document.addEventListener('show.bs.modal', function (event) {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            if (modal !== event.target) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        });
    });
    
    // Fix para formulários em modais
    document.addEventListener('submit', function(event) {
        const form = event.target;
        if (form.closest('.modal')) {
            // Previne submit duplo
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                setTimeout(() => {
                    submitButton.disabled = false;
                }, 2000);
            }
        }
    });
    
    // Limpa campos de formulário quando modal é fechado
    document.addEventListener('hidden.bs.modal', function (event) {
        const modal = event.target;
        const forms = modal.querySelectorAll('form');
        forms.forEach(form => {
            // Reset apenas se não for um modal de edição
            if (!modal.querySelector('[data-edit-mode="true"]')) {
                form.reset();
                
                // Limpa validações do Bootstrap
                form.classList.remove('was-validated');
                const invalidInputs = form.querySelectorAll('.is-invalid');
                invalidInputs.forEach(input => input.classList.remove('is-invalid'));
                
                const validInputs = form.querySelectorAll('.is-valid');
                validInputs.forEach(input => input.classList.remove('is-valid'));
            }
        });
    });
    
    // Fix para z-index de modais aninhados
    let modalZIndex = 1050;
    document.addEventListener('show.bs.modal', function (event) {
        const modal = event.target;
        modalZIndex += 10;
        modal.style.zIndex = modalZIndex;
        
        // Ajusta backdrop também
        setTimeout(() => {
            const backdrop = document.querySelector('.modal-backdrop:last-child');
            if (backdrop) {
                backdrop.style.zIndex = modalZIndex - 1;
            }
        }, 100);
    });
    
    // Reset z-index quando todos os modais são fechados
    document.addEventListener('hidden.bs.modal', function (event) {
        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length === 0) {
            modalZIndex = 1050;
        }
    });
    
    // Fix para página travada - verifica periodicamente se há problemas
    setInterval(function() {
        const hasModalOpen = document.body.classList.contains('modal-open');
        const activeModals = document.querySelectorAll('.modal.show');
        const backdrops = document.querySelectorAll('.modal-backdrop');
        
        // Se o body tem modal-open mas não há modais ativos, limpa tudo
        if (hasModalOpen && activeModals.length === 0) {
            console.log('Detectado problema de modal travado - limpando...');
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            // Remove backdrops órfãos
            backdrops.forEach(backdrop => backdrop.remove());
        }
        
        // Se há backdrops mas não há modais ativos, remove os backdrops
        if (backdrops.length > 0 && activeModals.length === 0) {
            console.log('Removendo backdrops órfãos...');
            backdrops.forEach(backdrop => backdrop.remove());
        }
    }, 1000); // Verifica a cada segundo
    
    // Adiciona botão de emergência para destravar página (Ctrl+Alt+M)
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.altKey && event.key === 'm') {
            console.log('Atalho de emergência ativado - limpando todos os modais...');
            
            // Remove todos os modais e backdrops
            const allModals = document.querySelectorAll('.modal');
            const allBackdrops = document.querySelectorAll('.modal-backdrop');
            
            allModals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
                modal.remove();
            });
            
            allBackdrops.forEach(backdrop => backdrop.remove());
            
            // Restaura estado normal da página
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            // Mostra confirmação
            alert('Página destravada! Todos os modais foram fechados.');
        }
    });
});

