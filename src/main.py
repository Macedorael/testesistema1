import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

# Configurar logging detalhado
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Configurar loggers específicos para nível DEBUG
logging.getLogger('src.routes.assinaturas').setLevel(logging.INFO)
# logging.getLogger('src.utils.subscription_payment_handler').setLevel(logging.INFO)
# logging.getLogger('src.utils.mercadopago_config').setLevel(logging.INFO)
# logging.getLogger('src.routes.mercadopago_webhook').setLevel(logging.INFO)

print("[DEBUG] Configuração de logging aplicada - logs detalhados habilitados")

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
    from src.models.diario import DiaryEntry
    print("[DEBUG] Importação de diario model OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar diario model: {e}")

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

try:
    from src.models.assinatura import Subscription
    from src.models.historico_assinatura import SubscriptionHistory
    print("[DEBUG] Importação de assinatura e historico OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar assinatura: {e}")

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
    from src.routes.diarios import diaries_bp
    print("[DEBUG] Importação de diarios routes OK")
except Exception as e:
    print(f"[ERROR] Erro ao importar diarios routes: {e}")

try:
    # Importar após inicialização do Mercado Pago
    pass
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

# Comentado - removendo importação do mercadopago_webhook
# try:
#     from src.routes.mercadopago_webhook import mercadopago_webhook_bp
#     print("[DEBUG] Importação de mercadopago_webhook routes OK")
# except Exception as e:
#     print(f"[ERROR] Erro ao importar mercadopago_webhook routes: {e}")



# Configuração do Flask com debug de static folder
static_path = os.path.join(os.path.dirname(__file__), 'static')
print(f"[DEBUG] Static folder path: {static_path}")
print(f"[DEBUG] Static folder exists: {os.path.exists(static_path)}")

app = Flask(__name__, static_folder=static_path)
# Configuração da SECRET_KEY
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'consultorio-psicologia-secret-key-2024')

# Configurações de sessão para desenvolvimento
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Permite acesso via JavaScript
app.config['SESSION_COOKIE_SECURE'] = False    # Para desenvolvimento local (HTTP)
app.config['SESSION_COOKIE_SAMESITE'] = None   # Permite cookies cross-site
app.config['SESSION_COOKIE_DOMAIN'] = None     # Permite localhost
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
print("[DEBUG] Configurações de sessão aplicadas para desenvolvimento")

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
    
    
    return response

# Handler de erro personalizado para debugging
from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    """Handler global para todas as exceções"""
    # Se for uma exceção HTTP, deixar o Flask lidar com ela
    if isinstance(e, HTTPException):
        return e
    
    # Para exceções não-HTTP, logar detalhes e retornar erro 500
    error_id = str(hash(str(e)))[:8]  # ID único para rastreamento
    
    print(f"[ERROR] EXCEÇÃO NÃO TRATADA [ID: {error_id}]: {str(e)}")
    print(f"[ERROR] Tipo da exceção: {type(e).__name__}")
    print(f"[ERROR] Traceback completo:")
    print(traceback.format_exc())
    
    # Em desenvolvimento, retornar detalhes do erro
    if os.getenv('FLASK_ENV') != 'production':
        return jsonify({
            'error': 'Erro Interno do Servidor',
            'message': str(e),
            'type': type(e).__name__,
            'error_id': error_id,
            'traceback': traceback.format_exc().split('\n')
        }), 500
    else:
        # Em produção, retornar erro genérico mas logar detalhes
        return jsonify({
            'error': 'Erro Interno do Servidor',
            'message': 'Ocorreu um erro interno no servidor',
            'error_id': error_id
        }), 500

@app.errorhandler(500)
def handle_500_error(e):
    """Handler específico para erros 500"""
    error_id = str(hash(str(e)))[:8]
    print(f"[ERROR] ERRO 500 [ID: {error_id}]: {str(e)}")
    
    return jsonify({
        'error': 'Erro Interno do Servidor',
        'message': 'Erro interno do servidor',
        'error_id': error_id
    }), 500

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
    app.register_blueprint(diaries_bp, url_prefix='/api')
    print("[DEBUG] Blueprint diaries_bp registrado")
