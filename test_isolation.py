from src.main import app, db
from src.models.usuario import User
from src.models.funcionario import Funcionario
from src.models.especialidade import Especialidade
from werkzeug.security import generate_password_hash
import requests
import json

def test_user_isolation():
    with app.app_context():
        # Criar usuário de teste se não existir
        test_user = User.query.filter_by(email='teste2@email.com').first()
        if not test_user:
            test_user = User(
                username='teste2',
                email='teste2@email.com',
                password_hash=generate_password_hash('123456')
            )
            db.session.add(test_user)
            db.session.commit()
            print(f'Usuário teste criado: ID={test_user.id}, Email={test_user.email}')
        else:
            print(f'Usuário teste já existe: ID={test_user.id}, Email={test_user.email}')
        
        # Criar especialidade para o usuário de teste
        especialidade = Especialidade.query.filter_by(user_id=test_user.id).first()
        if not especialidade:
            especialidade = Especialidade(
                nome='Psicologia Teste',
                user_id=test_user.id
            )
            db.session.add(especialidade)
            db.session.commit()
            print(f'Especialidade criada: ID={especialidade.id}, Nome={especialidade.nome}, User_ID={especialidade.user_id}')
        
        # Testar login e criação de funcionário via API
        session = requests.Session()
        
        # Login
        login_data = {'email': 'teste2@email.com', 'password': '123456'}
        login_response = session.post('http://127.0.0.1:5000/api/login', json=login_data)
        print(f'Login response: {login_response.status_code}')
        
        if login_response.status_code == 200:
            # Testar outras rotas primeiro
            test_routes = [
                '/api/especialidades',
                '/api/patients', 
                '/api/funcionarios'
            ]
            
            for route in test_routes:
                test_response = session.get(f'http://127.0.0.1:5000{route}')
                print(f'GET {route} response: {test_response.status_code}')
                if test_response.status_code != 200:
                    print(f'Response text: {test_response.text[:100]}')
            
            # Criar funcionário
            funcionario_data = {
                'nome': 'Dr. Teste Isolamento',
                'especialidade_id': especialidade.id,
                'telefone': '123456789',
                'email': 'teste.isolamento@email.com'
            }
            create_response = session.post('http://127.0.0.1:5000/api/funcionarios', json=funcionario_data)
            print(f'Create funcionario response: {create_response.status_code}')
            print(f'Response text: {create_response.text[:200]}')
            
            # Verificar funcionários no banco
            funcionarios = Funcionario.query.all()
            print('\n=== TODOS OS FUNCIONÁRIOS NO BANCO ===')
            for f in funcionarios:
                print(f'ID: {f.id}, Nome: {f.nome}, User_ID: {f.user_id}')
        else:
            print(f'Login falhou: {login_response.text}')

if __name__ == '__main__':
    test_user_isolation()