from src.models.usuario import db
from datetime import datetime
from sqlalchemy.orm import validates

class Especialidade(db.Model):
    __tablename__ = 'especialidades'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    @validates('created_at', 'updated_at')
    def validate_datetime_fields(self, key, value):
        """Valida campos de data/hora para prevenir valores inválidos"""
        if value is None:
            return value
            
        # Se for string, verificar se é uma data válida
        if isinstance(value, str):
            # Prevenir strings como 'ativo', 'ATIVO', etc.
            if value.lower() in ['ativo', 'active', 'true', 'false']:
                raise ValueError(f"Valor inválido para campo {key}: {value}. Deve ser uma data válida.")
                
            # Tentar converter para datetime
            try:
                from datetime import datetime
                if 'T' in value:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError(f"Formato de data inválido para campo {key}: {value}")
                
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    # Relacionamentos
    user = db.relationship('User', backref='especialidades', lazy=True)
    
    def __repr__(self):
        return f'<Especialidade {self.nome}>'