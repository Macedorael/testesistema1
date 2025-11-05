from datetime import datetime, timedelta
import secrets
import string
from src.models.usuario import db

class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def __init__(self, user_id, expires_in_minutes=10):
        self.user_id = user_id
        self.token = self.generate_token()
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    
    @staticmethod
    def generate_token(length=32):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self):
        self.used = True
    
    @classmethod
    def create_for_user(cls, user_id):
        # Invalidar tokens anteriores não utilizados
        old_tokens = cls.query.filter_by(user_id=user_id, used=False).all()
        for token in old_tokens:
            token.mark_as_used()
        
        new_token = cls(user_id=user_id)
        db.session.add(new_token)
        db.session.commit()
        return new_token
    
    @classmethod
    def find_valid_token(cls, token_string):
        token = cls.query.filter_by(token=token_string).first()
        if token and token.is_valid():
            return token
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used,
            'is_valid': self.is_valid()
        }