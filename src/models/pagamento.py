from src.models.usuario import db
from datetime import datetime
from enum import Enum

class PaymentMethod(Enum):
    PIX = 'PIX'
    DINHEIRO = 'DINHEIRO'
    CARTAO_CREDITO = 'CARTAO_CREDITO'
    CARTAO_DEBITO = 'CARTAO_DEBITO'
    LINK_PAGAMENTO = 'LINK_PAGAMENTO'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    data_pagamento = db.Column(db.Date, nullable=False)
    valor_pago = db.Column(db.Numeric(10, 2), nullable=False)
    modalidade_pagamento = db.Column(db.Enum(PaymentMethod), nullable=True) # Usando a enum
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='payments', lazy=True)
    payment_sessions = db.relationship('PaymentSession', backref='payment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Payment {self.id} - Patient {self.patient_id} - R$ {self.valor_pago}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'patient_id': self.patient_id,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'valor_pago': float(self.valor_pago) if self.valor_pago else 0,
            'modalidade_pagamento': self.modalidade_pagamento.value if self.modalidade_pagamento else None, # Retornando o valor da enum
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sessions': [ps.session.to_dict() for ps in self.payment_sessions] if self.payment_sessions else []
        }


class PaymentSession(db.Model):
    """Tabela de associação entre pagamentos e sessões (many-to-many)"""
    __tablename__ = 'payment_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PaymentSession Payment:{self.payment_id} Session:{self.session_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

