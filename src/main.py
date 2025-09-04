import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory, session, redirect, url_for
from flask_cors import CORS

# Importações básicas primeiro
try:
    from src.models.base import db
    from src.models.usuario import User
    print("[DEBUG] Importação de usuario OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar usuario: {e}")

try:
    from src.models.paciente import Patient
    print("[DEBUG] Importação de paciente OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar paciente: {e}")

try:
    from src.models.consulta import Appointment, Session
    print("[DEBUG] Importação de consulta OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar consulta: {e}")

try:
    from src.models.pagamento import Payment, PaymentSession
    print("[DEBUG] Importação de pagamento OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar pagamento: {e}")

try:
    from src.models.password_reset import PasswordResetToken
    print("[DEBUG] Importação de password_reset OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar password_reset: {e}")

try:
    from src.models.especialidade import Especialidade
    print("[DEBUG] Importação de especialidade OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar especialidade: {e}")

try:
    from src.models.funcionario import Funcionario
    print("[DEBUG] Importação de funcionario OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar funcionario: {e}")

# Importações de rotas
try:
    from src.routes.usuario import user_bp
    print("[DEBUG] Importação de usuario routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar usuario routes: {e}")

try:
    from src.routes.pacientes import patients_bp
    print("[DEBUG] Importação de pacientes routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar pacientes routes: {e}")

try:
    from src.routes.consultas import appointments_bp
    print("[DEBUG] Importação de consultas routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar consultas routes: {e}")

try:
    from src.routes.pagamentos import payments_bp
    print("[DEBUG] Importação de pagamentos routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar pagamentos routes: {e}")

try:
    from src.routes.dashboard import dashboard_bp
    print("[DEBUG] Importação de dashboard routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar dashboard routes: {e}")

try:
    from src.routes.dashboard_payments import dashboard_payments_bp
    print("[DEBUG] Importação de dashboard_payments routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar dashboard_payments routes: {e}")

try:
    from src.routes.dashboard_sessions import dashboard_sessions_bp
    print("[DEBUG] Importação de dashboard_sessions routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar dashboard_sessions routes: {e}")

try:
    from src.routes.assinaturas import subscriptions_bp
    print("[DEBUG] Importação de assinaturas routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar assinaturas routes: {e}")

try:
    from src.routes.especialidades import especialidades_bp
    print("[DEBUG] Importação de especialidades routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar especialidades routes: {e}")

try:
    from src.routes.funcionarios import funcionarios_bp
    print("[DEBUG] Importação de funcionarios routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar funcionarios routes: {e}")



# Configuração do Flask com debug de static folder
static_path = os.path.join(os.path.dirname(__file__), 'static')
print(f"[DEBUG] Static folder path: {static_path}")
print(f"[DEBUG] Static folder exists: {os.path.exists(static_path)}")

app = Flask(__name__, static_folder=static_path)
# Configuração da SECRET_KEY
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'consultorio-psicologia-secret-key-2024')

print(f"[DEBUG] Flask static_folder: {app.static_folder}")
print(f"[DEBUG] Flask static_url_path: {app.static_url_path}")

# Verificar se inicial.html existe
inicial_path = os.path.join(static_path, 'inicial.html')
print(f"[DEBUG] inicial.html path: {inicial_path}")
print(f"[DEBUG] inicial.html exists: {os.path.exists(inicial_path)}")

# Configurar CORS para produção
if os.getenv('FLASK_ENV') == 'production':
    # Produção - CORS restritivo
    allowed_origins = [
        os.getenv('BASE_URL', 'https://consultorio-psicologia.onrender.com'),
        'https://consultorio-psicologia.onrender.com'
    ]
    CORS(app, origins=allowed_origins, supports_credentials=True)
else:
    # Desenvolvimento - CORS permissivo
    CORS(app, supports_credentials=True)

# Middleware para logar todas as requisições - SIMPLIFICADO
@app.before_request
def log_request_info():
    from flask import request
    print(f"[DEBUG] >>> REQUISIÇÃO: {request.method} {request.path}")

@app.after_request
def log_response_info(response):
    print(f"[DEBUG] <<< RESPOSTA: {response.status_code}")
    
    # Headers de segurança para produção
    if os.getenv('FLASK_ENV') == 'production':
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

# Registrar blueprints
try:
    app.register_blueprint(user_bp, url_prefix='/api')
    print("[DEBUG] Blueprint user_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar user_bp: {e}")

