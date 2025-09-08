# Deploy Automático com Migração

## Visão Geral

Este sistema implementa um deploy automático que executa a migração da coluna `user_id` nas tabelas `funcionarios` e `especialidades` durante o processo de deploy, garantindo que a aplicação funcione corretamente em produção sem intervenção manual.

## Arquivos Criados/Modificados

### 1. `deploy_migration.py`
**Novo arquivo** - Script principal de migração automática que:
- Detecta automaticamente o tipo de banco de dados (PostgreSQL/SQLite)
- Verifica se as tabelas `funcionarios` e `especialidades` existem
- Verifica se a coluna `user_id` já existe em cada tabela
- Adiciona a coluna `user_id` se necessário em ambas as tabelas
- Cria foreign key constraint (PostgreSQL)
- Atualiza registros existentes com `user_id = 1` em ambas as tabelas
- Verifica se a migração foi aplicada corretamente em ambas as tabelas
- Instala dependências automaticamente

### 2. `build.sh` (Modificado)
**Arquivo atualizado** - Script de build do Render.com que agora:
- Executa `deploy_migration.py` antes da inicialização do banco
- Garante que a migração seja aplicada em cada deploy
- Continua o processo normal mesmo se a migração não for necessária

## Como Funciona

### Durante o Deploy

1. **Instalação de Dependências**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. **Execução da Migração Automática**
   ```bash
   python3 deploy_migration.py
   ```
   - Conecta ao banco de dados de produção
   - Verifica estrutura atual
   - Aplica migração se necessário
   - Valida resultado

3. **Inicialização Normal do Banco**
   ```bash
   python3 -c "from src.main import app, db; app.app_context().push(); db.create_all()"
   ```

4. **Continuação do Deploy Normal**
   - Criação de usuário admin
   - Correções de bugs
   - População de dados de exemplo (se necessário)

### Detecção de Ambiente

- **Produção**: Usa `DATABASE_URL` (PostgreSQL no Render.com)
- **Desenvolvimento**: Usa `sqlite:///src/database/app.db`

### Segurança da Migração

✅ **Idempotente**: Pode ser executada múltiplas vezes sem problemas
✅ **Não destrutiva**: Apenas adiciona coluna, não remove dados
✅ **Verificação prévia**: Checa se migração é necessária
✅ **Rollback seguro**: Falha graciosamente se houver problemas
✅ **Logs detalhados**: Registra cada etapa do processo

## Logs de Exemplo

### Primeira Execução (Migração Necessária)
```
2025-01-08 10:30:00 - INFO - === INICIANDO DEPLOY COM MIGRAÇÃO AUTOMÁTICA ===
2025-01-08 10:30:01 - INFO - Usando DATABASE_URL de produção: postgresql://...
2025-01-08 10:30:02 - INFO - Conexão com banco de dados estabelecida
2025-01-08 10:30:03 - INFO - === INICIANDO MIGRAÇÃO DE COLUNAS USER_ID ===
2025-01-08 10:30:04 - INFO - Migrando tabela: funcionarios
2025-01-08 10:30:05 - INFO - Tabela 'funcionarios' existe
2025-01-08 10:30:06 - INFO - Coluna 'user_id' na tabela 'funcionarios' não existe
2025-01-08 10:30:07 - INFO - Iniciando migração: adicionando coluna 'user_id' na tabela 'funcionarios'
2025-01-08 10:30:08 - INFO - Detectado PostgreSQL - executando migração para funcionarios
2025-01-08 10:30:09 - INFO - Atualizados 6 registros em funcionarios com user_id = 1
2025-01-08 10:30:10 - INFO - Migração da tabela funcionarios concluída com sucesso!
2025-01-08 10:30:11 - INFO - Migrando tabela: especialidades
2025-01-08 10:30:12 - INFO - Tabela 'especialidades' existe
2025-01-08 10:30:13 - INFO - Coluna 'user_id' na tabela 'especialidades' não existe
2025-01-08 10:30:14 - INFO - Iniciando migração: adicionando coluna 'user_id' na tabela 'especialidades'
2025-01-08 10:30:15 - INFO - Detectado PostgreSQL - executando migração para especialidades
2025-01-08 10:30:16 - INFO - Atualizados 4 registros em especialidades com user_id = 1
2025-01-08 10:30:17 - INFO - Migração da tabela especialidades concluída com sucesso!
2025-01-08 10:30:18 - INFO - === VERIFICANDO MIGRAÇÕES ===
2025-01-08 10:30:19 - INFO - Verificação: 6 funcionários total, 6 com user_id, 0 com user_id NULL
2025-01-08 10:30:20 - INFO - Verificação: 4 especialidades total, 4 com user_id, 0 com user_id NULL
2025-01-08 10:30:21 - INFO - === MIGRAÇÃO CONCLUÍDA COM SUCESSO ===
```

