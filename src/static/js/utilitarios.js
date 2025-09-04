// Funções utilitárias
window.Utils = {
    
    // Verificação de autenticação
    async verificarAutenticacao() {
        try {
            const response = await fetch('/api/me', {
                method: 'GET',
                credentials: 'include'
            });
            
            if (!response.ok) {
                // Redirecionar para login se não autenticado
                window.location.href = '/entrar.html';
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('Erro ao verificar autenticação:', error);
            window.location.href = '/entrar.html';
            return false;
        }
    },
    
    // Validação de formato
    validateCPF(cpf) {
        cpf = cpf.replace(/[^\d]/g, '');
        
        if (cpf.length !== 11) return false;
        
        // Verificar CPFs inválidos conhecidos
        if (/^(\d)\1{10}$/.test(cpf)) return false;
        
        // Validar dígitos verificadores
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.charAt(9))) return false;
        
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.charAt(10))) return false;
        
        return true;
    },

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    validatePhone(phone) {
        const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
        return phoneRegex.test(phone);
    },

    // Utilitários de data
    formatDateForAPI(dateString) {
        if (!dateString) return null;
        const date = new Date(dateString);
        return date.toISOString().split('T')[0];
    },

    formatDateTimeForAPI(dateString) {
        if (!dateString) return null;
        const date = new Date(dateString);
        return date.toISOString();
    },

    addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    },

    addWeeks(date, weeks) {
        return this.addDays(date, weeks * 7);
    },

    addMonths(date, months) {
        const result = new Date(date);
        result.setMonth(result.getMonth() + months);
        return result;
    },

    // Utilitários de string
    capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    },

    truncate(str, length = 50) {
        if (!str) return '';
        return str.length > length ? str.substring(0, length) + '...' : str;
    },

    // Utilitários de número
    parseFloat(value) {
        if (typeof value === 'number') return value;
        if (typeof value === 'string') {
            // Lidar com formato de número brasileiro
            const cleaned = value.replace(/[^\d,-]/g, '').replace(',', '.');
            return parseFloat(cleaned) || 0;
        }
        return 0;
    },

    // Utilitários de formulário
    serializeForm(formElement) {
        const formData = new FormData(formElement);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    },

    clearForm(formElement) {
        const inputs = formElement.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
    },

    // Utilitários de armazenamento local
    saveToStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    },

    loadFromStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            return defaultValue;
        }
    },

    removeFromStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    },

    // Utilitários de exportação
    exportToCSV(data, filename) {
        if (!data || data.length === 0) {
            window.app.showError('Nenhum dado para exportar');
            return;
        }

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => {
                const value = row[header];
                // Escapar vírgulas e aspas
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            }).join(','))
        ].join('\n');

        this.downloadFile(csvContent, filename, 'text/csv');
    },

    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
    },

    // Utilitários de impressão
    printElement(elementId) {
        const element = document.getElementById(elementId);
        if (!element) {
            window.app.showError('Elemento não encontrado para impressão');
            return;
        }

        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Impressão</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="css/style.css" rel="stylesheet">
                <style>
                    @media print {
                        body { margin: 0; }
                        .no-print { display: none !important; }
                    }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    },

    // Utilitários de confirmação
    confirm(message, callback) {
        if (window.confirm(message)) {
            callback();
        }
    },

    // Utilitários de carregamento
    showElementLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="d-flex justify-content-center align-items-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                </div>
            `;
        }
    },

    // Utilitário de debounce
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Utilitários de tema
    definirTema(tema) {
        document.documentElement.setAttribute('data-theme', tema);
        this.saveToStorage('tema', tema);
    },

    obterTema() {
        return this.loadFromStorage('tema', 'light');
    },

    // Utilitários responsivos
    isMobile() {
        return window.innerWidth <= 768;
    },

    isTablet() {
        return window.innerWidth > 768 && window.innerWidth <= 1024;
    },

    isDesktop() {
        return window.innerWidth > 1024;
    },

    // Utilitários de animação
    fadeIn(element, duration = 300) {
        element.style.opacity = 0;
        element.style.display = 'block';
        
        const start = performance.now();
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    },

    fadeOut(element, duration = 300) {
        const start = performance.now();
        const startOpacity = parseFloat(window.getComputedStyle(element).opacity);
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = startOpacity * (1 - progress);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
            }
        }
        
        requestAnimationFrame(animate);
    }
};

// Funções globais para compatibilidade
window.verificarAutenticacao = Utils.verificarAutenticacao;
window.showLoading = function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    }
};
window.hideLoading = function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
};
window.showError = function(message) {
    alert('Erro: ' + message);
};
window.showSuccess = function(message) {
    alert('Sucesso: ' + message);
};
window.showElement = function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    }
};
window.hideElement = function(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
};
window.escapeHtml = function(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};
window.formatarData = function(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
};
window.resetarFormulario = function() {
    // Função mantida para compatibilidade
};

// Inicializar utilitários quando o DOM for carregado
document.addEventListener('DOMContentLoaded', () => {
    // Aplicar tema salvo
    const temaSalvo = Utils.obterTema();
    Utils.definirTema(temaSalvo);
    
    // Adicionar classes responsivas ao body
    function updateResponsiveClasses() {
        document.body.classList.remove('mobile', 'tablet', 'desktop');
        
        if (Utils.isMobile()) {
            document.body.classList.add('mobile');
        } else if (Utils.isTablet()) {
            document.body.classList.add('tablet');
        } else {
            document.body.classList.add('desktop');
        }
    }
    
    updateResponsiveClasses();
    window.addEventListener('resize', Utils.debounce(updateResponsiveClasses, 250));
});

