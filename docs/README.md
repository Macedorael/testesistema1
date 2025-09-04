# Sistema de Consultório de Psicologia

Um sistema web completo e intuitivo para gerenciamento de consultórios de psicologia, desenvolvido com Flask, Bootstrap e SQLite.

## 🎯 Funcionalidades Principais

### 1. Gestão de Pacientes (CRUD Completo)
- ✅ Cadastro de pacientes com validação de CPF
- ✅ Visualização de lista com busca e filtros
- ✅ Edição de informações pessoais
- ✅ Exclusão de pacientes
- ✅ Página de detalhes com estatísticas completas

**Campos do Paciente:**
- Nome completo
- Telefone (formatado automaticamente)
- E-mail (com validação)
- CPF (com validação)
- Data de nascimento
- Observações

### 2. Agendamento de Consultas (CRUD Completo)
- ✅ Criação de agendamentos com múltiplas sessões automáticas
- ✅ Configuração de frequência (semanal, quinzenal, mensal)
- ✅ Associação a pacientes existentes
- ✅ Visualização de agenda ordenada por data
- ✅ Edição e exclusão de agendamentos
- ✅ Página de detalhes com lista de sessões

**Campos do Agendamento:**
- Paciente associado
- Data e hora da primeira sessão
- Quantidade total de sessões
- Frequência das sessões
- Valor por sessão
- Observações

### 3. Controle de Pagamentos (CRUD Completo)
- ✅ Registro de pagamentos associados a sessões
- ✅ Seleção múltipla de sessões para pagamento
- ✅ Marcação automática de sessões como "pagas"
- ✅ Visualização de histórico de pagamentos
- ✅ Filtros por data e paciente
- ✅ Pagamento rápido direto das sessões

**Campos do Pagamento:**
- Paciente
- Sessões pagas (seleção múltipla)
- Data do pagamento
- Valor pago
- Observações

### 4. Dashboard de Acompanhamento
- ✅ Estatísticas em tempo real
- ✅ Total já recebido e a receber
- ✅ Número de agendamentos e sessões
- ✅ Gráficos de receita mensal
- ✅ Status das sessões (realizadas/pendentes/pagas)
- ✅ Próximas sessões (7 dias)

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Framework CSS:** Bootstrap 5.3.2
- **Banco de Dados:** SQLite
- **Ícones:** Bootstrap Icons
- **Gráficos:** Chart.js

## 📋 Requisitos do Sistema

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno

## 🚀 Instalação e Configuração

### 1. Clone ou baixe o projeto
```bash
# Se usando git
git clone <url-do-repositorio>
cd consultorio-psicologia

# Ou extraia o arquivo ZIP baixado
```

### 2. Crie e ative o ambiente virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Linux/Mac
source venv/bin/activate

# Ativar no Windows
venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Inicialize o banco de dados
```bash
python src/init_db.py
```

### 5. Execute o sistema
```bash
python src/main.py
```

### 6. Acesse o sistema
Abra seu navegador e acesse: `http://localhost:5000`

## 📖 Como Usar

### Primeiro Acesso
1. O sistema já vem com dados de exemplo para demonstração
2. Acesse o Dashboard para ver as estatísticas gerais
3. Navegue pelas abas para explorar as funcionalidades

### Cadastrando um Novo Paciente
1. Clique na aba "Pacientes"
2. Clique em "Novo Paciente"
3. Preencha todos os campos obrigatórios
4. O CPF e e-mail são validados automaticamente
5. Clique em "Salvar"

### Criando um Agendamento
1. Clique na aba "Agendamentos"
2. Clique em "Novo Agendamento"
3. Selecione o paciente
4. Configure a data/hora da primeira sessão
5. Defina a quantidade de sessões e frequência
6. O sistema criará automaticamente todas as sessões
7. Clique em "Salvar"

### Registrando Pagamentos
1. Clique na aba "Pagamentos"
2. Clique em "Registrar Pagamento"
3. Selecione o paciente
4. Escolha as sessões a serem pagas
5. Informe o valor e data do pagamento
6. Clique em "Registrar"

### Visualizando Detalhes
- Clique no ícone de "olho" em qualquer lista para ver detalhes completos
- Os modais mostram informações detalhadas e estatísticas
- Use os botões de ação para editar ou excluir registros

## 🎨 Interface e Design

### Características da Interface
- **Responsiva:** Funciona perfeitamente em desktop, tablet e mobile
- **Intuitiva:** Navegação simples e clara
- **Moderna:** Design limpo com Bootstrap 5
- **Acessível:** Cores contrastantes e ícones descritivos