### Execuções Subsequentes (Migração Não Necessária)
```
2025-01-08 11:00:00 - INFO - === INICIANDO DEPLOY COM MIGRAÇÃO AUTOMÁTICA ===
2025-01-08 11:00:01 - INFO - Usando DATABASE_URL de produção: postgresql://...
2025-01-08 11:00:02 - INFO - Conexão com banco de dados estabelecida
2025-01-08 11:00:03 - INFO - === INICIANDO MIGRAÇÃO DE COLUNAS USER_ID ===
2025-01-08 11:00:04 - INFO - Migrando tabela: funcionarios
2025-01-08 11:00:05 - INFO - Tabela 'funcionarios' existe
2025-01-08 11:00:06 - INFO - Coluna 'user_id' já existe na tabela 'funcionarios'. Migração não necessária.
2025-01-08 11:00:07 - INFO - Migrando tabela: especialidades
2025-01-08 11:00:08 - INFO - Tabela 'especialidades' existe
2025-01-08 11:00:09 - INFO - Coluna 'user_id' já existe na tabela 'especialidades'. Migração não necessária.
2025-01-08 11:00:10 - INFO - === VERIFICANDO MIGRAÇÕES ===
2025-01-08 11:00:11 - INFO - Verificação: 6 funcionários total, 6 com user_id, 0 com user_id NULL
2025-01-08 11:00:12 - INFO - Verificação: 4 especialidades total, 4 com user_id, 0 com user_id NULL
2025-01-08 11:00:13 - INFO - === MIGRAÇÃO CONCLUÍDA COM SUCESSO ===
```

## Vantagens

1. **Automático**: Não requer intervenção manual
2. **Seguro**: Múltiplas verificações e validações
3. **Flexível**: Funciona com PostgreSQL e SQLite
4. **Transparente**: Logs detalhados de cada etapa
5. **Robusto**: Trata erros graciosamente
6. **Eficiente**: Só executa quando necessário

## Próximos Deploys

Agora, sempre que você fizer um deploy:

1. **Faça suas alterações normalmente**
2. **Commit e push para o repositório**
3. **O Render.com executará automaticamente**:
   - Build da aplicação
   - Migração automática (se necessária)
   - Inicialização do banco
   - Start da aplicação

## Monitoramento

Para verificar se a migração foi aplicada corretamente em produção:

1. **Verifique os logs do deploy no Render.com**
2. **Procure por mensagens como**:
   - `=== MIGRAÇÃO CONCLUÍDA COM SUCESSO ===`
   - `Coluna 'user_id' já existe na tabela 'funcionarios'`

3. **Teste a funcionalidade**:
   - Acesse a página de funcionários
   - Verifique se os funcionários são exibidos corretamente
   - Confirme que cada usuário vê apenas seus próprios funcionários

## Resolução de Problemas

Se houver problemas durante a migração:

1. **Verifique os logs do deploy**
2. **Procure por mensagens de erro**
3. **A aplicação continuará funcionando** (migração não bloqueia o deploy)
4. **Execute manualmente se necessário**:
   ```bash
   python3 migrate_add_user_id_funcionarios.py
   ```

## Conclusão

Com esta implementação, o problema da coluna `user_id` faltante nas tabelas `funcionarios` e `especialidades` será resolvido automaticamente em produção, garantindo que:

- ✅ Funcionários sejam exibidos corretamente
- ✅ Especialidades sejam exibidas corretamente
- ✅ Isolamento entre usuários funcione para ambas as entidades
- ✅ Não haja mais erros de "funcionários não encontrados" ou "especialidades não encontradas"
- ✅ Deploy seja completamente automático
- ✅ Não seja necessária intervenção manual