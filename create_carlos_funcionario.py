import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.base import db
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade

# Importar a instância app do main.py
import importlib.util
spec = importlib.util.spec_from_file_location('main', 'src/main.py')
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

with main_module.app.app_context():
    # Buscar uma especialidade para Carlos (vamos usar Psicologia Clínica)
    especialidade = Especialidade.query.filter_by(nome='Psicologia Clínica').first()
    if not especialidade:
        print('❌ Especialidade "Psicologia Clínica" não encontrada!')
        exit(1)
    
    # Verificar se Carlos já existe
    carlos_existente = Funcionario.query.filter_by(nome='Carlos Souza').first()
    if carlos_existente:
        print('✅ Carlos Souza já existe como funcionário!')
        exit(0)
    
    # Criar Carlos Souza como funcionário
    carlos = Funcionario(
        nome='Carlos Souza',
        telefone='31987655678',
        email='carlos.souza@clinica.com',
        especialidade_id=especialidade.id,
        user_id=1,  # Mesmo user_id do admin
        observacoes='Psicólogo especializado em terapia cognitivo-comportamental'
    )
    
    db.session.add(carlos)
    db.session.commit()
    
    print('✅ Carlos Souza criado como funcionário!')
    print(f'   - ID: {carlos.id}')
    print(f'   - Nome: {carlos.nome}')
    print(f'   - Email: {carlos.email}')
    print(f'   - Especialidade: {especialidade.nome}')
    print(f'   - User ID: {carlos.user_id}')
    
    # Verificar total de funcionários
    total_funcionarios = Funcionario.query.count()
    print(f'\n📊 Total de funcionários no sistema: {total_funcionarios}')