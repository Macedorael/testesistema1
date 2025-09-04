#!/usr/bin/env python3
"""
Script rápido para ativar assinatura de um usuário
"""

import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from src.models.usuario import db, User
from src.models.assinatura import Subscription

# Criar app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'consultorio-psicologia-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db.init_app(app)

def activate_subscription(email):
    """Ativa assinatura para um usuário"""
    with app.app_context():
        try:
            # Buscar usuário
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"❌ Usuário com email {email} não encontrado")
                return False
            
            # Verificar se já tem assinatura ativa
            active_sub = Subscription.query.filter_by(
                user_id=user.id,
                status='active'
            ).filter(
                Subscription.end_date > datetime.utcnow()
            ).first()
            
            if active_sub:
                print(f"✅ Usuário {email} já possui assinatura ativa até {active_sub.end_date}")
                return True
            
            # Criar nova assinatura
            subscription = Subscription(
                user_id=user.id,
                plan_type='monthly',
                auto_renew=True
            )
            
            # Definir status como ativo após criação
            subscription.status = 'active'
            
            db.session.add(subscription)
            db.session.commit()
            
            print(f"✅ Assinatura ativada para {email} até {subscription.end_date}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao ativar assinatura: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python quick_activate_subscription.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    success = activate_subscription(email)
    if not success:
        sys.exit(1)