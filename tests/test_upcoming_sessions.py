import requests
import json

# Fazer login primeiro
login_data = {'email': 'admin@admin.com', 'password': 'admin123'}
session = requests.Session()
login_response = session.post('http://localhost:5000/login', data=login_data)

if login_response.status_code == 200:
    # Testar endpoint de próximas sessões
    response = session.get('http://localhost:5000/dashboard/sessions/upcoming?limit=5')
    if response.status_code == 200:
        data = response.json()
        print('Resposta do endpoint de próximas sessões:')
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
            print('Nenhuma sessão encontrada ou erro na resposta')
    else:
        print(f'Erro ao acessar endpoint: {response.status_code}')
        print(response.text)
else:
    print(f'Erro no login: {login_response.status_code}')