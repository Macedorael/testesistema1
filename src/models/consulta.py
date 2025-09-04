from src.models.usuario import db
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import relationship

class FrequencyType(Enum):
    SEMANAL = 'semanal'
    QUINZENAL = 'quinzenal'
    MENSAL = 'mensal'

class SessionStatus(Enum):
    AGENDADA = 'agendada'
    REALIZADA = 'realizada'
    CANCELADA = 'cancelada'
    FALTOU = 'faltou'
    REAGENDADA = 'reagendada'

class PaymentStatus(Enum):
    PENDENTE = 'pendente'
    PAGO = 'pago'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=True)

    data_primeira_sessao = db.Column(db.DateTime, nullable=False)
    quantidade_sessoes = db.Column(db.Integer, nullable=False, default=1)
    frequencia = db.Column(db.Enum(FrequencyType), nullable=False, default=FrequencyType.SEMANAL)
    valor_por_sessao = db.Column(db.Numeric(10, 2), nullable=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='appointments', lazy=True)
    funcionario = db.relationship('Funcionario', backref='appointments', lazy=True)
    sessions = db.relationship('Session', backref='appointment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Appointment {self.id} - Patient {self.patient_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'patient_id': self.patient_id,
            'funcionario_id': self.funcionario_id,
            'funcionario_nome': self.funcionario.nome if self.funcionario else None,
            'data_primeira_sessao': self.data_primeira_sessao.isoformat() if self.data_primeira_sessao else None,
            'quantidade_sessoes': self.quantidade_sessoes,
            'frequencia': self.frequencia.value if self.frequencia else None,
            'valor_por_sessao': float(self.valor_por_sessao) if self.valor_por_sessao else 0,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sessions': [session.to_dict() for session in self.sessions] if self.sessions else []
        }

    def generate_sessions(self):
        """Gera as sessões automaticamente baseado na frequência e quantidade"""
        # Remove sessões existentes
        for session in self.sessions:
            db.session.delete(session)
        
        # Calcula o intervalo baseado na frequência
        if self.frequencia == FrequencyType.SEMANAL:
            interval_days = 7
        elif self.frequencia == FrequencyType.QUINZENAL:
            interval_days = 14
        elif self.frequencia == FrequencyType.MENSAL:
            interval_days = 30
        else:
            interval_days = 7  # default
        
        # Gera as sessões
        current_date = self.data_primeira_sessao
        for i in range(self.quantidade_sessoes):
            session = Session(
                appointment_id=self.id,
                data_sessao=current_date,
                numero_sessao=i + 1,
                status=SessionStatus.AGENDADA,
                status_pagamento=PaymentStatus.PENDENTE,
                valor=self.valor_por_sessao
            )
            db.session.add(session)
            current_date += timedelta(days=interval_days)


class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    data_sessao = db.Column(db.DateTime, nullable=False)
    data_original = db.Column(db.DateTime, nullable=True) # Para guardar a data original em caso de reagendamento
    data_reagendamento = db.Column(db.DateTime, nullable=True) # Para guardar a nova data de reagendamento
    numero_sessao = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(SessionStatus), nullable=False, default=SessionStatus.AGENDADA)
    status_pagamento = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDENTE)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    payment_sessions = db.relationship('PaymentSession', backref='session', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Session {self.numero_sessao} - Appointment {self.appointment_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'data_sessao': self.data_sessao.isoformat() if self.data_sessao else None,
            'numero_sessao': self.numero_sessao,
            'status': self.status.value if self.status else None,
            'status_pagamento': self.status_pagamento.value if self.status_pagamento else None,
            'valor': float(self.valor) if self.valor else 0,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'data_original': self.data_original.isoformat() if self.data_original else None,
            'data_reagendamento': self.data_reagendamento.isoformat() if self.data_reagendamento else None
        }