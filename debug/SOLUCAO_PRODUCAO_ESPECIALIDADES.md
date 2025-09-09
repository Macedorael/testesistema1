# 🚨 SOLUÇÃO URGENTE: Problema das Especialidades em Produção

## ⚡ Problema Identificado

O erro `ValueError: Invalid isoformat string: 'ativo'` ocorre porque alguns registros de especialidades em produção têm o campo `created_at` corrompido com a string "ativo" ao invés de uma data válida.

## 🎯 Solução Rápida (5 minutos)

### Passo 1: Backup Imediato
```bash
# PostgreSQL
pg_dump -h localhost -U seu_usuario -d nome_do_banco > backup_especialidades_$(date +%Y%m%d_%H%M%S).sql

# MySQL
mysqldump -u seu_usuario -p nome_do_banco > backup_especialidades_$(date +%Y%m%d_%H%M%S).sql
```

### Passo 2: Correção Direta no Banco

#### Para PostgreSQL:
```sql
-- Conectar ao banco
psql -h localhost -U seu_usuario -d nome_do_banco

-- Verificar registros problemáticos
SELECT id, nome, created_at FROM especialidades WHERE created_at::text = 'ativo';

-- Corrigir os registros
UPDATE especialidades 
SET created_at = NOW(), updated_at = NOW() 
WHERE created_at::text = 'ativo';

-- Verificar se funcionou
SELECT id, nome, created_at FROM especialidades;
```

#### Para MySQL:
```sql
-- Conectar ao banco
mysql -u seu_usuario -p nome_do_banco

-- Verificar registros problemáticos
SELECT id, nome, created_at FROM especialidades WHERE created_at = 'ativo';

-- Corrigir os registros
UPDATE especialidades 
SET created_at = NOW(), updated_at = NOW() 
WHERE created_at = 'ativo';

-- Verificar se funcionou
SELECT id, nome, created_at FROM especialidades;
```

### Passo 3: Usar o Script Python (Alternativa)

```bash
# Copiar o script para o servidor
scp fix_ativo_bug.py usuario@servidor:/caminho/do/projeto/

# No servidor, executar
cd /caminho/do/projeto
python fix_ativo_bug.py
```

### Passo 4: Reiniciar a Aplicação

```bash
# Systemd
sudo systemctl restart sua_aplicacao

# PM2
pm2 restart sua_aplicacao

# Docker
docker restart container_da_aplicacao

# Supervisor
sudo supervisorctl restart sua_aplicacao
```

### Passo 5: Verificar se Funcionou

```bash
# Testar a API
curl -X GET https://seu-dominio.com/api/especialidades

# Verificar logs
tail -f /var/log/sua_aplicacao.log
```

## 🛡️ Prevenção (Aplicar Após Correção)

### Adicionar Validação no Modelo

O arquivo `src/models/especialidade.py` já foi atualizado com validação. Certifique-se de que está em produção:

```python
from sqlalchemy.orm import validates

class Especialidade(db.Model):
    # ... outros campos ...
    
    @validates('created_at')
    def validate_created_at(self, key, value):
        if isinstance(value, str):
            invalid_values = ['ativo', 'active', 'true', 'false', 'ATIVO', 'ACTIVE']
            if value.lower() in [v.lower() for v in invalid_values]:
                raise ValueError(f"Valor inválido para created_at: {value}")
        return value
```

## 📞 Comandos de Emergência

### Se a correção SQL não funcionar:
```sql
-- Deletar registros corrompidos (CUIDADO!)
DELETE FROM especialidades WHERE created_at = 'ativo';

-- Recriar especialidades básicas
INSERT INTO especialidades (nome, descricao, created_at, updated_at) VALUES 
('Psicologia Clínica', 'Atendimento psicológico geral', NOW(), NOW()),
('Psicologia Infantil', 'Especializada em crianças', NOW(), NOW()),
('Terapia de Casal', 'Terapia para relacionamentos', NOW(), NOW());
```

### Verificação Rápida:
```bash
# Contar especialidades
echo "SELECT COUNT(*) FROM especialidades;" | psql -h localhost -U seu_usuario -d nome_do_banco

# Listar todas
echo "SELECT id, nome, created_at FROM especialidades;" | psql -h localhost -U seu_usuario -d nome_do_banco
```

## ✅ Checklist de Execução

- [ ] Backup realizado
- [ ] Registros problemáticos identificados
- [ ] Correção SQL executada
- [ ] Aplicação reiniciada
- [ ] API testada
- [ ] Logs verificados
- [ ] Validação preventiva aplicada

---

**⚠️ IMPORTANTE:** 
- Execute sempre em horário de menor movimento
- Tenha o backup antes de qualquer alteração
- Teste a API após cada passo
- Monitore logs por pelo menos 30 minutos após a correção

**🆘 Em caso de problemas:** Restaure o backup e entre em contato para suporte adicional.