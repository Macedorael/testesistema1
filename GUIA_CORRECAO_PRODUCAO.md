# 🚨 GUIA DE CORREÇÃO: Problema "ativo" em Produção

## 📋 Resumo do Problema

O problema identificado é que o campo `created_at` de algumas especialidades em produção contém a string "ativo" ao invés de uma data válida. Isso causa o erro:

```
ValueError: Invalid isoformat string: 'ativo'
```

## 🔍 Causa Raiz

O problema ocorre porque:
1. Dados corrompidos foram inseridos no banco de produção
2. O campo `created_at` contém a string "ativo" ao invés de uma data ISO válida
3. O SQLAlchemy tenta converter "ativo" para datetime e falha

## ✅ Solução Implementada

### 1. Script de Correção (`fix_ativo_bug.py`)

**O que faz:**
- Identifica registros com "ativo" no campo `created_at`
- Corrige esses registros com a data atual
- Verifica a integridade após a correção

**Como usar em produção:**
```bash
# 1. Fazer backup do banco de dados
pg_dump nome_do_banco > backup_antes_correcao.sql

# 2. Executar o script de correção
python fix_ativo_bug.py

# 3. Verificar se funcionou
python -c "from src.main import app; from src.models.especialidade import Especialidade; app.app_context().push(); print(len(Especialidade.query.all()))"
```

### 2. Validação Preventiva (`prevent_ativo_bug.py`)

**O que foi implementado:**
- ✅ Validação no modelo SQLAlchemy
- ✅ Triggers no banco de dados
- ✅ Proteção contra valores inválidos

**Arquivos modificados:**
- `src/models/especialidade.py` - Adicionada validação `@validates`

## 🚀 Passos para Produção

### Passo 1: Backup
```bash
# PostgreSQL
pg_dump -h localhost -U usuario -d nome_banco > backup_$(date +%Y%m%d_%H%M%S).sql

# Ou se usar outro SGBD, adapte o comando
```

### Passo 2: Executar Correção
```bash
# Copiar os scripts para o servidor de produção
scp fix_ativo_bug.py usuario@servidor:/caminho/do/projeto/
scp prevent_ativo_bug.py usuario@servidor:/caminho/do/projeto/

# No servidor de produção
cd /caminho/do/projeto
python fix_ativo_bug.py
```

### Passo 3: Aplicar Validação Preventiva
```bash
# Aplicar as validações
python prevent_ativo_bug.py

# Reiniciar a aplicação
sudo systemctl restart nome_da_aplicacao
# ou
sudo service nome_da_aplicacao restart
```

### Passo 4: Verificação
```bash
# Testar se a API funciona
curl -X GET https://seu-dominio.com/api/especialidades

# Verificar logs
tail -f /var/log/sua_aplicacao.log
```

## 🔧 Verificação Manual no Banco

### PostgreSQL
```sql
-- Verificar registros problemáticos
SELECT id, nome, created_at 
FROM especialidades 
WHERE created_at::text = 'ativo' OR created_at::text = 'ATIVO';

-- Corrigir manualmente se necessário
UPDATE especialidades 
SET created_at = NOW(), updated_at = NOW() 
WHERE created_at::text IN ('ativo', 'ATIVO');
```

### SQLite (desenvolvimento)
```sql
-- Verificar registros problemáticos
SELECT id, nome, created_at 
FROM especialidades 
WHERE created_at = 'ativo' OR created_at = 'ATIVO';

-- Corrigir manualmente se necessário
UPDATE especialidades 
SET created_at = datetime('now'), updated_at = datetime('now') 
WHERE created_at IN ('ativo', 'ATIVO');
```

## 🛡️ Prevenção Futura

### Validação no Modelo
O modelo `Especialidade` agora tem validação que impede:
- Strings como "ativo", "active", "true", "false"
- Formatos de data inválidos

### Triggers no Banco
Triggers foram criados para validação adicional no nível do banco de dados.

### Monitoramento
Considere adicionar:
- Logs de auditoria para mudanças em especialidades
- Alertas para erros de validação
- Testes automatizados que verificam integridade dos dados

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Execute os scripts de verificação
3. Consulte este guia para troubleshooting

## 📝 Checklist de Execução

- [ ] Backup do banco realizado
- [ ] Script `fix_ativo_bug.py` executado com sucesso
- [ ] Script `prevent_ativo_bug.py` executado com sucesso
- [ ] Aplicação reiniciada
- [ ] API testada e funcionando
- [ ] Logs verificados sem erros
- [ ] Monitoramento configurado

---

**⚠️ IMPORTANTE:** Sempre teste em ambiente de homologação antes de aplicar em produção!