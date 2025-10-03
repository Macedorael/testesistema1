@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   🚀 DEPLOY AUTOMATICO LOCAL
echo   Sistema Consultorio de Psicologia
echo ========================================

:loop
echo.
echo [%date% %time%] 🔍 Verificando novos commits...

REM Fazer fetch do repositorio remoto
git fetch origin master 2>nul
if errorlevel 1 (
    echo [%date% %time%] ❌ Erro ao fazer fetch do repositorio
    goto wait
)

REM Verificar se ha novos commits
for /f %%i in ('git rev-list HEAD..origin/master --count 2^>nul') do set NEW_COMMITS=%%i

if "%NEW_COMMITS%"=="0" (
    echo [%date% %time%] ✅ Nenhum commit novo encontrado
    goto wait
)

echo [%date% %time%] 🎉 %NEW_COMMITS% novo(s) commit(s) encontrado(s)!
echo [%date% %time%] 📥 Fazendo pull das alteracoes...

REM Fazer pull das alteracoes
git pull origin master
if errorlevel 1 (
    echo [%date% %time%] ❌ Erro ao fazer pull das alteracoes
    goto wait
)

echo [%date% %time%] 🛑 Parando containers Docker...
docker-compose down
if errorlevel 1 (
    echo [%date% %time%] ⚠️ Aviso: Erro ao parar containers (podem nao estar rodando)
)

echo [%date% %time%] 🏗️ Fazendo build local da aplicacao (sem Docker Hub)...
docker-compose build --no-cache app
if errorlevel 1 (
    echo [%date% %time%] ❌ Erro no build da aplicacao
    goto wait
)

echo [%date% %time%] 🚀 Iniciando containers atualizados...
docker-compose up -d
if errorlevel 1 (
    echo [%date% %time%] ❌ Erro ao iniciar containers
    goto wait
)

echo [%date% %time%] ✅ Deploy local concluido com sucesso!
echo [%date% %time%] 🌐 Aplicacao disponivel em: http://localhost:5000
echo [%date% %time%] 📊 Para ver logs: docker-compose logs -f app

REM Aguardar um pouco antes de verificar novamente
timeout /t 60 /nobreak >nul

goto loop

:wait
echo [%date% %time%] ⏳ Aguardando 30 segundos antes da proxima verificacao...
timeout /t 30 /nobreak >nul
goto loop