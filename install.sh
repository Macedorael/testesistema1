#!/bin/bash

echo "🚀 Instalando Sistema de Consultório de Psicologia..."
echo "=================================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Erro ao criar ambiente virtual."
    exit 1
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️ Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências."
    exit 1
fi

# Inicializar banco de dados
echo "🗄️ Inicializando banco de dados..."
python src/init_db.py

if [ $? -ne 0 ]; then
    echo "❌ Erro ao inicializar banco de dados."
    exit 1
fi

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo "=================================================="
echo ""
echo "Para iniciar o sistema:"
echo "1. Execute: source venv/bin/activate"
echo "2. Execute: python src/main.py"
echo "3. Acesse: http://localhost:5000"
echo ""
echo "Ou execute o script de inicialização:"
echo "./start.sh"
echo ""

# Criar script de inicialização
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando Sistema de Consultório de Psicologia..."
source venv/bin/activate
python src/main.py
EOF

chmod +x start.sh

echo "✅ Script de inicialização criado: ./start.sh"
echo ""
echo "Deseja iniciar o sistema agora? (s/n)"
read -r response

if [[ "$response" =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando sistema..."
    python src/main.py
fi

