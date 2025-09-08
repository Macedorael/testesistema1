# Guia de Correção de Isolamento em Produção

## 🚨 Problema Identificado

O isolamento de dados entre usuários está funcionando localmente mas não em produção. Isso indica que as correções aplicadas localmente precisam ser replicadas no ambiente de produção.

## 📋 Checklist de Correções Necessárias

### 1. Verificar Estado Atual em Produção

```bash
# Conectar ao servidor de produção e executar:
python check_production_user_ids.py
```

### 2. Aplicar Correções de Constraints

```bash
# Executar script de correção de constraints:
python fix_isolation_constraints.py
```

**⚠️ IMPORTANTE:** Este script:
- Faz backup dos dados
- Recria as tabelas com constraints corretas
- Restaura os dados
- Testa as novas constraints

### 3. Redistribuir Dados Entre Usuários

```bash
# Executar redistribuição de registros:
python fix_user_isolation.py
```

### 4. Reiniciar Servidor de Produção

```bash
# Reiniciar o servidor para aplicar mudanças:
# No Render ou similar:
# - Fazer novo deploy
# - Ou reiniciar o serviço
```

## 🔍 Scripts de Diagnóstico

### Verificar Tabelas do Banco
```bash
python check_db_tables.py
```

### Verificar Registros Sem user_id
```bash
python check_null_user_ids.py
```

### Verificar Isolamento Atual
```bash
python check_production_user_ids.py
```

## 📊 Estado Esperado Após Correção

- **Usuário 1** (teste@email.com): 3 especialidades, 3 funcionários
- **Usuário 4** (teste2@email.com): 3 especialidades, 3 funcionários
- **Usuários 2 e 3**: 0 registros cada

## 🚀 Deploy em Produção

### Opção 1: Deploy Automático (Render)

1. Fazer push das correções:
```bash
git push origin master
```

2. Aguardar deploy automático no Render

3. Executar scripts de correção via terminal do Render:
```bash
python fix_isolation_constraints.py
python fix_user_isolation.py
```

### Opção 2: Deploy Manual

1. Conectar ao servidor de produção
2. Fazer pull das mudanças:
```bash
git pull origin master
```

3. Executar scripts de correção:
```bash
python fix_isolation_constraints.py
python fix_user_isolation.py
```

4. Reiniciar servidor:
```bash
# Dependendo do ambiente:
sudo systemctl restart consultorio-app
# ou
pm2 restart app
# ou reiniciar via painel de controle
```

## ✅ Verificação Pós-Deploy

1. **Testar Login com Usuário 1:**
   - Deve ver apenas 3 especialidades
   - Deve ver apenas 3 funcionários

2. **Testar Login com Usuário 4:**
   - Deve ver 3 especialidades diferentes
   - Deve ver 3 funcionários diferentes

3. **Executar Diagnóstico:**
```bash
python check_production_user_ids.py
```

## 🔧 Troubleshooting

### Se o Problema Persistir:

1. **Verificar se o banco correto está sendo usado:**
```bash
# Verificar logs do servidor para confirmar caminho do banco
tail -f /var/log/app.log
```

2. **Verificar constraints do banco:**
```bash
sqlite3 src/database/app.db
.schema especialidades
.schema funcionarios
```

3. **Verificar se as mudanças foram aplicadas:**
```bash
python -c "import sqlite3; conn = sqlite3.connect('src/database/app.db'); cursor = conn.cursor(); cursor.execute('SELECT user_id, COUNT(*) FROM especialidades GROUP BY user_id'); print(cursor.fetchall())"
```

### Logs Importantes:

- Verificar se aparecem erros de constraint UNIQUE
- Confirmar que o servidor está usando o banco correto
- Verificar se as tabelas foram recriadas corretamente

## 📞 Suporte

Se o problema persistir após seguir este guia:

1. Coletar logs do servidor
2. Executar todos os scripts de diagnóstico
3. Verificar se o deploy foi bem-sucedido
4. Confirmar que o banco de produção foi atualizado

---

**Data de Criação:** $(date)
**Versão:** 1.0
**Status:** Pronto para aplicação em produção