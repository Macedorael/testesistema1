from src.models.usuario import User, db
from src.main import app

with app.app_context():
    # Buscar o usuário
    user = User.query.filter_by(email='admin@teste.com').first()
    
    if user:
        print(f'=== VERIFICAÇÃO DE CREDENCIAIS ===\n')
        print(f'Usuário encontrado:')
        print(f'  - ID: {user.id}')
        print(f'  - Email: {user.email}')
        print(f'  - Username: {user.username}')
        print(f'  - Password hash: {user.password_hash[:50]}...')
        
        # Testar senhas comuns
        senhas_teste = ['senha123', '123456', 'password', 'teste', 'r@teste.com']
        
        print(f'\nTestando senhas:')
        for senha in senhas_teste:
            if user.check_password(senha):
                print(f'  ✅ Senha correta: "{senha}"')
                break
            else:
                print(f'  ❌ Senha incorreta: "{senha}"')
        else:
            print(f'\n❌ Nenhuma das senhas testadas funcionou.')
            print(f'Você pode redefinir a senha executando:')
            print(f'user.set_password("nova_senha")')
            print(f'db.session.commit()')
    else:
        print('❌ Usuário não encontrado')
        
        # Listar todos os usuários
        all_users = User.query.all()
        print(f'\nUsuários existentes:')
        for u in all_users:
            print(f'  - {u.email} (ID: {u.id})')