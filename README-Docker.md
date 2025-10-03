# 🐳 Consultório de Psicologia - Docker

Este projeto foi configurado para rodar com Docker, utilizando duas imagens separadas:
- **Aplicação Flask**: Container com a aplicação Python
- **Banco MySQL**: Container com banco de dados MySQL 8.0

## 📋 Pré-requisitos

- Docker instalado
- Docker Compose instalado

## 🚀 Como executar

### Opção 1: Script automático (Linux/Mac)
```bash
chmod +x docker-start.sh
./docker-start.sh
```

### Opção 2: Script automático (Windows)
```cmd
docker-start.bat
```

### Opção 3: Comandos manuais
```bash
# Construir e iniciar os containers
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Parar os containers
docker-compose down
```

## 🔧 Configuração

### Variáveis de Ambiente
As configurações estão no arquivo `.env.docker`:
- `DATABASE_URL`: Conexão com MySQL
- `SECRET_KEY`: Chave secreta da aplicação
- `FLASK_ENV`: Ambiente de execução

### Banco de Dados
- **Host**: localhost
- **Porta**: 3306
- **Banco**: consultorio_db
- **Usuário**: consultorio_user
- **Senha**: consultorio_pass_123

## 📊 Serviços

### Aplicação (app)
- **Porta**: 5000
- **URL**: http://localhost:5000
- **Container**: consultorio_app

### MySQL (mysql)
- **Porta**: 3306
- **Container**: consultorio_mysql
- **Volume**: mysql_data (persistente)

## 🛠️ Comandos Úteis

```bash
# Ver status dos containers
docker-compose ps

# Ver logs da aplicação
docker-compose logs app

# Ver logs do MySQL
docker-compose logs mysql

# Acessar terminal da aplicação
docker-compose exec app bash

# Acessar MySQL
docker-compose exec mysql mysql -u consultorio_user -p consultorio_db

# Reiniciar apenas a aplicação
docker-compose restart app

# Reconstruir a aplicação
docker-compose up --build app

# Limpar volumes (CUIDADO: apaga dados do banco)
docker-compose down -v
```

## 📁 Estrutura de Arquivos Docker

```
├── Dockerfile              # Imagem da aplicação
├── docker-compose.yml      # Orquestração dos serviços
├── .env.docker            # Variáveis de ambiente
├── docker-start.sh        # Script de inicialização (Linux/Mac)
├── docker-start.bat       # Script de inicialização (Windows)
└── init-db/               # Scripts de inicialização do MySQL
    └── 01-init.sql        # Configuração inicial do banco
```

## 🔒 Segurança

- As senhas padrão devem ser alteradas em produção
- O arquivo `.env.docker` não deve ser commitado com senhas reais
- Configure HTTPS em produção

## 🐛 Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs

# Verificar se as portas estão livres
netstat -an | grep :5000
netstat -an | grep :3306
```

### Problemas de conexão com banco
```bash
# Verificar se MySQL está rodando
docker-compose exec mysql mysqladmin ping

# Testar conexão
docker-compose exec app python -c "
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"
```

### Reset completo
```bash
# Parar tudo e limpar
docker-compose down -v
docker system prune -f

# Reconstruir do zero
docker-compose up --build
```

## 📝 Notas

- Os dados do MySQL são persistidos no volume `mysql_data`
- A aplicação reinicia automaticamente em caso de falha
- O healthcheck garante que o MySQL esteja pronto antes da aplicação iniciar
- As imagens não são enviadas para Docker Hub (apenas local)