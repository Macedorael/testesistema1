from flask import Blueprint, jsonify, request, session
from src.models.usuario import User, db
from src.models.assinatura import Subscription
from src.models.password_reset import PasswordResetToken
from src.utils.auth import login_required, get_current_user
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

user_bp = Blueprint("user", __name__)

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    # Verificar se o usuário existe
    if not user:
        return jsonify({"error": "Usuário não encontrado. Verifique o email digitado."}), 401
    
    # Verificar se a senha está correta
    if not user.check_password(password):
        return jsonify({"error": "Senha incorreta. Tente novamente."}), 401
    
    # Login bem-sucedido
    session['user_id'] = user.id
    session['username'] = user.username
    
    # Verificar se o usuário tem uma assinatura ativa
    active_subscription = Subscription.query.filter_by(
        user_id=user.id,
        status='active'
    ).filter(
        Subscription.end_date > datetime.utcnow()
    ).first()
    
    if active_subscription:
        return jsonify({
            "message": "Login bem-sucedido!",
            "user": {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            "redirect": "/"
        }), 200
    else:
        return jsonify({
            "message": "Login bem-sucedido!",
            "user": {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            "redirect": "/assinaturas.html"
        }), 200

@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logout realizado com sucesso"}), 200

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    # Validações básicas
    if not username or not email or not password:
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres"}), 400
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Nome de usuário já existe"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já está cadastrado"}), 400
    
    try:
        # Criar novo usuário
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "Usuário cadastrado com sucesso!",
            "user": {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao cadastrar usuário"}), 500

@user_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    """Lista todos os usuários (sem senhas)"""
    try:
        users = User.query.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        return jsonify({
            "success": True,
            "data": users_data
        }), 200
    except Exception as e:
        return jsonify({"error": "Erro ao buscar usuários"}), 500

@user_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    """Obtém um usuário específico"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        return jsonify({
            "success": True,
            "data": {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Erro ao buscar usuário"}), 500

@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    """Atualiza um usuário"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        data = request.json
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        # Validações
        if username and username != user.username:
            if User.query.filter_by(username=username).first():
                return jsonify({"error": "Nome de usuário já existe"}), 400
            user.username = username
        
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                return jsonify({"error": "Email já está cadastrado"}), 400
            user.email = email
        
        if password:
            if len(password) < 6:
                return jsonify({"error": "A senha deve ter pelo menos 6 caracteres"}), 400
            user.set_password(password)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Usuário atualizado com sucesso!",
            "data": {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao atualizar usuário"}), 500

@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    """Remove um usuário"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Usuário excluído com sucesso"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao excluir usuário"}), 500



@user_bp.route("/me", methods=["GET"])
@login_required
def get_current_user_info():
    user = get_current_user()
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })
    return jsonify({"error": "Usuário não encontrado"}), 404

@user_bp.route("/esqueci-senha", methods=["POST"])
def forgot_password():
    """Rota para solicitar recuperação de senha"""
    data = request.json
    email = data.get("email")
    
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400
    
    # Verificar se o usuário existe
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email não encontrado no sistema"}), 404
    
    try:
        # Criar token de recuperação
        reset_token = PasswordResetToken.create_for_user(user.id)
        
        # Enviar email com o token
        success = send_password_reset_email(user.email, user.username, reset_token.token)
        
        if success:
            return jsonify({
                "message": "Email de recuperação enviado com sucesso! Verifique sua caixa de entrada."
            }), 200
        else:
            return jsonify({"error": "Erro ao enviar email. Tente novamente mais tarde."}), 500
            
    except Exception as e:
        print(f"[ERROR] Erro ao processar recuperação de senha: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@user_bp.route("/resetar-senha", methods=["POST"])
def reset_password():
    """Rota para resetar senha com token"""
    data = request.json
    token = data.get("token")
    new_password = data.get("password")
    
    if not token or not new_password:
        return jsonify({"error": "Token e nova senha são obrigatórios"}), 400
    
    if len(new_password) < 6:
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres"}), 400
    
    # Verificar se o token é válido
    reset_token = PasswordResetToken.find_valid_token(token)
    if not reset_token:
        return jsonify({"error": "Token inválido ou expirado"}), 400
    
    try:
        # Buscar o usuário
        user = User.query.get(reset_token.user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        # Atualizar a senha
        user.set_password(new_password)
        
        # Marcar o token como usado
        reset_token.mark_as_used()
        
        db.session.commit()
        
        return jsonify({
            "message": "Senha alterada com sucesso! Você já pode fazer login com a nova senha."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Erro ao resetar senha: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

def send_password_reset_email(email, username, token):
    """Função para enviar email de recuperação de senha"""
    import os
    try:
        # Configurações do email do arquivo .env
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        if not sender_email or not sender_password:
            print("[ERROR] Configurações de email não encontradas no .env")
            return False
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Recuperação de Senha - Consultório Médico"
        
        # Corpo do email em HTML
        html_body = f"""
        <html>
        <body>
            <h2>Recuperação de Senha</h2>
            <p>Olá {username},</p>
            <p>Você solicitou a recuperação de sua senha no sistema do Consultório Médico.</p>
            <p>Para criar uma nova senha, clique no link abaixo:</p>
            <p><a href="{base_url}/resetar-senha.html?token={token}" 
               style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
               Resetar Senha</a></p>
            <p>Ou copie e cole este link no seu navegador:</p>
            <p>{base_url}/resetar-senha.html?token={token}</p>
            <p><strong>Este link expira em 30 minutos.</strong></p>
            <p>Se você não solicitou esta recuperação, ignore este email.</p>
            <br>
            <p>Atenciosamente,<br>Equipe do Consultório Médico</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Enviar email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        
        print(f"[DEBUG] Email de recuperação enviado para {email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erro ao enviar email: {e}")
        return False

