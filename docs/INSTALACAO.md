# 🚀 Guia Rápido de Instalação

## Pré-requisitos
- Python 3.8+ instalado
- pip (gerenciador de pacotes Python)

## Instalação em 5 Passos

### 1️⃣ Baixar o Sistema
Extraia o arquivo ZIP do sistema em uma pasta de sua escolha.

### 2️⃣ Abrir Terminal/Prompt
- **Windows:** Pressione `Win + R`, digite `cmd` e pressione Enter
- **Mac/Linux:** Abra o Terminal

### 3️⃣ Navegar até a Pasta
```bash
cd caminho/para/consultorio-psicologia
```

### 4️⃣ Executar Script de Instalação
```bash
# Windows
install.bat

# Mac/Linux
chmod +x install.sh
./install.sh
```

### 5️⃣ Acessar o Sistema
Abra seu navegador e acesse: `http://localhost:5000`

## Instalação Manual (se o script não funcionar)

### Passo 1: Criar Ambiente Virtual
```bash
python -m venv venv
```

### Passo 2: Ativar Ambiente Virtual
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Inicializar Banco de Dados
```bash
python src/init_db.py
```

### Passo 5: Executar Sistema
```bash
python src/main.py
```

## ✅ Verificação da Instalação

Se tudo estiver funcionando, você verá:
1. Mensagem no terminal: "Running on http://127.0.0.1:5000"
2. No navegador: Dashboard com dados de exemplo

## 🔧 Solução de Problemas Comuns

### Erro: "python não é reconhecido"
- **Solução:** Instale o Python do site oficial: https://python.org
- Marque a opção "Add Python to PATH" durante a instalação

### Erro: "pip não é reconhecido"
- **Solução:** Reinstale o Python marcando "Add Python to PATH"

### Erro: "Porta 5000 em uso"
- **Solução:** Feche outros programas que possam estar usando a porta
- Ou edite `src/main.py` e mude a porta para 5001

### Erro: "Módulo não encontrado"
- **Solução:** Certifique-se de que o ambiente virtual está ativado
- Execute novamente: `pip install -r requirements.txt`

## 📱 Primeiro Uso

### Dados de Exemplo
O sistema vem com dados de demonstração:
- 2 pacientes cadastrados
- 2 agendamentos com sessões
- Estatísticas no dashboard

### Testando o Sistema
1. **Dashboard:** Veja as estatísticas gerais
2. **Pacientes:** Visualize e teste o cadastro
3. **Agendamentos:** Crie um novo agendamento
4. **Pagamentos:** Registre um pagamento de teste

### Limpando Dados de Exemplo
Para começar com dados limpos:
```bash
# Apague o arquivo do banco
rm consultorio.db

# Recrie o banco vazio
python src/init_db.py --empty
```

## 🆘 Precisa de Ajuda?

1. **Leia o README.md completo** para documentação detalhada
2. **Verifique os logs** no terminal onde o sistema está rodando
3. **Console do navegador** (F12) para erros JavaScript
4. **Reinicie o sistema** fechando o terminal e executando novamente

## 📞 Comandos Úteis

### Parar o Sistema
Pressione `Ctrl + C` no terminal

### Reiniciar o Sistema
```bash
python src/main.py
```

### Backup do Banco de Dados
```bash
# Copie o arquivo consultorio.db para local seguro
cp consultorio.db backup_consultorio_$(date +%Y%m%d).db
```

### Atualizar Dependências
```bash
pip install --upgrade -r requirements.txt
```

---

**🎉 Pronto! Seu sistema está funcionando!**

Acesse `http://localhost:5000` e comece a gerenciar seu consultório de forma profissional.