except Exception as e:
    print(f"[ERROR] Erro ao registrar diaries_bp: {e}")

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
    print(f"[DEBUG] DATABASE_URL encontrada: {database_url[:50]}...")
    # Render usa postgres:// mas SQLAlchemy precisa de postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print("[DEBUG] URL do PostgreSQL corrigida de postgres:// para postgresql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print("[DEBUG] Configuração do banco PostgreSQL aplicada")
else:
    # Desenvolvimento - SQLite local
    sqlite_path = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_path
    print(f"[DEBUG] Configuração do banco SQLite aplicada: {sqlite_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Inicializar banco de dados
def initialize_database():
    """Inicializa o banco de dados de forma robusta"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"[DEBUG] Tentativa {retry_count + 1}/{max_retries} de inicialização do banco...")
            print(f"[DEBUG] URI do banco: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Testar conexão com timeout menor
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("[DEBUG] Conexão com o banco de dados testada com sucesso")
            
            db.create_all()
            print("[DEBUG] Tabelas do banco de dados criadas/verificadas com sucesso")
            
            # CORREÇÃO AUTOMÁTICA DE ISOLAMENTO
            print("[STARTUP] Verificando isolamento de dados...")
            try:
                # Verificar se existem registros sem user_id
                from src.models.especialidade import Especialidade
                from src.models.funcionario import Funcionario
                
                esp_null = Especialidade.query.filter_by(user_id=None).count()
                func_null = Funcionario.query.filter_by(user_id=None).count()
                
                if esp_null > 0 or func_null > 0:
                    print(f"[STARTUP] Problema detectado: {esp_null} especialidades e {func_null} funcionários sem user_id")
                    print("[STARTUP] Aplicando correções automáticas...")
                    
                    # Corrigir registros sem user_id
                    if esp_null > 0:
                        especialidades_sem_user = Especialidade.query.filter_by(user_id=None).all()
                        for i, esp in enumerate(especialidades_sem_user):
                            esp.user_id = (i % 2) + 1  # Distribuir entre usuários 1 e 2
                        print(f"[STARTUP] {esp_null} especialidades corrigidas")
                    
                    if func_null > 0:
                        funcionarios_sem_user = Funcionario.query.filter_by(user_id=None).all()
                        for i, func in enumerate(funcionarios_sem_user):
                            func.user_id = (i % 2) + 1  # Distribuir entre usuários 1 e 2
                        print(f"[STARTUP] {func_null} funcionários corrigidos")
                    
                    db.session.commit()
                    print("[STARTUP] Correções aplicadas com sucesso!")
                else:
                    print("[STARTUP] Isolamento OK - nenhuma correção necessária")
                    
            except Exception as e:
                print(f"[STARTUP] Erro na verificação de isolamento: {e}")
                db.session.rollback()
            
            # Verificar se há funcionários no banco
            try:
                funcionarios_count = Funcionario.query.count()
                print(f"[DEBUG] Total de funcionários no banco: {funcionarios_count}")
                
                if funcionarios_count > 0:
                    funcionarios = Funcionario.query.limit(5).all()
                    for func in funcionarios:
                        print(f"[DEBUG] Funcionário encontrado: ID={func.id}, Nome='{func.nome}', User_ID={func.user_id}")
            except Exception as e:
                print(f"[DEBUG] Erro ao verificar funcionários: {e}")
            
            print("[SUCCESS] Inicialização do banco concluída com sucesso!")
            return True
            
        except Exception as e:
            retry_count += 1
            print(f"[ERROR] Tentativa {retry_count} falhou: {e}")
            
            if retry_count < max_retries:
                import time
                wait_time = retry_count * 2  # Espera progressiva: 2s, 4s, 6s
                print(f"[RETRY] Aguardando {wait_time}s antes da próxima tentativa...")
                time.sleep(wait_time)
            else:
                print("[ERROR] Todas as tentativas de conexão falharam")
                print("[WARNING] Aplicação continuará sem inicialização completa do banco")
                import traceback
                print(f"[ERROR] Traceback completo: {traceback.format_exc()}")
                return False
    
    return False

# Executar inicialização robusta
with app.app_context():
    database_initialized = initialize_database()
    if not database_initialized:
        print("[WARNING] Banco não foi inicializado completamente, mas aplicação continuará")
    
    # Criar usuário administrador automaticamente em produção
    try:
        print("[STARTUP] Verificando estrutura da base de dados...")
        from src.models.usuario import User
        from src.models.assinatura import Subscription
        from datetime import datetime, timedelta
        from sqlalchemy import text, inspect
        
        # Verificar e adicionar coluna 'role' se não existir
        try:
            inspector = inspect(db.engine)
            columns = inspector.get_columns('users')
            column_names = [col['name'] for col in columns]
            
            if 'role' not in column_names:
                print("[MIGRATION] Coluna 'role' não encontrada. Adicionando...")
                
                # Adicionar coluna 'role' com valor padrão 'user'
                db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                
                # Popular todos os usuários existentes com role 'user'
                db.session.execute(text("UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''"))
                db.session.commit()
                
                print("✅ [MIGRATION] Coluna 'role' adicionada e usuários existentes populados com role 'user'")
            else:
                print("✅ [MIGRATION] Coluna 'role' já existe")
            
            # Verificar e adicionar coluna 'created_at' se não existir
            if 'created_at' not in column_names:
                print("[MIGRATION] Coluna 'created_at' não encontrada. Adicionando...")
                
                # Detectar tipo de banco de dados
                db_url = os.getenv('DATABASE_URL', '')
                is_postgres = 'postgresql' in db_url or 'postgres' in db_url
                
                if is_postgres:
                    # PostgreSQL
                    db.session.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                else:
                    # SQLite
                    db.session.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                
                # Popular usuários existentes com data atual
                db.session.execute(text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
                db.session.commit()
                
                print("✅ [MIGRATION] Coluna 'created_at' adicionada e usuários existentes populados")
            else:
                print("✅ [MIGRATION] Coluna 'created_at' já existe")
                
            # NOVO: Migrar coluna 'emocao_intensidades' na tabela 'diary_entries'
            try:
                diary_columns = inspector.get_columns('diary_entries')
                diary_column_names = [col['name'] for col in diary_columns]
                if 'emocao_intensidades' not in diary_column_names:
                    print("[MIGRATION] Coluna 'emocao_intensidades' não encontrada em 'diary_entries'. Adicionando...")
                    # Usar TEXT para compatibilidade entre SQLite/PostgreSQL
                    db.session.execute(text("ALTER TABLE diary_entries ADD COLUMN emocao_intensidades TEXT"))
                    db.session.commit()
                    print("✅ [MIGRATION] Coluna 'emocao_intensidades' adicionada em 'diary_entries'")
                else:
                    print("✅ [MIGRATION] Coluna 'emocao_intensidades' já existe em 'diary_entries'")
            except Exception as diary_migration_error:
                print(f"[WARNING] Erro ao migrar 'diary_entries': {diary_migration_error}")
                db.session.rollback()

            # NOVO: Migrar coluna 'ativo' na tabela 'patients'
            try:
                patient_columns = inspector.get_columns('patients')
                patient_column_names = [col['name'] for col in patient_columns]
                if 'ativo' not in patient_column_names:
                    print("[MIGRATION] Coluna 'ativo' não encontrada em 'patients'. Adicionando...")

                    db_url = os.getenv('DATABASE_URL', '')
                    is_postgres = 'postgresql' in db_url or 'postgres' in db_url

                    if is_postgres:
                        db.session.execute(text("ALTER TABLE patients ADD COLUMN ativo BOOLEAN DEFAULT TRUE NOT NULL"))
                        db.session.execute(text("UPDATE patients SET ativo = TRUE WHERE ativo IS NULL"))
                    else:
                        db.session.execute(text("ALTER TABLE patients ADD COLUMN ativo BOOLEAN DEFAULT 1 NOT NULL"))
                        db.session.execute(text("UPDATE patients SET ativo = 1 WHERE ativo IS NULL"))

                    db.session.commit()
                    print("✅ [MIGRATION] Coluna 'ativo' adicionada em 'patients'")
                else:
                    print("✅ [MIGRATION] Coluna 'ativo' já existe em 'patients'")
            except Exception as patients_migration_error:
                print(f"[WARNING] Erro ao migrar 'patients': {patients_migration_error}")
                db.session.rollback()

            # NOVO: Migrar coluna 'diario_tcc_ativo' na tabela 'patients'
            try:
                patient_columns = inspector.get_columns('patients')
                patient_column_names = [col['name'] for col in patient_columns]
                if 'diario_tcc_ativo' not in patient_column_names:
                    print("[MIGRATION] Coluna 'diario_tcc_ativo' não encontrada em 'patients'. Adicionando...")

                    db_url = os.getenv('DATABASE_URL', '')
                    is_postgres = 'postgresql' in db_url or 'postgres' in db_url

                    if is_postgres:
                        db.session.execute(text("ALTER TABLE patients ADD COLUMN diario_tcc_ativo BOOLEAN DEFAULT FALSE NOT NULL"))
                        db.session.execute(text("UPDATE patients SET diario_tcc_ativo = FALSE WHERE diario_tcc_ativo IS NULL"))
                    else:
                        db.session.execute(text("ALTER TABLE patients ADD COLUMN diario_tcc_ativo BOOLEAN DEFAULT 0 NOT NULL"))
                        db.session.execute(text("UPDATE patients SET diario_tcc_ativo = 0 WHERE diario_tcc_ativo IS NULL"))

                    db.session.commit()
                    print("✅ [MIGRATION] Coluna 'diario_tcc_ativo' adicionada em 'patients'")
                else:
                    print("✅ [MIGRATION] Coluna 'diario_tcc_ativo' já existe em 'patients'")
            except Exception as patients_flag_migration_error:
                print(f"[WARNING] Erro ao migrar coluna 'diario_tcc_ativo' em 'patients': {patients_flag_migration_error}")
                db.session.rollback()
            
            # População automática de roles para usuários existentes
            print("[STARTUP] Verificando e populando roles de usuários...")
            
            # Contar usuários sem role ou com role vazio
            users_without_role = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE role IS NULL OR role = ''")
            ).scalar()
            
            if users_without_role > 0:
                print(f"[STARTUP] Encontrados {users_without_role} usuário(s) sem role definido")
                
                # Popular usuários sem role com 'user'
                result = db.session.execute(
                    text("UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''")
                )
                db.session.commit()
                
                print(f"✅ [STARTUP] {result.rowcount} usuário(s) populado(s) com role 'user'")
            else:
                print("✅ [STARTUP] Todos os usuários já possuem roles definidos")
                
            # Garantir que existe pelo menos um admin
            admin_count = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            ).scalar()
            
            if admin_count == 0:
                print("[STARTUP] Nenhum administrador encontrado. Promovendo primeiro usuário a admin...")
                # Promover o primeiro usuário a admin se não houver nenhum
                
            # População automática de campos obrigatórios para usuários existentes
            print("[STARTUP] Verificando e populando campos obrigatórios...")
            
            # Verificar usuários sem telefone
            users_without_phone = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE telefone IS NULL OR telefone = ''")
            ).scalar()
            
            if users_without_phone > 0:
                print(f"[STARTUP] Encontrados {users_without_phone} usuário(s) sem telefone")
                
                # Popular usuários sem telefone com valor padrão
                result = db.session.execute(
                    text("UPDATE users SET telefone = '(00) 00000-0000' WHERE telefone IS NULL OR telefone = ''")
                )
                db.session.commit()
                
                print(f"✅ [STARTUP] {result.rowcount} usuário(s) populado(s) com telefone padrão")
            else:
                print("✅ [STARTUP] Todos os usuários já possuem telefone definido")
            
            # Verificar usuários sem data de nascimento
            users_without_birthdate = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE data_nascimento IS NULL")
            ).scalar()
            
            if users_without_birthdate > 0:
                print(f"[STARTUP] Encontrados {users_without_birthdate} usuário(s) sem data de nascimento")
                
                # Popular usuários sem data de nascimento com valor padrão
                result = db.session.execute(
                    text("UPDATE users SET data_nascimento = '1990-01-01' WHERE data_nascimento IS NULL")
                )
                db.session.commit()
                
                print(f"✅ [STARTUP] {result.rowcount} usuário(s) populado(s) com data de nascimento padrão")
            else:
                print("✅ [STARTUP] Todos os usuários já possuem data de nascimento definida")
            
            # Verificar se há pelo menos um administrador
            admin_count = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            ).scalar()
            
            if admin_count == 0:
                print("[STARTUP] Nenhum administrador encontrado. Promovendo primeiro usuário...")
                # Promover o primeiro usuário a admin se não houver nenhum
                first_user = db.session.execute(
                    text("SELECT id FROM users ORDER BY id LIMIT 1")
                ).first()
                
                if first_user:
                    db.session.execute(
                        text("UPDATE users SET role = 'admin' WHERE id = :user_id"),
                        {"user_id": first_user[0]}
                    )
                    db.session.commit()
                    print(f"✅ [STARTUP] Usuário ID {first_user[0]} promovido a administrador")
            else:
                print(f"✅ [STARTUP] {admin_count} administrador(es) encontrado(s)")
                
        except Exception as migration_error:
            print(f"[WARNING] Erro na migração/população de roles: {migration_error}")
            db.session.rollback()
        
        print("[STARTUP] Verificando usuário administrador...")
        
        # Verificar se já existe um usuário admin (por email OU username)
        existing_admin = User.query.filter(
            (User.email == 'admin@consultorio.com') | 
            (User.username == 'admin')
        ).first()
        
        # Em produção, criar admin automaticamente se não existir
        is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('DATABASE_URL') is not None
        
        if not existing_admin:
            if is_production:
                print("[PRODUCTION] Criando usuário administrador automaticamente...")
            else:
                print("[STARTUP] Criando usuário administrador...")
            
            # Criar usuário administrador
            admin_user = User(
                username='admin',
                email='admin@consultorio.com'
            )
            admin_user.role = 'admin'  # Definir role após criar a instância
            admin_user.set_password('admin123')  # Senha padrão - ALTERE APÓS O PRIMEIRO LOGIN
            
            db.session.add(admin_user)
            db.session.flush()  # Para obter o ID do usuário
            
            # Criar assinatura ativa para o admin (válida por 1 ano)
            end_date = datetime.now() + timedelta(days=365)
            admin_subscription = Subscription(
                user_id=admin_user.id,
                plan_type='admin',
                status='active',
                start_date=datetime.now(),
                end_date=end_date,
                price=0.0,
                auto_renew=True
            )
            
            db.session.add(admin_subscription)
            db.session.commit()
            
            if is_production:
                print("🚀 [PRODUCTION] Usuário administrador criado automaticamente no deploy!")
                print("📧 Email: admin@consultorio.com")
                print("🔑 Senha: admin123")
                print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            else:
                print("✅ Usuário administrador criado com sucesso!")
                print("📧 Email: admin@consultorio.com")
                print("🔑 Senha: admin123 (ALTERE APÓS O PRIMEIRO LOGIN)")
        else:
            if is_production:
                print("✅ [PRODUCTION] Usuário administrador já existe no ambiente de produção.")
            else:
                print("✅ Usuário administrador já existe.")
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar usuário administrador: {e}")
        db.session.rollback()

# Comentado - removendo inicialização do Mercado Pago
# try:
#     from src.utils.mercadopago_config import init_mercadopago
#     init_mercadopago(app)
#     print("[DEBUG] Mercado Pago inicializado com sucesso")
# except Exception as e:
#     print(f"[ERROR] Erro ao inicializar Mercado Pago: {e}")

# Importar blueprints que dependem do Mercado Pago após inicialização
try:
    from src.routes.assinaturas import subscriptions_bp
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    print("[DEBUG] Blueprint subscriptions_bp importado e registrado")
except Exception as e:
    print(f"[ERROR] Erro ao importar/registrar subscriptions_bp: {e}")

# Comentado - removendo registro do mercadopago_webhook_bp
# try:
#     from src.routes.mercadopago_webhook import mercadopago_webhook_bp
#     app.register_blueprint(mercadopago_webhook_bp, url_prefix='/api')
#     print("[DEBUG] Blueprint mercadopago_webhook_bp importado e registrado após inicialização do Mercado Pago")
# except Exception as e:
#     print(f"[ERROR] Erro ao importar/registrar mercadopago_webhook_bp: {e}")

try:
    from src.routes.admin import admin_bp
    app.register_blueprint(admin_bp)
    print("[DEBUG] Blueprint admin_bp importado e registrado")
except Exception as e:
    print(f"[ERROR] Erro ao importar/registrar admin_bp: {e}")

# Definir rotas específicas ANTES da rota catch-all
@app.route('/')
def home():
    """Rota principal - redireciona baseado no status de login e assinatura"""
    try:
        print(f"[DEBUG] Acessando rota principal. Session: {dict(session)}")
        
        # Verificar se o usuário está logado
        if 'user_id' in session:
            print(f"[DEBUG] Usuário logado com ID: {session['user_id']}, verificando tipo de usuário...")
            
            # Verificar se é administrador
            user = User.query.get(session['user_id'])
            if user:
                # Verificar se o usuário tem role definido, se não tiver, definir como 'user'
                user_role = getattr(user, 'role', None) or 'user'
                if user_role is None or user_role == '':
                    user.role = 'user'
                    db.session.commit()
                    user_role = 'user'
                
                print(f"[DEBUG] Usuário encontrado: {user.username}, email: {user.email}, role: {user_role}")
                if user.is_admin():
                    print("[DEBUG] Usuário é administrador, redirecionando para dashboard admin")
                    return redirect('/admin/dashboard')
                else:
                    print(f"[DEBUG] Usuário não é admin (role: {user_role}), continuando verificação de assinatura")
            else:
                print(f"[DEBUG] Usuário com ID {session['user_id']} não encontrado no banco")
            
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

@app.route('/assinaturas')
def assinaturas():
    """Rota específica para a página de assinaturas"""
    print("[DEBUG] Rota /assinaturas acessada")
    return send_from_directory(app.static_folder, 'assinaturas.html')

@app.route('/historico-assinaturas.html')
def historico_assinaturas():
    """Rota específica para a página de histórico de assinaturas"""
    print("[DEBUG] Rota /historico-assinaturas.html acessada")
    return send_from_directory(app.static_folder, 'historico-assinaturas.html')

@app.route('/perfil')
def perfil():
    """Rota específica para a página de perfil do usuário"""
    print("[DEBUG] Rota /perfil acessada")
    return send_from_directory(app.static_folder, 'perfil.html')

# Rotas de pagamento desabilitadas - funcionalidade removida
# @app.route('/payment/success')
# def payment_success():
#     return send_from_directory('templates', 'payment_success.html')

# @app.route('/payment/failure')
# def payment_failure():
#     return send_from_directory('templates', 'payment_failure.html')

# @app.route('/checkout')
# def checkout():
#     return send_from_directory(app.static_folder, 'checkout.html')

# IMPORTANTE: A rota catch-all deve ser definida APÓS todos os blueprints
# para não interceptar as rotas da API
@app.route('/<path:path>')
def serve(path):
    # Não interceptar rotas da API - deixar os blueprints processarem
    if path.startswith('api/'):
        # Se chegou aqui, a rota da API não foi encontrada nos blueprints
        return jsonify({'error': 'Rota da API não encontrada', 'path': path}), 404
        
    # Interceptar apenas rotas específicas que não são da API
    if path in ['medicos', 'psicologos', 'funcionarios', 'especialidades']:
        return jsonify({'error': 'Rota não encontrada', 'path': path}), 404
        
    print(f"[DEBUG] FUNÇÃO SERVE CHAMADA - Tentando servir arquivo: {path}")
    static_folder_path = app.static_folder
    print(f"[DEBUG] Static folder path: {static_folder_path}")
    
    if static_folder_path is None:
        print("[ERROR] Static folder not configured")
        return jsonify({'error': 'Pasta estática não configurada'}), 404

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
        return jsonify({'error': 'Arquivo não encontrado', 'path': path}), 404


if __name__ == '__main__':
    print("[DEBUG] Iniciando Flask com debug=True na porta 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
