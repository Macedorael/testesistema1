from src.main import app
from src.models.usuario import User

with app.app_context():
    users = User.query.all()
    print(f'Total de usuários: {len(users)}')
    for u in users:
        print(f'ID: {u.id}, Username: {u.username}, Email: {u.email}')