### Cores do Sistema
- **Primária:** Azul (#007bff) - Botões principais e navegação
- **Sucesso:** Verde (#28a745) - Valores recebidos e ações positivas
- **Aviso:** Amarelo (#ffc107) - Valores pendentes e alertas
- **Perigo:** Vermelho (#dc3545) - Exclusões e erros
- **Info:** Ciano (#17a2b8) - Informações gerais

## 🔧 Estrutura do Projeto

```
consultorio-psicologia/
├── src/
│   ├── main.py                 # Aplicação principal Flask
│   ├── init_db.py             # Script de inicialização do banco
│   ├── models/                # Modelos do banco de dados
│   │   ├── user.py           # Modelo base e configuração
│   │   ├── patient.py        # Modelo de Paciente
│   │   ├── appointment.py    # Modelo de Agendamento
│   │   └── payment.py        # Modelo de Pagamento
│   ├── routes/               # Blueprints das rotas
│   │   ├── patients.py       # Rotas de pacientes
│   │   ├── appointments.py   # Rotas de agendamentos
│   │   ├── payments.py       # Rotas de pagamentos
│   │   └── dashboard.py      # Rotas do dashboard
│   └── static/               # Arquivos estáticos
│       ├── index.html        # Página principal
│       ├── css/
│       │   └── style.css     # Estilos personalizados
│       └── js/               # Scripts JavaScript
│           ├── app.js        # Aplicação principal
│           ├── dashboard.js  # Dashboard
│           ├── patients.js   # Pacientes
│           ├── appointments.js # Agendamentos
│           ├── payments.js   # Pagamentos
│           └── utils.js      # Utilitários
├── requirements.txt          # Dependências Python
├── README.md                # Esta documentação
└── venv/                    # Ambiente virtual (criado na instalação)
```

## 🔒 Segurança e Validações

### Validações Implementadas
- **CPF:** Validação completa com dígitos verificadores
- **E-mail:** Validação de formato
- **Telefone:** Formatação automática
- **Datas:** Validação de formato e consistência
- **Valores:** Validação numérica e formatação monetária

### Segurança
- Sanitização de inputs
- Validação server-side
- Prevenção de SQL injection (SQLAlchemy ORM)
- CORS configurado adequadamente

## 📊 Banco de Dados

### Estrutura das Tabelas

#### Pacientes (patients)
- id (PK)
- nome_completo
- telefone
- email
- cpf
- data_nascimento
- observacoes
- created_at

#### Agendamentos (appointments)
- id (PK)
- patient_id (FK)
- data_primeira_sessao
- quantidade_sessoes
- frequencia
- valor_por_sessao
- observacoes
- created_at

#### Sessões (sessions)
- id (PK)
- appointment_id (FK)
- numero_sessao
- data_sessao
- valor
- status
- status_pagamento
- created_at

#### Pagamentos (payments)
- id (PK)
- patient_id (FK)
- data_pagamento
- valor_pago
- observacoes
- created_at

#### Sessões-Pagamentos (payment_sessions)
- payment_id (FK)
- session_id (FK)

## 🚀 Funcionalidades Avançadas

### Criação Automática de Sessões
O sistema calcula automaticamente as datas das sessões baseado na:
- Data da primeira sessão
- Frequência escolhida (semanal = 7 dias, quinzenal = 14 dias, mensal = 30 dias)
- Quantidade total de sessões

### Estatísticas em Tempo Real
- Cálculos automáticos de valores recebidos e a receber
- Contagem de sessões por status
- Gráficos dinâmicos de receita mensal
- Próximas sessões dos próximos 7 dias

### Filtros e Buscas
- Busca de pacientes por nome
- Filtros de agendamentos por status e paciente
- Filtros de pagamentos por data e paciente
- Ordenação automática por data

## 🔧 Personalização

### Modificando Cores
Edite o arquivo `src/static/css/style.css` para alterar as cores do sistema.

### Adicionando Campos
1. Modifique o modelo correspondente em `src/models/`
2. Execute `python src/init_db.py` para recriar o banco
3. Atualize os formulários em `src/static/js/`

### Configurando Frequências
Edite a lista de frequências em `src/static/js/appointments.js`.

## 🐛 Solução de Problemas

### Erro ao Iniciar o Servidor
- Verifique se o ambiente virtual está ativado
- Confirme se todas as dependências estão instaladas
- Verifique se a porta 5000 não está em uso

### Banco de Dados Corrompido
- Execute novamente `python src/init_db.py`
- Isso recriará o banco com dados de exemplo

### Problemas de Formatação
- Limpe o cache do navegador
- Verifique se os arquivos CSS e JS estão sendo carregados

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique esta documentação
2. Consulte os logs do servidor no terminal
3. Verifique o console do navegador (F12) para erros JavaScript

## 📝 Licença

Este projeto foi desenvolvido para uso em consultórios de psicologia. Todos os direitos reservados.

---

**Desenvolvido com ❤️ para profissionais da psicologia**

