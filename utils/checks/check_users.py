import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.models.base import db
from src.models.usuario import User
from src.models.assinatura import Subscription
from src.main import app
from datetime import datetime

with app.app_context():
    print('=== VERIFICAÇÃO DE USUÁRIOS ===')
    users = User.query.all()
    print(f'Total de usuários: {len(users)}')
    
    for user in users:
        role = getattr(user, 'role', 'N/A')
        print(f'ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {role}')
        
        # Verificar assinaturas do usuário
        subscriptions = Subscription.query.filter_by(user_id=user.id).all()
        print(f'  Assinaturas: {len(subscriptions)}')
        
        for sub in subscriptions:
            print(f'    ID: {sub.id}, Tipo: {sub.plan_type}, Status: {sub.status}')
            print(f'    Início: {sub.start_date}, Fim: {sub.end_date}')
            print(f'    Ativa: {sub.is_active()}, Dias restantes: {sub.days_remaining()}')
        print('---')