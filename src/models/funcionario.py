from src.models.usuario import db
from datetime import datetime

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True, unique=True)
    especialidade_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=True)
    obs = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='funcionarios', lazy=True)
    especialidade = db.relationship("Especialidade", backref="funcionarios")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'especialidade_id': self.especialidade_id,
            'especialidade_nome': self.especialidade.nome if self.especialidade else None,
            'obs': self.obs,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Funcionario {self.nome}>'