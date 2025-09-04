import requests

base_url = "http://127.0.0.1:5000"
session = requests.Session()

# Login
login_data = {"email": "r@teste.com", "password": "123456"}
session.post(f"{base_url}/api/login", json=login_data)

# Acessar home
home_response = session.get(f"{base_url}/")
content = home_response.text

print(f"Tamanho do conteúdo: {len(content)}")
print(f"Título encontrado: {'Sistema de Consultório de Psicologia' in content}")
print(f"Navbar encontrada: {'navbar' in content}")
print(f"Dashboard encontrado: {'dashboard' in content.lower()}")
print(f"Pacientes encontrado: {'pacientes' in content.lower()}")
print(f"Agendamentos encontrado: {'agendamentos' in content.lower()}")

if all([
    'Sistema de Consultório de Psicologia' in content,
    'navbar' in content,
    'dashboard' in content.lower(),
    'pacientes' in content.lower()
]):
    print("\n✅ CONFIRMADO: É o dashboard principal (index.html)")
else:
    print("\n❌ Não é o dashboard principal")