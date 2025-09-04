from src.models.especialidade import Especialidade
from src.models.base import db
from src.main import app

with app.app_context():
    especialidades = Especialidade.query.all()
    print(f'Total de especialidades: {len(especialidades)}')
    
    if len(especialidades) == 0:
        print('Nenhuma especialidade encontrada no banco de dados')
    else:
        print('Especialidades encontradas:')
        for e in especialidades:
            print(f'ID: {e.id}, Nome: "{e.nome}", Descrição: "{e.descricao}"')