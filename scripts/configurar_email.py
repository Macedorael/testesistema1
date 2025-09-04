#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar automaticamente o arquivo .env para envio de emails
"""

import os
import getpass
from pathlib import Path

def main():
    print("🔧 Configurador de Email - Sistema de Recuperação de Senha")
    print("=" * 60)
    print()
    
    # Verificar se .env já existe
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  Arquivo .env já existe!")
        resposta = input("Deseja sobrescrever? (s/N): ").lower().strip()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Configuração cancelada.")
            return
        print()
    
    print("📧 Configuração de Email")
    print("-" * 25)
    
    # Coletar informações do usuário
    print("\n1. Escolha seu provedor de email:")
    print("   1) Gmail (recomendado)")
    print("   2) Outlook/Hotmail")
    print("   3) Yahoo")
    print("   4) Outro")
    
    while True:
        try:
            opcao = int(input("\nEscolha uma opção (1-4): "))
            if 1 <= opcao <= 4:
                break
            else:
                print("❌ Opção inválida. Digite um número de 1 a 4.")
        except ValueError:
            print("❌ Digite apenas números.")
    
    # Configurações SMTP baseadas na escolha
    if opcao == 1:  # Gmail
        smtp_server = "smtp.gmail.com"
        smtp_port = "587"
        print("\n✅ Gmail selecionado")
        print("\n📋 IMPORTANTE para Gmail:")
        print("   1. Ative a verificação em 2 etapas")
        print("   2. Gere uma 'Senha de app' específica")
        print("   3. Use a senha de app (16 caracteres) abaixo")
        print("\n🔗 Guia: https://support.google.com/accounts/answer/185833")
        
    elif opcao == 2:  # Outlook
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = "587"
        print("\n✅ Outlook/Hotmail selecionado")
        
    elif opcao == 3:  # Yahoo
        smtp_server = "smtp.mail.yahoo.com"
        smtp_port = "587"
        print("\n✅ Yahoo selecionado")
        
    else:  # Outro
        print("\n🔧 Configuração personalizada")
        smtp_server = input("Servidor SMTP (ex: smtp.exemplo.com): ").strip()
        smtp_port = input("Porta SMTP (geralmente 587 ou 465): ").strip()
    
    print("\n" + "-" * 40)
    
    # Coletar credenciais
    email = input("📧 Seu email: ").strip()
    
    print("\n🔐 Senha:")
    if opcao == 1:
        print("   Digite a SENHA DE APP do Gmail (16 caracteres)")
    else:
        print("   Digite sua senha de email")
    
    senha = getpass.getpass("🔑 Senha: ")
    
    # URL base
    print("\n🌐 URL da aplicação:")
    base_url = input("URL base (padrão: http://localhost:5002): ").strip()
    if not base_url:
        base_url = "http://localhost:5002"
    
    # Chave secreta
    print("\n🔐 Chave secreta do Flask:")
    secret_key = input("Chave secreta (deixe vazio para gerar automaticamente): ").strip()
    if not secret_key:
        import secrets
        secret_key = secrets.token_urlsafe(32)
        print(f"✅ Chave gerada automaticamente: {secret_key[:20]}...")
    
    # Criar conteúdo do arquivo .env
    env_content = f"""# Configurações de Email para Recuperação de Senha
# Gerado automaticamente em {os.path.basename(__file__)}

# Configurações SMTP
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SMTP_EMAIL={email}
SMTP_PASSWORD={senha}

# URL base da aplicação (para links de recuperação)
BASE_URL={base_url}

# Configurações do Flask
SECRET_KEY={secret_key}
FLASK_ENV=development
"""
    
    # Salvar arquivo
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n" + "=" * 60)
        print("✅ Arquivo .env criado com sucesso!")
        print("\n📋 Próximos passos:")
        print("   1. Reinicie o servidor Python")
        print("   2. Teste a recuperação de senha")
        print("   3. Verifique se o email chega corretamente")
        
        print("\n🔒 SEGURANÇA:")
        print("   • Nunca compartilhe o arquivo .env")
        print("   • Adicione .env ao .gitignore se usar Git")
        print("   • Mantenha suas credenciais seguras")
        
        print("\n🧪 Para testar:")
        print(f"   Acesse: {base_url}/static/entrar.html")
        print("   Clique em 'Esqueci minha senha'")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar arquivo .env: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 Configuração concluída!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Configuração cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    input("\nPressione Enter para sair...")