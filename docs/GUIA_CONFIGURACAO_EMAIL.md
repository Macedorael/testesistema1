# 📧 Guia de Configuração de Email para Recuperação de Senha

Este guia te ajudará a configurar o sistema de envio de emails para a funcionalidade de recuperação de senha.

## 📋 Pré-requisitos

- Uma conta do Gmail (recomendado)
- Acesso às configurações de segurança da conta

## 🔧 Passo a Passo - Configuração Gmail

### 1. Ativar Verificação em 2 Etapas

1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá em **Segurança** no menu lateral
3. Em "Como fazer login no Google", clique em **Verificação em duas etapas**
4. Siga as instruções para ativar (necessário para senhas de app)

### 2. Gerar Senha de Aplicativo

1. Ainda na seção **Segurança**
2. Clique em **Senhas de app** (aparece após ativar 2FA)
3. Selecione **Outro (nome personalizado)**
4. Digite: `Consultorio Psicologia`
5. Clique em **Gerar**
6. **IMPORTANTE**: Copie a senha gerada (16 caracteres) - você não conseguirá vê-la novamente!

### 3. Configurar o Arquivo .env

1. **Copie o arquivo de exemplo**:
   ```bash
   copy .env.example .env
   ```

2. **Abra o arquivo .env** no seu editor de texto

3. **Configure as seguintes variáveis**:
   ```env
   # Configurações SMTP
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=seu-email@gmail.com          # ← Seu email do Gmail
   SMTP_PASSWORD=abcd efgh ijkl mnop        # ← Senha de app gerada (16 caracteres)
   
   # URL base da aplicação
   BASE_URL=http://localhost:5002
   
   # Configurações do Flask
   SECRET_KEY=minha-chave-super-secreta-123  # ← Mude para algo único
   FLASK_ENV=development
   ```

## 📝 Exemplo Prático

Se seu email for `joao.silva@gmail.com` e a senha de app gerada for `abcd efgh ijkl mnop`, seu arquivo .env ficará assim:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=joao.silva@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
BASE_URL=http://localhost:5002
SECRET_KEY=consultorio-psicologia-2024-secreto
FLASK_ENV=development
```

## 🔒 Segurança

### ⚠️ IMPORTANTE - Nunca compartilhe:
- Sua senha de aplicativo
- O arquivo `.env` (ele contém informações sensíveis)
- Adicione `.env` ao `.gitignore` se usar Git

### 🛡️ Dicas de Segurança:
- Use uma senha de app específica (não sua senha normal do Gmail)
- Mantenha o arquivo `.env` fora do controle de versão
- Troque a `SECRET_KEY` para algo único e complexo

## 🧪 Testando a Configuração

1. **Reinicie o servidor** após configurar o .env
2. **Acesse**: http://localhost:5002/static/entrar.html
3. **Clique em**: "Esqueci minha senha"
4. **Digite um email** cadastrado no sistema
5. **Verifique** se o email chegou na caixa de entrada

## 🔧 Outros Provedores de Email

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_EMAIL=seu-email@outlook.com
SMTP_PASSWORD=sua-senha-de-app
```

### Yahoo
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_EMAIL=seu-email@yahoo.com
SMTP_PASSWORD=sua-senha-de-app
```

## ❌ Problemas Comuns

### "Erro de autenticação"
- ✅ Verifique se a verificação em 2 etapas está ativada
- ✅ Confirme se está usando a senha de app (não a senha normal)
- ✅ Verifique se o email está correto

### "Conexão recusada"
- ✅ Verifique se o SMTP_SERVER e SMTP_PORT estão corretos
- ✅ Confirme se sua internet está funcionando
- ✅ Alguns antivírus podem bloquear conexões SMTP

### "Email não chega"
- ✅ Verifique a pasta de spam/lixo eletrônico
- ✅ Confirme se o email destinatário está correto
- ✅ Aguarde alguns minutos (pode haver atraso)

## 🆘 Precisa de Ajuda?

Se ainda tiver dúvidas:
1. Verifique os logs do servidor no terminal
2. Confirme se todas as configurações estão corretas
3. Teste com um email diferente

---

**✅ Após seguir este guia, seu sistema de recuperação de senha estará totalmente funcional!**