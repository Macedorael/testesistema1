#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.user import User, db
from src.models.subscription import Subscription
from datetime import datetime
from flask import Flask

# Configurar Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("=== CORRIGINDO MÚLTIPLAS ASSINATURAS ATIVAS ===")
    
    # Buscar usuário
    user = User.query.filter_by(email='r@teste.com').first()
    if not user:
        print("❌ Usuário não encontrado!")
        exit(1)
    
    print(f"Usuário: {user.email} (ID: {user.id})")
    
    # Buscar todas as assinaturas ativas
    active_subscriptions = Subscription.query.filter_by(
        user_id=user.id,
        status='active'
    ).filter(Subscription.end_date > datetime.utcnow()).order_by(Subscription.created_at.desc()).all()
    
    print(f"\nAssinaturas ativas encontradas: {len(active_subscriptions)}")
    
    if len(active_subscriptions) <= 1:
        print("✅ Usuário tem apenas uma ou nenhuma assinatura ativa. Nada a fazer.")
        exit(0)
    
    # Manter apenas a mais recente (primeira da lista ordenada por created_at desc)
    most_recent = active_subscriptions[0]
    to_cancel = active_subscriptions[1:]
    
    print(f"\nMantendo assinatura mais recente:")
    print(f"  ID: {most_recent.id}, Plano: {most_recent.plan_type}, Criada: {most_recent.created_at}")
    
    print(f"\nCancelando {len(to_cancel)} assinaturas antigas:")
    for sub in to_cancel:
        print(f"  ID: {sub.id}, Plano: {sub.plan_type}, Criada: {sub.created_at}")
        sub.cancel()
    
    # Salvar mudanças
    db.session.commit()
    
    print(f"\n✅ {len(to_cancel)} assinaturas canceladas com sucesso!")
    
    # Verificar resultado final
    final_active = Subscription.query.filter_by(
        user_id=user.id,
        status='active'
    ).filter(Subscription.end_date > datetime.utcnow()).count()
    
    print(f"\nVerificação final:")
    print(f"  Assinaturas ativas restantes: {final_active}")
    print(f"  has_active_subscription(): {user.has_active_subscription()}")
    
    if final_active == 1:
        print("\n🎉 Problema resolvido! Usuário agora tem apenas uma assinatura ativa.")
    else:
        print(f"\n⚠️  Ainda há {final_active} assinaturas ativas. Pode ser necessário investigar mais.")