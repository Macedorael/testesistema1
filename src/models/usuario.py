from werkzeug.security import generate_password_hash, check_password_hash
from src.models.base import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user', 'admin' ou 'patient'
    telefone = db.Column(db.String(20), nullable=False)  # Campo para telefone (obrigatório)
    data_nascimento = db.Column(db.Date, nullable=False)  # Campo para data de nascimento (obrigatório)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    first_login = db.Column(db.Boolean, default=True)  # Indica se é o primeiro login do usuário
    
    # Relacionamento com Subscription (um usuário pode ter uma assinatura)
    # Removido temporariamente para evitar erro de circular import
    # subscription = db.relationship('Subscription', back_populates='user', uselist=False, lazy='select')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        role = getattr(self, 'role', None) or 'user'
        return role == 'admin'
    
    def is_new_user(self):
        """Verifica se o usuário foi criado há menos de 1 dia"""
        if not self.created_at:
            return False
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.days < 1

    def has_active_subscription(self):
        """Verifica se o usuário tem uma assinatura ativa"""
        from src.models.assinatura import Subscription
        from datetime import datetime
        
        # Buscar a assinatura ativa mais recente
        active_subscription = Subscription.query.filter_by(
            user_id=self.id,
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.created_at.desc()).first()
        
        return active_subscription is not None
    
    def get_subscription_status(self):
        """Retorna o status da assinatura do usuário"""
        from src.models.assinatura import Subscription
        from datetime import datetime
        
        # Buscar a assinatura ativa mais recente
        active_subscription = Subscription.query.filter_by(
            user_id=self.id,
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.created_at.desc()).first()
        
        if active_subscription:
            return active_subscription.status
        return 'no_subscription'
    
    def get_subscription_days_remaining(self):
        """Retorna quantos dias restam na assinatura"""
        from src.models.assinatura import Subscription
        from datetime import datetime
        
        # Buscar a assinatura ativa mais recente
        active_subscription = Subscription.query.filter_by(
            user_id=self.id,
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.created_at.desc()).first()
        
        if active_subscription:
            return active_subscription.days_remaining()
        return 0
    
    def to_dict(self):
        from src.models.assinatura import Subscription
        from datetime import datetime
        
        # Buscar a assinatura ativa mais recente
        active_subscription = Subscription.query.filter_by(
            user_id=self.id,
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.created_at.desc()).first()
        
        subscription_info = None
        if active_subscription:
            subscription_info = active_subscription.to_dict()
            
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': getattr(self, 'role', None) or 'user',
            'telefone': self.telefone,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'subscription': subscription_info,
            'has_active_subscription': self.has_active_subscription()
        }


