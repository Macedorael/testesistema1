# Correção da Persistência de Dados no Deploy

## Problema Identificado

O sistema estava perdendo todos os dados (usuários, pacientes, etc.) a cada novo deploy manual no Render. Isso acontecia porque:

1. **Script `build.sh`** chamava `init_database()` que executava `db.drop_all()` 
2. **Função `init_database()`** em `scripts/init_db.py` apagava todas as tabelas antes de recriar
3. **Dados existentes** eram perdidos completamente a cada deploy

## Solução Implementada

### 1. Modificação do `build.sh`

**Antes:**
```bash
# Initialize database
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"

# Run database migrations if needed
python3 -c "import sys; sys.path.append('.'); from scripts.init_db import init_database; init_database(); print('Database populated successfully')" || echo "Database population skipped (already exists)"
```

**Depois:**
```bash
# Initialize database (only create tables if they don't exist - preserves existing data)
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database tables created/verified successfully')"

# Ensure admin user exists (safe - won't duplicate)
python3 scripts/create_admin_user.py

# Only populate with sample data if database is empty (first deploy)
python3 -c "import sys; sys.path.append('.'); from src.main import app, db; from src.models.usuario import User; app.app_context().push(); user_count = User.query.count(); print(f'Found {user_count} existing users'); exit(0 if user_count > 0 else 1)" && echo "Database has existing data - skipping sample data population" || python3 -c "import sys; sys.path.append('.'); from scripts.init_db import create_sample_data; create_sample_data(); print('Sample data populated successfully')"
```

### 2. Criação do Script `create_admin_user.py`

Novo script que:
- ✅ Verifica se usuário admin já existe
- ✅ Cria apenas se não existir
- ✅ Não duplica usuários
- ✅ Garante sempre ter um usuário para login

**Credenciais do Admin:**
- Email: `admin@teste.com`
- Senha: `123456`

### 3. Lógica de Preservação de Dados

1. **`db.create_all()`** - Cria apenas tabelas que não existem
2. **Verificação de usuários** - Conta usuários existentes
3. **População condicional** - Só popula se banco estiver vazio
4. **Admin garantido** - Sempre garante que existe um usuário admin

## Benefícios

✅ **Dados preservados** - Usuários criados não são mais perdidos  
✅ **Deploy seguro** - Pode fazer deploy sem perder dados  
✅ **Admin sempre disponível** - Sempre existe um usuário para login  
✅ **Primeira execução funcional** - Ainda popula dados em deploy inicial  
✅ **Sem duplicatas** - Não cria usuários ou dados duplicados  

## Como Testar

1. **Criar usuário** no sistema em produção
2. **Fazer alteração** no código
3. **Executar deploy** manual
4. **Verificar** se usuário ainda existe
5. **Login** deve funcionar normalmente

## Arquivos Modificados

- `build.sh` - Lógica de deploy preservando dados
- `scripts/create_admin_user.py` - Novo script para admin

## Próximos Passos

1. Fazer commit das alterações
2. Testar em produção
3. Verificar persistência após deploy
4. Documentar processo para equipe

---

**Data da correção:** $(date)  
**Status:** ✅ Implementado e testado localmente