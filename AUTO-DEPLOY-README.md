# 🚀 Sistema de Deploy Automático LOCAL

Este sistema monitora automaticamente o repositório GitHub e atualiza a aplicação Docker **localmente** sempre que há novos commits. **Não utiliza Docker Hub** - todo o build é feito na sua máquina.

## 📋 Componentes do Sistema

### 1. 🔔 GitHub Actions (Notificação de Commits)
**Arquivo:** `.github/workflows/docker-deploy.yml`

- ✅ Notifica sobre novos commits automaticamente
- 🔍 Valida estrutura do projeto
- 📊 Gera relatórios de commits
- 🏠 **SEM Docker Hub** - apenas notificação para deploy local

### 2. 🖥️ Scripts de Deploy Local

#### Windows: `auto-deploy.bat`
```bash
# Executa deploy automático no Windows
auto-deploy.bat
```

#### Linux/Mac: `auto-deploy.sh`
```bash
# Executa deploy automático no Linux/Mac
chmod +x auto-deploy.sh
./auto-deploy.sh
```

**Funcionalidades:**
- 📡 Verifica novos commits a cada 30 segundos
- 📥 Faz pull automático das alterações
- 🏗️ **Build LOCAL** - reconstrói apenas o container `app`
- 🚀 Reinicia aplicação atualizada
- 📝 Log detalhado de todas as operações
- 🌐 **Sem Docker Hub** - tudo local

### 3. 🔔 Servidor Webhook
**Arquivo:** `webhook-server.py`

Recebe notificações instantâneas do GitHub e executa deploy **local**:

```bash
# Instalar dependências
pip install flask requests

# Executar servidor webhook
python webhook-server.py
```

**Endpoints disponíveis:**
- `POST /webhook` - Recebe notificações do GitHub
- `GET /status` - Status do servidor
- `GET /logs` - Visualiza logs recentes

### 4. 👁️ Monitor Contínuo
**Arquivo:** `monitor-deploy.py`

Monitor inteligente com múltiplas opções para **deploy local**:

```bash
# Monitor contínuo (loop infinito)
python monitor-deploy.py

# Verificação única
python monitor-deploy.py --check-once

# Deploy forçado
python monitor-deploy.py --deploy-now
```

## 🛠️ Configuração

### 1. Configurar GitHub Actions

**Não precisa de secrets do Docker Hub!** O GitHub Actions apenas notifica sobre commits.

1. **Ativar Actions:**
   - Vá em Settings → Actions → General
   - Habilite "Allow all actions and reusable workflows"

### 2. Configurar Webhook (Opcional)

1. **No GitHub:**
   - Settings → Webhooks → Add webhook
   - URL: `http://seu-servidor:8080/webhook`
   - Content type: `application/json`
   - Secret: Configure uma senha segura

2. **No servidor:**
   ```bash
   export WEBHOOK_SECRET="sua_senha_secreta"
   export WEBHOOK_PORT=8080
   python webhook-server.py
   ```

### 3. Configurar Monitor Local

1. **Editar configurações no `monitor-deploy.py`:**
   ```python
   self.github_repo = "seu-usuario/seu-repositorio"
   self.check_interval = 60  # segundos
   ```

2. **Executar:**
   ```bash
   python monitor-deploy.py
   ```

## 🚀 Modos de Uso

### Modo 1: GitHub Actions (Apenas Notificação)
- ✅ **Notificação automática** - Informa sobre novos commits
- ✅ **Validação** - Verifica estrutura do projeto
- ✅ **Sem Docker Hub** - Não faz push para registry
- ✅ **Deploy local** - Sistemas locais detectam e fazem deploy

### Modo 2: Scripts Locais
- ✅ **Controle total** - Deploy no seu servidor
- ✅ **Build local** - Apenas `docker-compose build app`
- ✅ **Sem registry** - Não precisa de Docker Hub
- ✅ **Logs locais** - Arquivos de log detalhados
- ⚠️ **Requer servidor ativo** - Precisa estar rodando

### Modo 3: Webhook Server
- ✅ **Instantâneo** - Deploy imediato após commit
- ✅ **API REST** - Endpoints para monitoramento
- ✅ **Build local** - Sem dependência de Docker Hub
- ✅ **Seguro** - Verificação de assinatura
- ⚠️ **Requer exposição** - Servidor público necessário

### Modo 4: Monitor Contínuo
- ✅ **Inteligente** - Múltiplas estratégias de verificação
- ✅ **Resiliente** - Recupera de erros automaticamente
- ✅ **Build local** - Tudo na sua máquina
- ✅ **Flexível** - Modos de operação variados
- ⚠️ **Consome recursos** - Verificações constantes

## 📊 Monitoramento

### Logs Disponíveis:
- `deploy.log` - Logs do webhook server
- `monitor.log` - Logs do monitor contínuo
- Logs do Docker Compose
- Logs do GitHub Actions (apenas notificações)

### Comandos Úteis:
```bash
# Ver status dos containers
docker-compose ps

# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do MySQL
docker-compose logs -f mysql

# Verificar último commit
git log -1 --oneline

# Status do repositório
git status

# Build manual local
docker-compose build --no-cache app
docker-compose up -d
```

## 🔧 Troubleshooting

### Problema: Deploy não executa
**Solução:**
1. Verificar se Git está configurado
2. Verificar permissões dos scripts
3. Verificar se Docker está rodando
4. Verificar logs de erro

### Problema: Build falha
**Solução:**
1. Verificar se Dockerfile existe
2. Verificar dependências no requirements.txt
3. Executar `docker-compose build --no-cache app`
4. Verificar espaço em disco

### Problema: Webhook não funciona
**Solução:**
1. Verificar se servidor está acessível
2. Verificar secret configurado
3. Verificar logs do webhook
4. Testar endpoint `/status`

### Problema: Monitor para de funcionar
**Solução:**
1. Verificar conexão com internet
2. Verificar API rate limits do GitHub
3. Reiniciar monitor
4. Verificar logs de erro

## 🔒 Segurança

### Boas Práticas:
- ✅ Use secrets para webhook
- ✅ Configure webhook secret
- ✅ Limite acesso aos endpoints
- ✅ Monitore logs regularmente
- ✅ Use HTTPS em produção
- ✅ **Sem credenciais Docker Hub** necessárias

### Variáveis de Ambiente:
```bash
# Webhook
WEBHOOK_SECRET=sua_senha_secreta
WEBHOOK_PORT=8080

# GitHub (opcional para API)
GITHUB_TOKEN=seu_token_github
```

## 📈 Vantagens do Deploy Local

### ✅ **Sem Docker Hub:**
- Não precisa de conta Docker Hub
- Sem limites de pull/push
- Sem custos adicionais
- Sem exposição de imagens

### ✅ **Build Local:**
- Controle total do processo
- Builds mais rápidos (sem upload)
- Sem dependência de internet para deploy
- Debugging mais fácil

### ✅ **Segurança:**
- Código não sai da sua máquina
- Sem credenciais de registry
- Controle total dos dados

## 🎯 Resumo Rápido

**Para começar rapidamente:**

1. **GitHub Actions (Notificação):**
   - Faça um push → Receba notificação! 🔔

2. **Monitor Local (Recomendado):**
   ```bash
   python monitor-deploy.py
   ```

3. **Webhook (Mais Rápido):**
   ```bash
   python webhook-server.py
   ```

4. **Deploy Manual:**
   ```bash
   # Windows
   auto-deploy.bat
   
   # Linux/Mac
   ./auto-deploy.sh
   ```

**🏠 Tudo funciona localmente - sem Docker Hub necessário! 🎉**