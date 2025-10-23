from src.models.usuario import db
from datetime import datetime

class DiaryEntry(db.Model):
    __tablename__ = 'diary_entries'

    id = db.Column(db.Integer, primary_key=True)
    # Owner user (profissional) para isolamento por usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Paciente ao qual o registro pertence
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # Campos do registro diário
    situacao = db.Column(db.Text, nullable=False)
    pensamento = db.Column(db.Text, nullable=False)
    emocao = db.Column(db.String(100), nullable=False)
    intensidade = db.Column(db.Integer, nullable=False)  # 0-10
    comportamento = db.Column(db.Text, nullable=False)
    consequencia = db.Column(db.Text, nullable=False)

    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = db.relationship('User', backref='diary_entries', lazy=True)

    def __repr__(self):
        return f'<DiaryEntry {self.id} - Patient {self.patient_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'patient_id': self.patient_id,
            'situacao': self.situacao,
            'pensamento': self.pensamento,
            'emocao': self.emocao,
            'intensidade': self.intensidade,
            'comportamento': self.comportamento,
            'consequencia': self.consequencia,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }