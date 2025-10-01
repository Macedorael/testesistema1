from src.models.usuario import db, User
from src.models.assinatura import Subscription
from src.main import app

with app.app_context():
    # Buscar todas as assinaturas ativas
    subscriptions = Subscription.query.filter_by(status='active').all()
    print('=== STATUS DAS ASSINATURAS NO BANCO ===')
    for sub in subscriptions:
        user = User.query.get(sub.user_id)
        email = user.email if user else "N/A"
        print(f'Usuário: {email} | Auto-renew: {sub.auto_renew} | Status: {sub.status}')
    print('=' * 40)