from src.models.usuario import db
from datetime import datetime

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    especialidade_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=True)
    obs = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint única composta: email deve ser único por usuário (quando não for nulo)
    __table_args__ = (db.UniqueConstraint('user_id', 'email', name='uq_user_funcionario_email'),)
    
    # Relacionamentos
    user = db.relationship('User', backref='funcionarios', lazy=True)
    especialidade = db.relationship("Especialidade", backref="funcionarios")
    
    def to_dict(self):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Tentar acessar especialidade com segurança
            especialidade_nome = None
            if self.especialidade_id:
                try:
                    if hasattr(self, 'especialidade') and self.especialidade:
                        especialidade_nome = self.especialidade.nome
                        logger.debug(f"[FUNCIONARIO] Especialidade encontrada: {especialidade_nome}")
                    else:
                        logger.warning(f"[FUNCIONARIO] Especialidade ID {self.especialidade_id} não carregada")
                except Exception as esp_error:
                    logger.error(f"[FUNCIONARIO] Erro ao acessar especialidade: {str(esp_error)}")
            
            result = {
                'id': self.id,
                'user_id': self.user_id,
                'nome': self.nome,
                'telefone': self.telefone,
                'email': self.email,
                'especialidade_id': self.especialidade_id,
                'especialidade_nome': especialidade_nome,
                'obs': self.obs,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
            
            logger.debug(f"[FUNCIONARIO] to_dict() concluído para funcionário ID {self.id}")
            return result
            
        except Exception as e:
            logger.error(f"[FUNCIONARIO] Erro em to_dict(): {str(e)}")
            # Retornar versão mínima em caso de erro
            return {
                'id': getattr(self, 'id', None),
                'user_id': getattr(self, 'user_id', None),
                'nome': getattr(self, 'nome', 'Nome não disponível'),
                'telefone': getattr(self, 'telefone', None),
                'email': getattr(self, 'email', None),
                'especialidade_id': getattr(self, 'especialidade_id', None),
                'especialidade_nome': None,
                'obs': getattr(self, 'obs', None),
                'created_at': None,
                'updated_at': None
            }
    
    def __repr__(self):
        return f'<Funcionario {self.nome}>'