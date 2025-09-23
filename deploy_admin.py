#!/usr/bin/env python3
"""
Script de Deploy - Criação do Usuário Administrador
Este script cria um usuário administrador apenas na primeira execução do deploy.
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.base import db
from models.usuario import User
from models.assinatura import Subscription

def create_admin_user():
    """
    Cria um usuário administrador se não existir.
    Retorna True se criou o usuário, False se já existia.
    """
    try:
        # Verificar se já existe um usuário admin
        existing_admin = User.query.filter_by(email='admin@consultorio.com').first()
        
        if existing_admin:
            print("✅ Usuário administrador já existe. Pulando criação...")
            return False
        
        print("🔧 Criando usuário administrador...")
        
        # Criar usuário administrador
        admin_user = User(
            username='admin',
            email='admin@consultorio.com',
            role='admin'
        )
        admin_user.set_password('admin123')  # Senha padrão - ALTERE APÓS O PRIMEIRO LOGIN
        
        db.session.add(admin_user)
        db.session.flush()  # Para obter o ID do usuário
        
        # Criar assinatura ativa para o admin (válida por 1 ano)
        end_date = datetime.now() + timedelta(days=365)
        admin_subscription = Subscription(
            user_id=admin_user.id,
            plan_type='admin',
            status='active',
            start_date=datetime.now(),
            end_date=end_date,
            price=0.0,
            auto_renew=True
        )
        
        db.session.add(admin_subscription)
        db.session.commit()
        
        print("✅ Usuário administrador criado com sucesso!")
        print("📧 Email: admin@consultorio.com")
        print("🔑 Senha: admin123")
        print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário administrador: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Função principal do script de deploy"""
    print("🚀 Iniciando script de deploy...")
    print("=" * 50)
    
    try:
        # Configurar variáveis de ambiente se necessário
        os.environ.setdefault('FLASK_ENV', 'production')
        
        # Importar a aplicação Flask para inicializar o contexto
        from main import app, db
        
        with app.app_context():
            # Criar usuário administrador
            admin_created = create_admin_user()
            
            if admin_created:
                print("\n🎉 Deploy concluído com sucesso!")
                print("👤 Usuário administrador criado.")
            else:
                print("\n✅ Deploy concluído!")
                print("👤 Usuário administrador já existia.")
                
    except Exception as e:
        print(f"❌ Erro durante o deploy: {str(e)}")
        sys.exit(1)
    
    print("=" * 50)
    print("🏁 Script de deploy finalizado.")

if __name__ == '__main__':
    main()