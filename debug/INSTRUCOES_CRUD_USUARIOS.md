# Sistema CRUD de Usuários - Consultório de Psicologia

## 📋 Visão Geral

Este documento descreve o sistema CRUD (Create, Read, Update, Delete) de usuários implementado no sistema de consultório de psicologia. O sistema permite o cadastro e gerenciamento de usuários com senhas criptografadas, preparando a base para futuro controle de acesso.

## 🚀 Funcionalidades Implementadas

### ✅ CRUD Completo de Usuários
- **Criar**: Cadastro de novos usuários com validação
- **Ler**: Listagem e visualização de usuários
- **Atualizar**: Edição de dados dos usuários
- **Excluir**: Remoção de usuários do sistema

### 🔐 Segurança
- Senhas criptografadas usando Werkzeug
- Validação de campos obrigatórios
- Verificação de unicidade de username e email
- Validação de força da senha (mínimo 6 caracteres)

### 🎨 Interface de Usuário
- Interface responsiva com Bootstrap 5
- Modais para criação, edição e visualização
- Sistema de notificações (toasts)
- Busca e filtros em tempo real
- Ícones intuitivos para ações

## 📁 Estrutura dos Arquivos

### Backend (Python/Flask)
```
src/
├── models/
│   └── user.py              # Modelo de usuário com criptografia
├── routes/
│   └── user.py              # Rotas da API REST para usuários
└── main.py                  # Aplicação principal (já registra as rotas)
```

### Frontend (HTML/CSS/JavaScript)
```
src/static/
├── index.html               # Página principal (aba Usuários adicionada)
└── js/
    ├── users.js             # Lógica específica para usuários
    └── app.js               # Funções utilitárias (showToast, showLoading)
```

## 🔧 Instalação e Execução

### 1. Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 2. Instalação
```bash
# Navegar para o diretório do projeto
cd consultorio-psicologia

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados (se necessário)
python src/init_db.py
```

### 3. Execução
```bash
# Iniciar o servidor
python src/main.py

# Acessar no navegador
http://localhost:5000
```

## 📖 Como Usar o Sistema de Usuários

### Acessando a Seção de Usuários
1. Abra o sistema no navegador
2. Clique na aba "Usuários" no menu superior
3. A página de gerenciamento será carregada

### Criando um Novo Usuário
1. Clique no botão "Novo Usuário"
2. Preencha os campos obrigatórios:
   - Nome de Usuário (único)
   - Email (único)
   - Senha (mínimo 6 caracteres)
   - Confirmar Senha
3. Clique em "Salvar"
4. Uma notificação de sucesso será exibida

### Visualizando Usuários
- A lista de usuários é carregada automaticamente
- Use o campo de busca para filtrar por nome ou email
- Clique no ícone de "olho" para ver detalhes completos

### Editando um Usuário
1. Clique no ícone de "lápis" na linha do usuário
2. Modifique os campos desejados
3. Para alterar a senha, preencha os campos de nova senha
4. Clique em "Salvar Alterações"

### Excluindo um Usuário
1. Clique no ícone de "lixeira" na linha do usuário
2. Confirme a exclusão no modal de confirmação
3. O usuário será removido permanentemente

## 🔌 API REST

### Endpoints Disponíveis

#### GET /api/users
- **Descrição**: Lista todos os usuários
- **Resposta**: Array de objetos usuário (sem senhas)

#### POST /api/users
- **Descrição**: Cria um novo usuário
- **Body**: 
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
- **Validações**:
  - Username único
  - Email único e válido
  - Senha obrigatória

#### GET /api/users/{id}
- **Descrição**: Obtém um usuário específico
- **Resposta**: Objeto usuário (sem senha)

#### PUT /api/users/{id}
- **Descrição**: Atualiza um usuário
- **Body**: 
```json
{
  "username": "string",
  "email": "string",
  "password": "string" // opcional
}
```

#### DELETE /api/users/{id}
- **Descrição**: Remove um usuário
- **Resposta**: Status 204 (No Content)

## 🗄️ Estrutura do Banco de Dados

### Tabela: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128)
);
```

### Campos
- **id**: Chave primária auto-incremento
- **username**: Nome de usuário único
- **email**: Email único
- **password_hash**: Senha criptografada (nunca armazenada em texto plano)

## 🔐 Segurança Implementada

### Criptografia de Senhas
- Utiliza `werkzeug.security.generate_password_hash()`
- Algoritmo seguro com salt automático
- Verificação com `check_password_hash()`

### Validações Backend
- Campos obrigatórios verificados
- Unicidade de username e email
- Sanitização de dados de entrada

### Validações Frontend
- Confirmação de senha
- Validação de força da senha
- Feedback visual para erros

## 🚀 Próximos Passos (Controle de Acesso)

### Funcionalidades Planejadas
1. **Sistema de Login**
   - Tela de login
   - Autenticação de usuários
   - Sessões seguras

2. **Controle de Permissões**
   - Níveis de acesso (admin, usuário)
   - Proteção de rotas
   - Middleware de autenticação

3. **Gestão de Sessões**
   - Login/logout
   - Timeout de sessão
   - Lembrança de login

### Preparação Atual
- Modelo de usuário já suporta autenticação
- Senhas criptografadas
- API REST funcional
- Interface de gerenciamento completa

## 🐛 Solução de Problemas

### Erro: "Usuário não foi criado"
- Verifique se todos os campos estão preenchidos
- Confirme se username e email são únicos
- Verifique se a senha tem pelo menos 6 caracteres

### Erro: "Página não carrega"
- Confirme se o servidor Flask está rodando
- Verifique se a porta 5000 está disponível
- Limpe o cache do navegador

### Erro: "Funções JavaScript não funcionam"
- Verifique se todos os arquivos JS estão carregados
- Abra o console do navegador (F12) para ver erros
- Confirme se o Bootstrap está carregado

## 📞 Suporte Técnico

### Logs do Sistema
- Logs do Flask aparecem no terminal
- Erros JavaScript no console do navegador (F12)
- Erros de rede na aba Network do navegador

### Arquivos de Configuração
- `requirements.txt`: Dependências Python
- `src/main.py`: Configuração principal
- `src/static/js/app.js`: Configurações frontend

## 📝 Notas de Desenvolvimento

### Tecnologias Utilizadas
- **Backend**: Flask, SQLAlchemy, Werkzeug
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **Banco**: SQLite (desenvolvimento)
- **Segurança**: Werkzeug Security

### Padrões Seguidos
- API REST com códigos HTTP apropriados
- Separação de responsabilidades (MVC)
- Validação dupla (frontend + backend)
- Interface responsiva
- Código limpo e documentado

---

**Sistema desenvolvido para controle de acesso ao consultório de psicologia**
*Versão 1.0 - Janeiro 2025*

