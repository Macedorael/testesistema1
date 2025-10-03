@echo off
echo 🐳 Iniciando Consultório de Psicologia com Docker...

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está instalado. Por favor, instale o Docker primeiro.
    pause
    exit /b 1
)

REM Verificar se Docker Compose está instalado
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro.
    pause
    exit /b 1
)

REM Parar containers existentes (se houver)
echo 🛑 Parando containers existentes...
docker-compose down

REM Construir e iniciar os containers
echo 🔨 Construindo e iniciando containers...
docker-compose up --build -d

REM Aguardar alguns segundos para os serviços iniciarem
echo ⏳ Aguardando serviços iniciarem...
timeout /t 10 /nobreak >nul

REM Verificar status dos containers
echo 📊 Status dos containers:
docker-compose ps

REM Mostrar logs da aplicação
echo 📋 Logs da aplicação:
docker-compose logs app

echo.
echo ✅ Sistema iniciado com sucesso!
echo 🌐 Acesse a aplicação em: http://localhost:5000
echo 🗄️  MySQL disponível em: localhost:3306
echo.
echo 📝 Comandos úteis:
echo    - Ver logs: docker-compose logs -f
echo    - Parar sistema: docker-compose down
echo    - Reiniciar: docker-compose restart
echo    - Acessar MySQL: docker-compose exec mysql mysql -u consultorio_user -p consultorio_db
echo.
pause