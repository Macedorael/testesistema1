import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.usuario import db, User
from src.models.assinatura import Subscription
from datetime import datetime
from flask import Flask

# Configurar Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("=== ATIVANDO ASSINATURA DO USUÁRIO ===")
    
    # Buscar usuário
    user = User.query.filter_by(email='teste@exemplo.com').first()
    print(f"\nUsuário encontrado: {user.email}")
    
    # Buscar assinatura
    subscription = Subscription.query.filter_by(user_id=user.id).first()
    print(f"\nAssinatura atual:")
    print(f"  - Status: {subscription.status}")
    print(f"  - Plano: {subscription.plan_type}")
    print(f"  - Data fim: {subscription.end_date}")
    
    # Ativar assinatura
    subscription.status = 'active'
    db.session.commit()
    
    print(f"\n✅ Assinatura ativada com sucesso!")
    print(f"\nAssinatura atualizada:")
    print(f"  - Status: {subscription.status}")
    print(f"  - Plano: {subscription.plan_type}")
    print(f"  - Data fim: {subscription.end_date}")
    
    # Verificar se agora seria considerada ativa
    active_subscription = Subscription.query.filter_by(
        user_id=user.id,
        status='active'
    ).filter(
        Subscription.end_date > datetime.utcnow()
    ).first()
    
    print(f"\nVerificação final: {'✅ ATIVA' if active_subscription else '❌ INATIVA'}")