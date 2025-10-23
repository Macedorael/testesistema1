import sys
import os

# Adicionar o diretório raiz ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.usuario import db, User
from sqlalchemy import text

def add_first_login_column():
    """Adiciona a coluna first_login à tabela users"""
    try:
        # Verificar se a coluna já existe
        try:
            # Tentar acessar a coluna para ver se ela existe
            User.query.filter(User.first_login == True).first()
            print("✅ [MIGRATION] Coluna 'first_login' já existe")
            return True
        except Exception:
            # Se der erro, a coluna não existe e precisamos criá-la
            print("[MIGRATION] Adicionando coluna 'first_login' à tabela users...")
            
            # Adicionar a coluna com valor padrão False
            db.session.execute(text("ALTER TABLE users ADD COLUMN first_login BOOLEAN DEFAULT FALSE"))
            db.session.commit()
            print("✅ [MIGRATION] Coluna 'first_login' adicionada com sucesso")
            return True
    except Exception as e:
        print(f"❌ [ERROR] Erro ao adicionar coluna 'first_login': {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    # Inicializar a conexão com o banco de dados
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.main import app
    
    with app.app_context():
        add_first_login_column()