try:
    app.register_blueprint(patients_bp, url_prefix='/api')
    print("[DEBUG] Blueprint patients_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar patients_bp: {e}")

try:
    app.register_blueprint(appointments_bp, url_prefix='/api')
    print("[DEBUG] Blueprint appointments_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar appointments_bp: {e}")

try:
    app.register_blueprint(payments_bp, url_prefix='/api')
    print("[DEBUG] Blueprint payments_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar payments_bp: {e}")

try:
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    print("[DEBUG] Blueprint dashboard_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar dashboard_bp: {e}")

try:
    app.register_blueprint(dashboard_payments_bp, url_prefix='/api')
    print("[DEBUG] Blueprint dashboard_payments_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar dashboard_payments_bp: {e}")

try:
    app.register_blueprint(dashboard_sessions_bp, url_prefix='/api')
    print("[DEBUG] Blueprint dashboard_sessions_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar dashboard_sessions_bp: {e}")

try:
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    print("[DEBUG] Blueprint subscriptions_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar subscriptions_bp: {e}")

try:
    app.register_blueprint(especialidades_bp, url_prefix='/api')
    print("[DEBUG] Blueprint especialidades_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar especialidades_bp: {e}")

try:
    app.register_blueprint(funcionarios_bp, url_prefix='/api')
    print("[DEBUG] Blueprint funcionarios_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar funcionarios_bp: {e}")



# Configuração do banco de dados
if os.getenv('DATABASE_URL'):
    # Produção - PostgreSQL no Render
    database_url = os.getenv('DATABASE_URL')
    # Render usa postgres:// mas SQLAlchemy precisa de postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Desenvolvimento - SQLite local
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas apenas se não existirem
with app.app_context():
    try:
        db.create_all()
        print("[DEBUG] Tabelas do banco de dados criadas/verificadas com sucesso")
    except Exception as e:
        print(f"[ERROR] Erro ao criar tabelas: {e}")

@app.route('/')
def home():
    """Rota principal - redireciona baseado no status de login e assinatura"""
    try:
        print(f"[DEBUG] Acessando rota principal. Session: {dict(session)}")
        
        # Verificar se o usuário está logado
        if 'user_id' in session:
            print("[DEBUG] Usuário logado, verificando assinatura...")
            
            # Importar aqui para evitar circular imports
            from src.models.assinatura import Subscription
            from datetime import datetime
            
            # Verificar se tem assinatura ativa
            active_subscription = Subscription.query.filter_by(
                user_id=session['user_id'],
                status='active'
            ).filter(
                Subscription.end_date > datetime.utcnow()
            ).first()
            
            if active_subscription:
                print("[DEBUG] Usuário com assinatura ativa, retornando index.html")
                return send_from_directory(app.static_folder, 'index.html')
            else:
                print("[DEBUG] Usuário sem assinatura ativa, redirecionando para assinaturas")
                return send_from_directory(app.static_folder, 'assinaturas.html')
        else:
            print("[DEBUG] Usuário não logado, retornando inicial.html")
            return send_from_directory(app.static_folder, 'inicial.html')
            
    except Exception as e:
        print(f"[ERROR] Erro na rota principal: {e}")
        return f"Erro: {str(e)}", 500

@app.route('/<path:path>')
def serve(path):
    # Não interceptar rotas da API
    if path.startswith('api/'):
        return "API route not found", 404
        
    print(f"[DEBUG] FUNÇÃO SERVE CHAMADA - Tentando servir arquivo: {path}")
    static_folder_path = app.static_folder
    print(f"[DEBUG] Static folder path: {static_folder_path}")
    
    if static_folder_path is None:
        print("[ERROR] Static folder not configured")
        return "Static folder not configured", 404

    # Verificar se o arquivo existe
    file_path = os.path.join(static_folder_path, path)
    print(f"[DEBUG] Caminho completo do arquivo: {file_path}")
    print(f"[DEBUG] Arquivo existe: {os.path.exists(file_path)}")
    
    if path != "" and os.path.exists(file_path):
        print(f"[DEBUG] Servindo arquivo: {path}")
        return send_from_directory(static_folder_path, path)
    else:
        # Se o arquivo não existe, retornar 404 ao invés de index.html
        print(f"[ERROR] Arquivo não encontrado: {path}")
        return f"File not found: {path}", 404


if __name__ == '__main__':
    print("[DEBUG] Iniciando Flask com debug=True na porta 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
