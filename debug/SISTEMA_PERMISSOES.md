# Sistema de Permissões - Consultório de Psicologia

## Roles Definidos

### 1. Admin (Administrador)
- **Descrição**: Acesso total ao sistema
- **Permissões**:
  - Gerenciar usuários (criar, editar, excluir, alterar roles)
  - Gerenciar pacientes (criar, editar, excluir, visualizar)
  - Gerenciar consultas/sessões (criar, editar, excluir, visualizar)
  - Gerenciar pagamentos (criar, editar, excluir, visualizar)
  - Acessar todos os dashboards e relatórios
  - Configurações do sistema

### 2. Psicologo (Psicólogo)
- **Descrição**: Profissional que atende os pacientes
- **Permissões**:
  - Gerenciar seus próprios pacientes (criar, editar, visualizar)
  - Gerenciar suas próprias consultas/sessões (criar, editar, visualizar)
  - Visualizar pagamentos relacionados aos seus pacientes
  - Acessar dashboard com seus dados
  - Não pode excluir registros históricos
  - Não pode gerenciar outros usuários

### 3. Secretario (Secretário/Recepcionista)
- **Descrição**: Responsável pelo atendimento e agendamentos
- **Permissões**:
  - Gerenciar pacientes (criar, editar, visualizar)
  - Gerenciar consultas/agendamentos (criar, editar, visualizar)
  - Gerenciar pagamentos (criar, editar, visualizar)
  - Acessar dashboards operacionais
  - Não pode excluir registros históricos
  - Não pode gerenciar usuários

### 4. Visualizador (Apenas Leitura)
- **Descrição**: Acesso somente para visualização
- **Permissões**:
  - Visualizar pacientes (somente leitura)
  - Visualizar consultas/sessões (somente leitura)
  - Visualizar pagamentos (somente leitura)
  - Acessar dashboards (somente leitura)
  - Não pode criar, editar ou excluir nada

## Estrutura de Implementação

### 1. Modelo de Dados
```python
# Adicionar ao modelo User:
role = db.Column(db.String(20), nullable=False, default='visualizador')

# Roles disponíveis:
ROLES = {
    'admin': 'Administrador',
    'psicologo': 'Psicólogo',
    'secretario': 'Secretário',
    'visualizador': 'Visualizador'
}
```

### 2. Mapeamento de Permissões
```python
PERMISSIONS = {
    'admin': {
        'users': ['create', 'read', 'update', 'delete'],
        'patients': ['create', 'read', 'update', 'delete'],
        'appointments': ['create', 'read', 'update', 'delete'],
        'payments': ['create', 'read', 'update', 'delete'],
        'dashboard': ['read']
    },
    'psicologo': {
        'patients': ['create', 'read', 'update'],
        'appointments': ['create', 'read', 'update'],
        'payments': ['read'],
        'dashboard': ['read']
    },
    'secretario': {
        'patients': ['create', 'read', 'update'],
        'appointments': ['create', 'read', 'update'],
        'payments': ['create', 'read', 'update'],
        'dashboard': ['read']
    },
    'visualizador': {
        'patients': ['read'],
        'appointments': ['read'],
        'payments': ['read'],
        'dashboard': ['read']
    }
}
```

### 3. Middleware de Autorização
- Decorador `@require_permission(resource, action)`
- Verificação automática baseada no role do usuário
- Retorno de erro 403 para acesso negado

### 4. Interface de Gerenciamento
- Página para administradores gerenciarem roles dos usuários
- Seletor de role no formulário de criação/edição de usuários
- Indicação visual do role atual do usuário logado

## Fluxo de Autorização

1. Usuário faz login
2. Sistema identifica o role do usuário
3. Para cada requisição, middleware verifica:
   - Se o usuário está autenticado
   - Se o role do usuário tem permissão para o recurso/ação solicitada
4. Permite ou nega o acesso baseado nas permissões

## Considerações de Segurança

- Roles são definidos no backend, não no frontend
- Verificação de permissões sempre no servidor
- Interface adapta-se dinamicamente às permissões do usuário
- Logs de acesso para auditoria (futuro)

