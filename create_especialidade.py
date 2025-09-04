from src.models.especialidade import Especialidade
from src.models.base import db
from src.main import app

with app.app_context():
    # Criar uma especialidade de exemplo
    especialidade = Especialidade(
        nome="Psicologia Clínica",
        descricao="Atendimento psicológico individual para adultos"
    )
    
    db.session.add(especialidade)
    db.session.commit()
    
    print(f"Especialidade criada: ID {especialidade.id}, Nome: {especialidade.nome}")
    
    # Verificar se foi criada corretamente
    todas = Especialidade.query.all()
    print(f"Total de especialidades no banco: {len(todas)}")
    for e in todas:
        print(f"ID: {e.id}, Nome: '{e.nome}', Descrição: '{e.descricao}'")