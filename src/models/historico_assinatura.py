from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.models.usuario import db

class SubscriptionHistory(db.Model):
    __tablename__ = 'subscription_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'), nullable=True)  # Pode ser null se a assinatura foi deletada
    action = Column(String(20), nullable=False)  # 'created', 'cancelled', 'renewed', 'updated', 'expired'
    plan_type = Column(String(20), nullable=False)  # 'monthly', 'quarterly', 'biannual', 'annual'
    price = Column(Float, nullable=False)
    # Campos para renovação - plano anterior
    previous_plan_type = Column(String(20), nullable=True)  # Plano anterior (para renovações)
    previous_price = Column(Float, nullable=True)  # Preço anterior (para renovações)
    start_date = Column(DateTime, nullable=True)  # Data de início da assinatura (para ações de criação/renovação)
    end_date = Column(DateTime, nullable=True)    # Data de fim da assinatura (para ações de criação/renovação)
    action_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # Quando a ação foi realizada
    details = Column(Text, nullable=True)  # Detalhes adicionais sobre a ação
    
    # Relacionamentos
    user = relationship('User', backref='subscription_history')
    subscription = relationship('Subscription', backref='history')
    
    def __init__(self, user_id, action, plan_type, price, subscription_id=None, start_date=None, end_date=None, details=None, previous_plan_type=None, previous_price=None):
        self.user_id = user_id
        self.subscription_id = subscription_id
        self.action = action
        self.plan_type = plan_type
        self.price = price
        self.previous_plan_type = previous_plan_type
        self.previous_price = previous_price
        self.start_date = start_date
        self.end_date = end_date
        self.details = details
        self.action_date = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'action': self.action,
            'plan_type': self.plan_type,
            'price': self.price,
            'previous_plan_type': self.previous_plan_type,
            'previous_price': self.previous_price,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'action_date': self.action_date.isoformat() if self.action_date else None,
            'details': self.details
        }
    
    @staticmethod
    def create_history_entry(user_id, action, plan_type, price, subscription_id=None, start_date=None, end_date=None, details=None, previous_plan_type=None, previous_price=None):
        """Método estático para criar uma entrada no histórico"""
        history_entry = SubscriptionHistory(
            user_id=user_id,
            action=action,
            plan_type=plan_type,
            price=price,
            subscription_id=subscription_id,
            start_date=start_date,
            end_date=end_date,
            details=details,
            previous_plan_type=previous_plan_type,
            previous_price=previous_price
        )
        db.session.add(history_entry)
        return history_entry
    
    @staticmethod
    def get_user_history(user_id, limit=None):
        """Retorna o histórico de assinaturas de um usuário"""
        query = SubscriptionHistory.query.filter_by(user_id=user_id).order_by(SubscriptionHistory.action_date.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_action_description(action):
        """Retorna uma descrição amigável para cada tipo de ação"""
        descriptions = {
            'created': 'Assinatura criada',
            'cancelled': 'Assinatura cancelada',
            'renewed': 'Assinatura renovada',
            'updated': 'Assinatura atualizada',
            'expired': 'Assinatura expirada'
        }
        return descriptions.get(action, action)
    
    @staticmethod
    def get_plan_name(plan_type):
        """Retorna o nome amigável do plano"""
        plan_names = {
            'monthly': 'Mensal',
            'quarterly': 'Trimestral',
            'biannual': 'Semestral',
            'annual': 'Anual'
        }
        return plan_names.get(plan_type, plan_type)