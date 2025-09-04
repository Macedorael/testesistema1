# Instruções para Usar a Tela de Login

## Visão Geral

Foi criada uma tela de login para o sistema de consultório de psicologia. A tela permite que usuários autentiquem-se no sistema usando email e senha.

## Arquivos Criados/Modificados

### Novos Arquivos:
1. `src/static/login.html` - Página HTML da tela de login
2. `src/static/css/login.css` - Estilos CSS para a tela de login
3. `src/static/js/login.js` - JavaScript para funcionalidade de login

### Arquivos Modificados:
1. `src/routes/user.py` - Adicionada rota `/api/login` para autenticação

## Como Usar

### 1. Executar o Sistema

```bash
cd consultorio-psicologia/consultorio-psicologia/consultorio-psicologia
python3.11 src/main.py
```

### 2. Acessar a Tela de Login

Abra o navegador e acesse: `http://localhost:5000/login.html`

### 3. Fazer Login

- **Email**: Use o email de um usuário cadastrado no sistema
- **Senha**: Use a senha correspondente ao usuário

#### Usuário de Teste Criado:
- **Email**: admin@teste.com
- **Senha**: 123456

### 4. Após o Login

Após um login bem-sucedido, o usuário será redirecionado automaticamente para a página principal do sistema (`index.html`).

## Funcionalidades Implementadas

1. **Validação de Formulário**: Campos obrigatórios para email e senha
2. **Autenticação Backend**: Verificação de credenciais no servidor
3. **Feedback de Erro**: Mensagens de erro são exibidas em caso de falha no login
4. **Redirecionamento**: Redirecionamento automático após login bem-sucedido
5. **Design Responsivo**: Interface adaptada para diferentes tamanhos de tela

## Estrutura da API

### Endpoint de Login
- **URL**: `/api/login`
- **Método**: POST
- **Corpo da Requisição**:
```json
{
  "email": "usuario@email.com",
  "password": "senha123"
}
```

### Respostas
- **Sucesso (200)**:
```json
{
  "message": "Login bem-sucedido!"
}
```

- **Erro (401)**:
```json
{
  "error": "Email ou senha inválidos"
}
```

## Próximos Passos (Opcionais)

Para melhorar ainda mais o sistema de login, considere implementar:

1. **Gerenciamento de Sessão**: Implementar tokens JWT ou sessões Flask
2. **Lembrar Login**: Funcionalidade "Lembrar de mim"
3. **Recuperação de Senha**: Sistema para redefinir senhas esquecidas
4. **Logout**: Funcionalidade para encerrar sessão
5. **Proteção de Rotas**: Verificar autenticação antes de acessar páginas protegidas

## Dependências

Certifique-se de que as seguintes dependências estão instaladas:
- Flask
- Flask-CORS
- Flask-SQLAlchemy
- Werkzeug (para hash de senhas)

Para instalar as dependências:
```bash
pip3 install flask flask-cors flask-sqlalchemy
```

