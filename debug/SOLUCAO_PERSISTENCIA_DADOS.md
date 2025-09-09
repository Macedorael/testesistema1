# 🔒 Solução para Persistência de Dados

## 🚨 Problema Identificado

O sistema estava perdendo todos os dados (usuários, pacientes, consultas, etc.) a cada deploy ou execução manual de scripts. Isso acontecia porque:

### Causas Principais:
1. **Script `init_db.py`** executava `db.drop_all()` por padrão
2. **Execução manual** do script durante configuração/manutenção
3. **Falta de proteção** contra perda acidental de dados

### Cenários Problemáticos:
- ✅ **Deploy no Render**: Já estava seguro (usa `db.create_all()` apenas)
- ❌ **Execução local**: `python scripts/init_db.py` apagava tudo
- ❌ **Instalação**: Scripts de instalação chamavam `init_db.py`
- ❌ **Manutenção**: Desenvolvedores executando script sem saber

## ✅ Solução Implementada

### 1. Modo Seguro por Padrão

O script `init_db.py` agora opera em **modo seguro** por padrão:

```bash
# SEGURO - Preserva dados existentes
python scripts/init_db.py
```

**O que faz:**
- ✅ Cria apenas tabelas que não existem
- ✅ Preserva todos os dados existentes
- ✅ Adiciona dados de exemplo apenas se banco estiver vazio
- ✅ Mostra quantos usuários já existem

### 2. Modo Reset Explícito

Para reset completo, agora é necessário confirmação:

```bash
# CUIDADO - Apaga todos os dados
python scripts/init_db.py --reset
```

**Proteções:**
- ⚠️ Exibe aviso claro sobre perda de dados
- 🔐 Requer digitação de 'CONFIRMO' para continuar
- 📝 Documenta claramente o que será perdido

### 3. Controle de Dados de Exemplo

```bash
# Sem dados de exemplo
python scripts/init_db.py --no-sample-data

# Reset sem dados de exemplo
python scripts/init_db.py --reset --no-sample-data
```

## 📋 Comandos Disponíveis

### Uso Normal (Recomendado)
```bash
# Inicialização segura - preserva dados
python scripts/init_db.py
```

### Desenvolvimento/Teste
```bash
# Reset completo para desenvolvimento
python scripts/init_db.py --reset

# Apenas estrutura, sem dados de exemplo
python scripts/init_db.py --no-sample-data
```

### Produção
```bash
# Deploy seguro (já implementado no build.sh)
# Usa apenas db.create_all() + create_admin_user.py
```

## 🔍 Como Verificar se Dados Estão Preservados

### 1. Contar Usuários
```python
from src.main import app, db
from src.models.usuario import User

with app.app_context():
    print(f"Total de usuários: {User.query.count()}")
```

### 2. Listar Usuários
```python
from src.main import app, db
from src.models.usuario import User

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Username: {user.username}")
```

### 3. Verificar Outras Tabelas
```python
from src.main import app, db
from src.models.paciente import Patient
from src.models.funcionario import Funcionario

with app.app_context():
    print(f"Pacientes: {Patient.query.count()}")
    print(f"Funcionários: {Funcionario.query.count()}")
```

## 🚀 Deploy em Produção

### Render (Atual)
O `build.sh` já está configurado corretamente:
- ✅ Usa `db.create_all()` (seguro)
- ✅ Executa `create_admin_user.py` (não duplica)
- ✅ Popula dados apenas se banco vazio

### Outros Ambientes
Para outros ambientes de produção:
```bash
# 1. Criar/verificar tabelas
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"

# 2. Garantir usuário admin
python scripts/create_admin_user.py

# 3. Dados de exemplo apenas se necessário
python scripts/init_db.py --no-sample-data
```

## 🛡️ Medidas de Segurança

### 1. Backup Antes de Operações
```bash
# PostgreSQL
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp src/database/app.db backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. Verificação Pós-Operação
```bash
# Verificar se dados ainda existem
python -c "from src.main import app, db; from src.models.usuario import User; app.app_context().push(); print(f'Usuários: {User.query.count()}')"
```

### 3. Logs de Operação
O script agora mostra claramente:
- 🔒 Modo seguro ativado
- ⚠️ Avisos de reset
- 📊 Contagem de dados existentes
- ✅ Confirmações de operação

## 📚 Documentação Atualizada

### Arquivos que Referenciam init_db.py:
- `install.sh` - Instalação Linux/Mac
- `install.bat` - Instalação Windows
- `docs/INSTALACAO.md` - Documentação
- `docs/README.md` - Manual do usuário

### Recomendação:
Atualizar documentação para usar modo seguro:
```bash
# Ao invés de:
python src/init_db.py

# Usar:
python scripts/init_db.py  # Modo seguro
```

## ✅ Checklist de Verificação

### Antes do Deploy:
- [ ] Backup do banco de dados
- [ ] Verificar se build.sh usa modo seguro
- [ ] Confirmar que não há chamadas para `init_database()` com reset

### Após o Deploy:
- [ ] Verificar se usuários existentes ainda estão lá
- [ ] Testar login com usuários existentes
- [ ] Verificar se dados de pacientes/consultas persistem
- [ ] Confirmar que admin user existe

### Para Desenvolvimento:
- [ ] Usar `python scripts/init_db.py` para preservar dados
- [ ] Usar `--reset` apenas quando necessário
- [ ] Fazer backup antes de reset

---

## 🎉 Resultado

✅ **Dados preservados** entre deploys  
✅ **Proteção contra perda acidental**  
✅ **Modo seguro por padrão**  
✅ **Reset controlado e explícito**  
✅ **Documentação clara**  
✅ **Compatibilidade mantida**  

**Agora você pode:**
- Criar usuários e dados sem medo de perdê-los
- Fazer deploy sem perder informações
- Desenvolver com segurança
- Resetar apenas quando necessário

---

**Data da correção:** $(date)  
**Status:** ✅ Implementado e testado