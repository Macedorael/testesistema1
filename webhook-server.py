#!/usr/bin/env python3
"""
🔔 Servidor Webhook para Auto-Deploy
Recebe notificações do GitHub e executa deploy automaticamente
"""

import os
import sys
import json
import hmac
import hashlib
import subprocess
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Configurações
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'seu_secret_aqui')
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_PATH, 'deploy.log')

def log_message(message):
    """Registra mensagem no log com timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    print(log_entry.strip())
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def verify_signature(payload_body, signature_header):
    """Verifica a assinatura do webhook do GitHub"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload_body,
        hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def execute_deploy():
    """Executa o processo de deploy local (sem Docker Hub)"""
    try:
        log_message("🚀 Iniciando deploy local automático...")
        log_message("📍 Build será feito localmente (sem Docker Hub)")
        
        # Muda para o diretório do repositório
        os.chdir(REPO_PATH)
        
        # Verifica se há novos commits primeiro
        log_message("🔍 Verificando novos commits...")
        try:
            subprocess.run(['git', 'fetch', 'origin', 'master'], 
                         check=True, capture_output=True, timeout=30)
            
            result = subprocess.run(['git', 'rev-list', 'HEAD..origin/master', '--count'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                new_commits = int(result.stdout.strip())
                if new_commits == 0:
                    log_message("✅ Nenhum commit novo - deploy não necessário")
                    return True, "Nenhum commit novo encontrado"
                else:
                    log_message(f"🎉 {new_commits} novo(s) commit(s) encontrado(s)")
            
        except Exception as e:
            log_message(f"⚠️ Erro ao verificar commits: {e}")
        
        # Executa o script de deploy apropriado
        if os.name == 'nt':  # Windows
            log_message("🖥️ Executando deploy no Windows...")
            result = subprocess.run(['auto-deploy.bat'], 
                                  capture_output=True, text=True, timeout=600)
        else:  # Linux/Mac
            log_message("🐧 Executando deploy no Linux/Mac...")
            result = subprocess.run(['./auto-deploy.sh'], 
                                  capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            log_message("✅ Deploy local concluído com sucesso!")
            log_message("🌐 Aplicação disponível em: http://localhost:5000")
            return True, result.stdout
        else:
            log_message(f"❌ Erro no deploy local: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        log_message("⏰ Timeout no deploy (>10min)")
        return False, "Deploy timeout - processo muito longo"
    except Exception as e:
        log_message(f"💥 Erro inesperado no deploy: {str(e)}")
        return False, str(e)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para receber webhooks do GitHub"""
    
    # Verifica se é um POST request
    if request.method != 'POST':
        return jsonify({'error': 'Método não permitido'}), 405
    
    # Obtém dados do request
    payload_body = request.get_data()
    signature_header = request.headers.get('X-Hub-Signature-256')
    
    # Verifica assinatura (se configurada)
    if WEBHOOK_SECRET != 'seu_secret_aqui':
        if not verify_signature(payload_body, signature_header):
            log_message("🔒 Assinatura inválida no webhook")
            return jsonify({'error': 'Assinatura inválida'}), 401
    
    try:
        # Parse do JSON
        payload = json.loads(payload_body)
        
        # Verifica se é um push para master/main
        if payload.get('ref') in ['refs/heads/master', 'refs/heads/main']:
            
            commit_info = payload.get('head_commit', {})
            author = commit_info.get('author', {}).get('name', 'Desconhecido')
            message = commit_info.get('message', 'Sem mensagem')
            commit_id = commit_info.get('id', 'N/A')[:7]
            
            log_message(f"📥 Novo commit recebido:")
            log_message(f"   👤 Autor: {author}")
            log_message(f"   💬 Mensagem: {message}")
            log_message(f"   🔗 ID: {commit_id}")
            
            # Executa deploy
            success, output = execute_deploy()
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Deploy executado com sucesso',
                    'commit': commit_id
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Erro no deploy',
                    'error': output
                }), 500
        else:
            log_message(f"ℹ️ Push ignorado (branch: {payload.get('ref')})")
            return jsonify({'status': 'ignored', 'message': 'Branch ignorada'}), 200
            
    except json.JSONDecodeError:
        log_message("📄 Erro ao fazer parse do JSON")
        return jsonify({'error': 'JSON inválido'}), 400
    except Exception as e:
        log_message(f"💥 Erro no webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar status do servidor"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'repo_path': REPO_PATH
    })

@app.route('/logs', methods=['GET'])
def logs():
    """Endpoint para visualizar logs recentes"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Retorna últimas 50 linhas
                recent_logs = ''.join(lines[-50:])
        else:
            recent_logs = "Nenhum log encontrado"
            
        return f"<pre>{recent_logs}</pre>", 200, {'Content-Type': 'text/html'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    log_message("🌐 Iniciando servidor webhook...")
    log_message(f"📁 Diretório do repositório: {REPO_PATH}")
    
    # Porta configurável via variável de ambiente
    port = int(os.environ.get('WEBHOOK_PORT', 8080))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )