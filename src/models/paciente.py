from src.models.usuario import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = 'patients'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'email', name='unique_user_email'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome_completo = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Novos campos para contato de emergência
    nome_contato_emergencia = db.Column(db.String(200), nullable=True)
    telefone_contato_emergencia = db.Column(db.String(20), nullable=True)
    grau_parentesco_emergencia = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='patients', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='patient', lazy=True, cascade='all, delete-orphan')
    diary_entries = db.relationship('DiaryEntry', backref='patient', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Patient {self.nome_completo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nome_completo': self.nome_completo,
            'telefone': self.telefone,
            'email': self.email,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'observacoes': self.observacoes,
            'ativo': bool(self.ativo) if self.ativo is not None else True,
            'nome_contato_emergencia': self.nome_contato_emergencia,
            'telefone_contato_emergencia': self.telefone_contato_emergencia,
            'grau_parentesco_emergencia': self.grau_parentesco_emergencia,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }



