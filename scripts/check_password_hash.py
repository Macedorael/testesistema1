from src.models.user import User, db
from src.main import app
from werkzeug.security import check_password_hash

with app.app_context():
    # Buscar o usuário
    user = User.query.filter_by(email='r@teste.com').first()
    
    if user:
        print(f'Usuário encontrado: {user.email}')
        print(f'Password hash: {user.password_hash}')
        
        # Testar várias senhas
        test_passwords = ['123456', '123', 'password', 'admin', 'teste']
        
        for pwd in test_passwords:
            is_valid = user.check_password(pwd)
            print(f'Senha "{pwd}": {"✅ VÁLIDA" if is_valid else "❌ inválida"}')
            
        # Testar diretamente com check_password_hash
        print('\n--- Teste direto com check_password_hash ---')
        for pwd in test_passwords:
            is_valid = check_password_hash(user.password_hash, pwd)
            print(f'Senha "{pwd}": {"✅ VÁLIDA" if is_valid else "❌ inválida"}')
    else:
        print('❌ Usuário não encontrado')