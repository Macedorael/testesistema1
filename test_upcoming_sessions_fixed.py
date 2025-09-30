import requests
import json

print('Iniciando teste...')

# Fazer login com JSON
login_data = {'email': 'admin@admin.com', 'password': 'admin123'}
session = requests.Session()
print('Fazendo login...')
login_response = session.post('http://localhost:5000/login', json=login_data)
print(f'Status do login: {login_response.status_code}')

if login_response.status_code == 200:
    print('Login realizado com sucesso')
    # Testar endpoint de próximas sessões
    print('Testando endpoint de próximas sessões...')
    response = session.get('http://localhost:5000/dashboard/sessions/upcoming?limit=5')
    print(f'Status da resposta: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print('Dados recebidos:')
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success') and data.get('data'):
            print('\nVerificando especialidades nas próximas sessões:')
            for i, session_data in enumerate(data['data']):
                print(f'Sessão {i+1}:')
                print(f'  - Paciente: {session_data.get("patient_name", "N/A")}')
                print(f'  - Funcionário: {session_data.get("funcionario_nome", "N/A")}')
                print(f'  - Especialidade: {session_data.get("especialidade_nome", "N/A")}')
                print(f'  - Funcionário Especialidade: {session_data.get("funcionario_especialidade", "N/A")}')
                print()
        else:
            print('Nenhuma sessão encontrada')
    else:
        print(f'Erro: {response.status_code}')
        print(response.text)
else:
    print(f'Erro no login: {login_response.status_code}')
    print(login_response.text)