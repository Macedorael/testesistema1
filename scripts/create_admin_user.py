#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuário admin padrão se não existir
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from flask import Flask
    from src.models.base import db
    from src.models.usuario import User
    
    # Criar aplicação Flask
    app = Flask(__name__)
    
    # Configurar banco de dados
    if os.getenv('DATABASE_URL'):
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"[DEBUG] Usando PostgreSQL: {database_url[:50]}...")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'app.db')}"
        print("[DEBUG] Usando SQLite local")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'temp-key-for-script'
    
    db.init_app(app)
    
    with app.app_context():
        print("[DEBUG] Verificando se usuário admin existe...")
        
        # Verificar se já existe um usuário admin
        admin_user = User.query.filter_by(email='admin@teste.com').first()
        
        if admin_user:
            print(f"[INFO] Usuário admin já existe: {admin_user.email}")
            print(f"[INFO] ID: {admin_user.id}, Username: {admin_user.username}")
        else:
            print("[INFO] Criando usuário admin padrão...")
            
            # Criar usuário admin
            admin_user = User(
                username='admin',
                email='admin@teste.com'
            )
            admin_user.set_password('123456')
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"[SUCCESS] Usuário admin criado com sucesso!")
            print(f"[INFO] Email: admin@teste.com")
            print(f"[INFO] Senha: 123456")
            print(f"[INFO] ID: {admin_user.id}")
        
        # Verificar total de usuários
        total_users = User.query.count()
        print(f"[INFO] Total de usuários no sistema: {total_users}")
        
except Exception as e:
    print(f"[ERROR] Erro ao criar usuário admin: {e}")
    import traceback
    print(f"[ERROR] Traceback: {traceback.format_exc()}")
    sys.exit(1)

print("[SUCCESS] Script executado com sucesso!")