from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from src.models.base import db

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_type = Column(String(20), nullable=False)  # 'monthly', 'quarterly', 'biannual', 'annual'
    status = Column(String(20), nullable=False, default='active')  # 'active', 'expired', 'cancelled'
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com User
    # Removido temporariamente para evitar erro de circular import
    # user = db.relationship('User', back_populates='subscription', lazy='select')
    
    # Preços dos planos (em reais)
    PLAN_PRICES = {
        'monthly': 29.90,
        'quarterly': 79.90,  # 3 meses com desconto
        'biannual': 149.90,  # 6 meses com desconto
        'annual': 279.90,    # 12 meses com desconto
        'trial': 0.0         # Plano de acesso temporário (2 dias)
    }
    
    # Duração dos planos em meses
    PLAN_DURATION = {
        'monthly': 1,
        'quarterly': 3,
        'biannual': 6,
        'annual': 12
    }
    
    def __init__(self, user_id, plan_type, auto_renew=True):
        self.user_id = user_id
        self.plan_type = plan_type
        self.price = self.PLAN_PRICES.get(plan_type, 0)
        self.auto_renew = auto_renew
        self.start_date = datetime.utcnow()
        self.end_date = self.calculate_end_date()
        
    def calculate_end_date(self):
        """Calcula a data de término baseada no tipo de plano"""
        # Suporte especial para plano de teste (2 dias)
        if self.plan_type == 'trial':
            return self.start_date + timedelta(days=2)

        duration_months = self.PLAN_DURATION.get(self.plan_type, 1)
        # Adiciona os meses à data de início
        if duration_months == 1:
            return self.start_date + timedelta(days=30)
        elif duration_months == 3:
            return self.start_date + timedelta(days=90)
        elif duration_months == 6:
            return self.start_date + timedelta(days=180)
        elif duration_months == 12:
            return self.start_date + timedelta(days=365)
        return self.start_date + timedelta(days=30)
    
    def is_active(self):
        """Verifica se a assinatura está ativa"""
        return self.status == 'active' and self.end_date > datetime.utcnow()
    
    def days_remaining(self):
        """Retorna quantos dias restam na assinatura"""
        if self.is_active():
            return (self.end_date - datetime.utcnow()).days
        return 0
    
    def renew(self):
        """Renova a assinatura por mais um período"""
        if self.auto_renew:
            # Salvar a data de término atual para usar como nova data de início
            old_end_date = self.end_date
            self.start_date = old_end_date
            
            # Calcular nova data de término baseada na nova data de início
            duration_months = self.PLAN_DURATION.get(self.plan_type, 1)
            if duration_months == 1:
                self.end_date = self.start_date + timedelta(days=30)
            elif duration_months == 3:
                self.end_date = self.start_date + timedelta(days=90)
            elif duration_months == 6:
                self.end_date = self.start_date + timedelta(days=180)
            elif duration_months == 12:
                self.end_date = self.start_date + timedelta(days=365)
            else:
                self.end_date = self.start_date + timedelta(days=30)
            
            self.status = 'active'
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def cancel(self):
        """Cancela a assinatura"""
        self.status = 'cancelled'
        self.auto_renew = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'price': self.price,
            'auto_renew': self.auto_renew,
            'days_remaining': self.days_remaining(),
            'is_active': self.is_active()
        }
    
    @staticmethod
    def get_plan_info():
        """Retorna informações sobre todos os planos disponíveis"""
        return {
            'monthly': {
                'name': 'Mensal',
                'price': Subscription.PLAN_PRICES['monthly'],
                'duration': '1 mês',
                'description': 'Plano básico mensal'
            },
            'quarterly': {
                'name': 'Trimestral',
                'price': Subscription.PLAN_PRICES['quarterly'],
                'duration': '3 meses',
                'description': 'Plano trimestral com desconto',
                'savings': round((Subscription.PLAN_PRICES['monthly'] * 3) - Subscription.PLAN_PRICES['quarterly'], 2)
            },
            'biannual': {
                'name': 'Semestral',
                'price': Subscription.PLAN_PRICES['biannual'],
                'duration': '6 meses',
                'description': 'Plano semestral com maior desconto',
                'savings': round((Subscription.PLAN_PRICES['monthly'] * 6) - Subscription.PLAN_PRICES['biannual'], 2)
            },
            'annual': {
                'name': 'Anual',
                'price': Subscription.PLAN_PRICES['annual'],
                'duration': '12 meses',
                'description': 'Plano anual com máximo desconto',
                'savings': round((Subscription.PLAN_PRICES['monthly'] * 12) - Subscription.PLAN_PRICES['annual'], 2)
            }
        }