# 🚀 Deploy no Render - Consultório de Psicologia

Este guia te ajudará a fazer o deploy da aplicação no Render.com.

## 📋 Pré-requisitos

- Conta no [Render.com](https://render.com)
- Repositório Git (GitHub, GitLab ou Bitbucket)
- Código da aplicação commitado no repositório

## 🔧 Passo a Passo

### 1. Preparar o Repositório

1. **Commit todos os arquivos**:
   ```bash
   git add .
   git commit -m "Preparar para deploy no Render"
   git push origin main
   ```

2. **Verificar arquivos essenciais**:
   - ✅ `requirements.txt` (com dependências de produção)
   - ✅ `render.yaml` (configuração do Render)
   - ✅ `build.sh` (script de build)
   - ✅ `.env.example` (exemplo de variáveis)

### 2. Criar Serviços no Render

#### 2.1 Criar Banco de Dados PostgreSQL

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `consultorio-db`
   - **Database Name**: `consultorio_psicologia`
   - **User**: `consultorio_user`
   - **Region**: `Oregon (US West)`
   - **Plan**: `Free`
4. Clique em **"Create Database"**
5. **Anote a URL de conexão** (será usada depois)

#### 2.2 Criar Web Service

1. Clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório Git
3. Configure:
   - **Name**: `consultorio-psicologia`
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`
   - **Plan**: `Free`

### 3. Configurar Variáveis de Ambiente

Na página do seu Web Service, vá em **"Environment"** e adicione:

```env
# Configurações Básicas
PYTHON_VERSION=3.11.0
FLASK_ENV=production

# Banco de Dados (será preenchido automaticamente)
DATABASE_URL=[URL do PostgreSQL criado]

# Segurança (gerar chave secreta)
SECRET_KEY=[chave-secreta-gerada]

# Configurações de Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=[seu-email@gmail.com]
SMTP_PASSWORD=[sua-senha-de-app]

# URL da Aplicação (será preenchida após deploy)
BASE_URL=https://consultorio-psicologia.onrender.com
```

### 4. Configurar Email (Gmail)

#### 4.1 Ativar Verificação em 2 Etapas
1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá em **Segurança** → **Verificação em duas etapas**
3. Siga as instruções para ativar

#### 4.2 Gerar Senha de App
1. Em **Segurança** → **Senhas de app**
2. Selecione **Outro** → Digite: `Consultorio Render`
3. **Copie a senha gerada** (16 caracteres)
4. Use esta senha na variável `MAIL_PASSWORD`

### 5. Deploy

1. **Conectar Banco de Dados**:
   - No Web Service, vá em **"Environment"
   - Em `DATABASE_URL`, selecione o banco criado

2. **Deploy Automático**:
   - O Render fará o deploy automaticamente
   - Acompanhe os logs em **"Logs"**

3. **Verificar Deploy**:
   - Aguarde o status ficar **"Live"**
   - Acesse a URL fornecida pelo Render

## 🧪 Testando a Aplicação

### Funcionalidades para Testar:

1. **Página Inicial**: `https://seu-app.onrender.com`
2. **Login**: Teste com usuário admin
3. **Cadastro**: Criar novo usuário
4. **Recuperação de Senha**: Testar envio de email
5. **CRUD Pacientes**: Criar, editar, listar
6. **Agendamentos**: Criar consultas
7. **Sistema de Assinaturas**: Verificar planos

### Usuário Admin Padrão:
- **Email**: `admin@teste.com`
- **Senha**: `123456`

## 🔧 Configurações Avançadas

### Domínio Personalizado
1. No Web Service → **"Settings"** → **"Custom Domains"
2. Adicione seu domínio
3. Configure DNS conforme instruções

### Monitoramento
- **Logs**: Acompanhe em tempo real
- **Metrics**: CPU, memória, requests
- **Alerts**: Configure notificações

## 🚨 Troubleshooting

### Problemas Comuns:

#### Build Falha
- Verifique `requirements.txt`
- Confirme se `build.sh` tem permissões
- Veja logs detalhados

#### Banco de Dados
- Confirme URL de conexão
- Verifique se PostgreSQL está ativo
- Teste conexão local primeiro

#### Email não Funciona
- Confirme senha de app do Gmail
- Verifique variáveis de ambiente
- Teste com email diferente

#### Aplicação não Carrega
- Verifique porta (deve usar `$PORT`)
- Confirme comando de start
- Veja logs de erro

### Comandos Úteis:

```bash
# Ver logs em tempo real
render logs --service=consultorio-psicologia --follow

# Redeploy manual
render deploy --service=consultorio-psicologia

# Conectar ao banco
render psql consultorio-db
```

## 📊 Monitoramento

### Métricas Importantes:
- **Response Time**: < 2s
- **Memory Usage**: < 512MB
- **CPU Usage**: < 80%
- **Error Rate**: < 1%

### Logs para Monitorar:
- Erros de autenticação
- Falhas de email
- Erros de banco de dados
- Requests 404/500

## 🔒 Segurança

### Checklist de Segurança:
- ✅ SECRET_KEY única e complexa
- ✅ Variáveis sensíveis em Environment
- ✅ HTTPS habilitado (automático no Render)
- ✅ Banco de dados com credenciais seguras
- ✅ Email com senha de app

## 📈 Otimizações

### Performance:
- Use CDN para assets estáticos
- Configure cache headers
- Otimize queries do banco
- Monitore tempo de resposta

### Custos:
- Plan Free: 750 horas/mês
- Upgrade conforme necessário
- Monitore uso de recursos

---

## 🎉 Deploy Concluído!

Sua aplicação está agora rodando em produção no Render!

**URL da Aplicação**: `https://consultorio-psicologia.onrender.com`

### Próximos Passos:
1. Configure domínio personalizado (opcional)
2. Configure backups do banco
3. Monitore performance
4. Configure alertas

---

**📞 Suporte**: Se precisar de ajuda, consulte a [documentação do Render](https://render.com/docs) ou abra um ticket de suporte.