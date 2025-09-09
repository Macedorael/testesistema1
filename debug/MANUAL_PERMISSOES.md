# Manual do Sistema de Permissões - Consultório de Psicologia

## Visão Geral

O sistema de permissões foi implementado para controlar o acesso dos usuários às diferentes funcionalidades do sistema. Cada usuário possui um **role** (papel) que define suas permissões de acesso.

## Roles Disponíveis

### 1. Administrador
- **Acesso total** ao sistema
- Pode gerenciar usuários (criar, editar, excluir, alterar roles)
- Pode gerenciar pacientes, consultas e pagamentos
- Acesso a todos os dashboards e relatórios

### 2. Psicólogo
- Pode gerenciar seus próprios pacientes
- Pode gerenciar suas próprias consultas/sessões
- Pode visualizar pagamentos relacionados aos seus pacientes
- Acesso ao dashboard com seus dados
- **Não pode** excluir registros históricos ou gerenciar outros usuários

### 3. Secretário
- Pode gerenciar pacientes (criar, editar, visualizar)
- Pode gerenciar consultas/agendamentos
- Pode gerenciar pagamentos
- Acesso aos dashboards operacionais
- **Não pode** excluir registros históricos ou gerenciar usuários

### 4. Visualizador
- **Apenas leitura** em todas as funcionalidades
- Pode visualizar pacientes, consultas, pagamentos e dashboards
- **Não pode** criar, editar ou excluir nada

## Como Usar

### Login Inicial
- **Usuário Administrador Padrão:**
  - Email: `admin@consultorio.com`
  - Senha: `admin123`

### Gerenciamento de Usuários (Apenas Administradores)

1. **Acessar Gerenciamento:**
   - Faça login como administrador
   - Clique em "Usuários" no menu lateral

2. **Criar Novo Usuário:**
   - Clique em "Novo Usuário"
   - Preencha os dados obrigatórios
   - Selecione o role apropriado
   - Clique em "Salvar"

3. **Alterar Role de Usuário:**
   - Na lista de usuários, clique no botão "Alterar Role" (ícone de escudo)
   - Selecione o novo role
   - Confirme a alteração

4. **Filtrar Usuários:**
   - Use o campo de busca para encontrar usuários específicos
   - Use o filtro por role para visualizar usuários de um tipo específico

### Indicadores Visuais

- **Badges de Role:** Cada usuário possui um badge colorido indicando seu role:
  - 🔴 Administrador (vermelho)
  - 🔵 Psicólogo (azul)
  - 🟡 Secretário (amarelo)
  - ⚫ Visualizador (cinza)

- **Menu Adaptativo:** O menu lateral se adapta às permissões do usuário logado
- **Botões Desabilitados:** Funcionalidades sem permissão aparecem desabilitadas

## Segurança

### Verificações Implementadas
- ✅ Autenticação obrigatória para todas as funcionalidades
- ✅ Verificação de permissões no backend (servidor)
- ✅ Interface adaptativa baseada nas permissões
- ✅ Sessões seguras com timeout automático

### Boas Práticas
- Sempre faça logout ao terminar de usar o sistema
- Use senhas fortes (mínimo 6 caracteres)
- Revise periodicamente as permissões dos usuários
- Mantenha apenas um usuário administrador ativo por vez

## Troubleshooting

### Problemas Comuns

**"Acesso negado" ao tentar acessar uma página:**
- Verifique se seu role tem permissão para essa funcionalidade
- Entre em contato com o administrador para revisar suas permissões

**Não consigo ver o menu "Usuários":**
- Apenas administradores podem gerenciar usuários
- Se você deveria ser administrador, entre em contato com outro admin

**Esqueci minha senha:**
- Entre em contato com o administrador do sistema
- O administrador pode redefinir sua senha

## Migração e Atualização

### Para Sistemas Existentes
1. Execute o script de migração: `python3 src/migrate_db.py`
2. O script criará automaticamente:
   - Campo 'role' para usuários existentes (padrão: visualizador)
   - Usuário administrador padrão se não existir

### Backup
- Sempre faça backup do banco de dados antes de atualizações
- O arquivo do banco está em: `src/database/app.db`

## Suporte Técnico

Para dúvidas ou problemas:
1. Consulte este manual
2. Verifique os logs do sistema
3. Entre em contato com o administrador técnico

---

**Versão:** 1.0  
**Data:** Julho 2025  
**Desenvolvido por:** Sistema de Consultório de Psicologia

