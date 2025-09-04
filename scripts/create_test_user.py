#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app
from src.models.usuario import User, db
from werkzeug.security import generate_password_hash

with app.app_context():
    # Verificar se o usuário de teste existe
    user = User.query.filter_by(email='teste@exemplo.com').first()
    
    if user:
        print('✅ Usuário de teste já existe')
        print(f'Email: {user.email}')
        print(f'ID: {user.id}')
    else:
        print('Criando usuário de teste...')
        new_user = User(
            username='teste_user',
            email='teste@exemplo.com',
            password_hash=generate_password_hash('senha123')
        )
        db.session.add(new_user)
        db.session.commit()
        print('✅ Usuário de teste criado com sucesso')
        print(f'Email: {new_user.email}')
        print(f'ID: {new_user.id}')