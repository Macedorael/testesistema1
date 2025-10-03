@echo off
echo ========================================
echo   Sistema de Deploy Automatico
echo   Consultorio de Psicologia
echo ========================================
echo.

echo Escolha uma opcao:
echo.
echo 1. Instalar dependencias
echo 2. Iniciar monitor continuo
echo 3. Iniciar servidor webhook
echo 4. Executar deploy manual
echo 5. Ver status dos containers
echo 6. Ver logs da aplicacao
echo 7. Sair
echo.

set /p choice="Digite sua opcao (1-7): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto monitor
if "%choice%"=="3" goto webhook
if "%choice%"=="4" goto deploy
if "%choice%"=="5" goto status
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto exit

echo Opcao invalida!
pause
goto start

:install
echo.
echo Instalando dependencias...
pip install -r requirements-automation.txt
echo.
echo Dependencias instaladas!
pause
goto start

:monitor
echo.
echo Iniciando monitor continuo...
echo Pressione Ctrl+C para parar
python monitor-deploy.py
pause
goto start

:webhook
echo.
echo Iniciando servidor webhook na porta 8080...
echo Pressione Ctrl+C para parar
python webhook-server.py
pause
goto start

:deploy
echo.
echo Executando deploy manual...
call auto-deploy.bat
pause
goto start

:status
echo.
echo Status dos containers:
docker-compose ps
echo.
pause
goto start

:logs
echo.
echo Logs da aplicacao (Ctrl+C para sair):
docker-compose logs -f app
pause
goto start

:exit
echo.
echo Saindo...
exit

:start
cls
goto :eof