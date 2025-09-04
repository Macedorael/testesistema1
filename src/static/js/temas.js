// Sistema de Temas para o Consultório Médico

// Função para mudar o tema
function changeTheme(themeName) {
    // Remove o tema atual do body
    document.body.removeAttribute("data-theme");
    
    // Aplica o novo tema
    if (themeName !== "default") {
        document.body.setAttribute("data-theme", themeName);
    }
    
    // Atualiza a seleção visual no menu dropdown
    document.querySelectorAll("#theme-options-menu .theme-option").forEach(option => {
        option.classList.remove("active");
    });
    
    const selectedOption = document.querySelector(`#theme-options-menu [data-theme="${themeName}"]`);
    if (selectedOption) {
        selectedOption.classList.add("active");
    }
    
    // Salva a preferência no localStorage
    localStorage.setItem("temaSelecionado", themeName);
    
    // Mostra notificação de mudança de tema
    mostrarNotificacaoMudancaTema(themeName);
}

// Função para mostrar notificação de mudança de tema
function mostrarNotificacaoMudancaTema(themeName) {
    const themeInfo = {
        "default": { name: "Azul Padrão", icon: "bi-droplet-fill", color: "#0d6efd" },
        "green": { name: "Verde Natureza", icon: "bi-tree-fill", color: "#198754" },
        "purple": { name: "Roxo Serenidade", icon: "bi-heart-fill", color: "#6f42c1" },
        "pink": { name: "Rosa Acolhimento", icon: "bi-heart-pulse-fill", color: "#d63384" },
        "orange": { name: "Laranja Energia", icon: "bi-sun-fill", color: "#fd7e14" },
        "dark": { name: "Escuro Profissional", icon: "bi-moon-stars-fill", color: "#6c757d" }
    };
    
    const theme = themeInfo[themeName];
    
    // Remove notificações anteriores
    const existingToast = document.querySelector(".theme-toast");
    if (existingToast) {
        existingToast.remove();
    }
    
    // Cria nova notificação com estilo melhorado
    const toast = document.createElement("div");
    toast.className = "toast theme-toast show";
    toast.setAttribute("role", "alert");
    toast.style.cssText = `
        background: linear-gradient(135deg, ${theme.color}, ${theme.color}aa);
        color: white;
        border: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-radius: 12px;
    `;
    toast.innerHTML = `
        <div class="toast-header" style="background: transparent; border: none; color: white;">
            <i class="bi ${theme.icon} me-2" style="color: white; font-size: 1.2rem;"></i>
            <strong class="me-auto">Tema Alterado</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body" style="color: white;">
            <div class="d-flex align-items-center">
                <div class="theme-preview-mini me-2" style="
                    width: 16px; 
                    height: 16px; 
                    border-radius: 50%; 
                    background: linear-gradient(45deg, ${theme.color}, ${theme.color}cc);
                    border: 2px solid rgba(255,255,255,0.3);
                "></div>
                Tema alterado para: <strong>${theme.name}</strong>
            </div>
        </div>
    `;
    
    // Adiciona ao container de toasts
    const toastContainer = document.getElementById("toast-container");
    toastContainer.appendChild(toast);
    
    // Adiciona animação de entrada
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
    
    setTimeout(() => {
        toast.style.transform = "translateX(0)";
    }, 10);
    
    // Remove automaticamente após 4 segundos
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.transform = "translateX(100%)";
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }
    }, 4000);
}

// Função para carregar o tema salvo
function carregarTemaSalvo() {
    const temaSalvo = localStorage.getItem("temaSelecionado") || "default";
    
    // Aplica o tema salvo
    if (temaSalvo !== "default") {
        document.body.setAttribute("data-theme", temaSalvo);
    }
    
    // Atualiza a seleção visual no menu dropdown
    document.querySelectorAll("#theme-options-menu .theme-option").forEach(option => {
        option.classList.remove("active");
    });
    
    const opcaoSalva = document.querySelector(`#theme-options-menu [data-theme="${temaSalvo}"]`);
    if (opcaoSalva) {
        opcaoSalva.classList.add("active");
    }
}

// Função para aplicar transições suaves
function aplicarTransicoesTema() {
    const style = document.createElement("style");
    style.textContent = `
        * {
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
        }
        
        .theme-options {
            transition: opacity 0.2s ease;
        }
    `;
    document.head.appendChild(style);
}

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function() {
    // Carrega o tema salvo
    carregarTemaSalvo();
    
    // Aplica transições suaves
    aplicarTransicoesTema();
});

// Função para exportar configurações de tema (para uso futuro)
function exportarConfiguracoesTema() {
    const temaAtual = localStorage.getItem("temaSelecionado") || "default";
    return {
        tema: temaAtual,
        dataHora: new Date().toISOString()
    };
}

// Função para importar configurações de tema (para uso futuro)
function importarConfiguracoesTema(configuracoes) {
    if (configuracoes && configuracoes.tema) {
        changeTheme(configuracoes.tema);
    }
}


