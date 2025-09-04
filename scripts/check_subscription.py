from src.models.user import User, db
from src.models.subscription import Subscription
from src.main import app
from datetime import datetime

with app.app_context():
    # Buscar o usuário
    user = User.query.filter_by(email='r@teste.com').first()
    
    if user:
        print(f'Usuário encontrado: {user.email} (ID: {user.id})')
        
        # Verificar assinaturas
        subscriptions = Subscription.query.filter_by(user_id=user.id).all()
        print(f'Total de assinaturas: {len(subscriptions)}')
        
        for sub in subscriptions:
            print(f'Assinatura ID: {sub.id}')
            print(f'Plano: {sub.plan_type}')
            print(f'Status: {sub.status}')
            print(f'Data início: {sub.start_date}')
            print(f'Data fim: {sub.end_date}')
            print(f'Ativa: {sub.end_date > datetime.utcnow() if sub.end_date else False}')
            print('---')
        
        # Verificar assinatura ativa
        active_subscription = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).first()
        
        if active_subscription:
            print('✅ Usuário tem assinatura ativa')
        else:
            print('❌ Usuário NÃO tem assinatura ativa')
    else:
        print('❌ Usuário não encontrado')