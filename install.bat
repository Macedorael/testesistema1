@echo off
chcp 65001 >nul
echo 🚀 Instalando Sistema de Consultório de Psicologia...
echo ==================================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale o Python 3.8 ou superior.
    echo Baixe em: https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version

REM Criar ambiente virtual
echo 📦 Criando ambiente virtual...
python -m venv venv

if errorlevel 1 (
    echo ❌ Erro ao criar ambiente virtual.
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
echo ⬆️ Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências
echo 📚 Instalando dependências...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências.
    pause
    exit /b 1
)

REM Inicializar banco de dados
echo 🗄️ Inicializando banco de dados...
python src\init_db.py

if errorlevel 1 (
    echo ❌ Erro ao inicializar banco de dados.
    pause
    exit /b 1
)

echo.
echo 🎉 Instalação concluída com sucesso!
echo ==================================================
echo.
echo Para iniciar o sistema:
echo 1. Execute: venv\Scripts\activate.bat
echo 2. Execute: python src\main.py
echo 3. Acesse: http://localhost:5000
echo.
echo Ou execute o script de inicialização:
echo start.bat
echo.

REM Criar script de inicialização
echo @echo off > start.bat
echo chcp 65001 ^>nul >> start.bat
echo echo 🚀 Iniciando Sistema de Consultório de Psicologia... >> start.bat
echo call venv\Scripts\activate.bat >> start.bat
echo python src\main.py >> start.bat
echo pause >> start.bat

echo ✅ Script de inicialização criado: start.bat
echo.
echo Deseja iniciar o sistema agora? (s/n)
set /p response=

if /i "%response%"=="s" (
    echo 🚀 Iniciando sistema...
    python src\main.py
)

pause

