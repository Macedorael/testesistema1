# Documentação - Deploy com Migração Automática

## Visão Geral

Este documento descreve o processo de deploy automático que inclui migração de campos obrigatórios para a aplicação do Consultório de Psicologia.

## Arquivos Criados/Modificados

### 1. `migrate_required_fields.py`
Script de migração que torna os campos `telefone` e `data_nascimento` obrigatórios na tabela `users`.

**Funcionalidades:**
- Detecta automaticamente o tipo de banco (PostgreSQL/SQLite)
- Verifica se os campos já são obrigatórios
- Popula registros existentes com valores padrão se necessário
- Altera as colunas para NOT NULL
- Verifica se a migração foi aplicada corretamente

### 2. `src/models/usuario.py` (Modificado)
Alterado os campos `telefone` e `data_nascimento` de `nullable=True` para `nullable=False`.

### 3. `build.sh` (Modificado)
Adicionado execução do script de migração no processo de deploy:
```bash
echo "Executando migração de campos obrigatórios..."
python migrate_required_fields.py
```

### 4. `src/main.py` (Modificado)
Adicionada lógica de população automática de dados padrão durante a inicialização:
- Usuários sem telefone recebem: `(00) 00000-0000`
- Usuários sem data de nascimento recebem: `1990-01-01`

## Processo de Deploy

### Ordem de Execução (build.sh)
1. Configuração do ambiente Python
2. Instalação de dependências
3. **Migração de campos obrigatórios** (novo)
4. Inicialização do banco de dados
5. Criação de usuário admin
6. Correções de bugs existentes
7. Inicialização da aplicação

### Valores Padrão Aplicados

| Campo | Valor Padrão | Descrição |
|-------|--------------|-----------|
| `telefone` | `(00) 00000-0000` | Telefone genérico para usuários existentes |
| `data_nascimento` | `1990-01-01` | Data padrão para usuários existentes |

## Segurança e Validação

### Frontend (cadastro.html)
- Campos marcados como `required`
- Validação JavaScript impede envio com campos vazios
- Máscara de entrada para telefone: `(XX) XXXXX-XXXX`
- Formato de data: `dd/mm/yyyy`

### Backend (usuario.py)
- Campos definidos como `nullable=False` no modelo
- Validação automática pelo SQLAlchemy

## Compatibilidade

### Bancos de Dados Suportados
- **PostgreSQL**: Suporte completo para ALTER COLUMN
- **SQLite**: Limitações conhecidas, mas funcional para novos registros

### Ambientes
- **Desenvolvimento**: SQLite local (`src/database/app.db`)
- **Produção**: PostgreSQL (via `DATABASE_URL`)

## Logs e Monitoramento

O script de migração produz logs detalhados:
```
✅ Conexão com banco de dados estabelecida
✅ Coluna 'telefone' alterada para obrigatória
✅ Coluna 'data_nascimento' alterada para obrigatória
✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!
```

## Rollback (Se Necessário)

Em caso de problemas, os campos podem ser revertidos para nullable:

```sql
-- PostgreSQL
ALTER TABLE users ALTER COLUMN telefone DROP NOT NULL;
ALTER TABLE users ALTER COLUMN data_nascimento DROP NOT NULL;

-- SQLite (requer recriação da tabela)
-- Consulte documentação específica do SQLite
```

## Testes Realizados

- ✅ Migração em banco SQLite local
- ✅ População automática de dados padrão
- ✅ Validação frontend com campos obrigatórios
- ✅ Integração com processo de build existente

## Contato

Para dúvidas sobre este processo de migração, consulte a documentação técnica ou entre em contato com a equipe de desenvolvimento.