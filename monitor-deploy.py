#!/usr/bin/env python3
"""
👁️ Monitor de Deploy Contínuo
Monitora o repositório GitHub e executa deploy automaticamente
"""

import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path

class DeployMonitor:
    def __init__(self):
        self.repo_path = Path(__file__).parent
        self.log_file = self.repo_path / 'monitor.log'
        self.last_check_file = self.repo_path / '.last_check'
        self.github_repo = "Macedorael/testesistema1"  # Ajuste conforme necessário
        self.check_interval = 60  # segundos
        
    def log(self, message):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def get_last_check_time(self):
        """Obtém timestamp da última verificação"""
        try:
            if self.last_check_file.exists():
                with open(self.last_check_file, 'r') as f:
                    return datetime.fromisoformat(f.read().strip())
        except:
            pass
        return datetime.now() - timedelta(hours=1)
    
    def save_last_check_time(self):
        """Salva timestamp da verificação atual"""
        with open(self.last_check_file, 'w') as f:
            f.write(datetime.now().isoformat())
    
    def check_github_commits(self):
        """Verifica novos commits no GitHub via API"""
        try:
            url = f"https://api.github.com/repos/{self.github_repo}/commits"
            params = {
                'sha': 'master',  # ou 'main'
                'per_page': 10
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            commits = response.json()
            if not commits:
                return False, "Nenhum commit encontrado"
            
            latest_commit = commits[0]
            commit_date = datetime.fromisoformat(
                latest_commit['commit']['author']['date'].replace('Z', '+00:00')
            )
            
            last_check = self.get_last_check_time()
            
            if commit_date > last_check:
                commit_info = {
                    'sha': latest_commit['sha'][:7],
                    'author': latest_commit['commit']['author']['name'],
                    'message': latest_commit['commit']['message'].split('\n')[0],
                    'date': commit_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                return True, commit_info
            
            return False, "Nenhum commit novo"
            
        except requests.RequestException as e:
            return False, f"Erro na API do GitHub: {str(e)}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
    
    def check_local_commits(self):
        """Verifica novos commits localmente via git"""
        try:
            os.chdir(self.repo_path)
            
            # Fetch do repositório remoto
            result = subprocess.run(['git', 'fetch', 'origin', 'master'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False, f"Erro no git fetch: {result.stderr}"
            
            # Verifica diferenças
            result = subprocess.run(['git', 'rev-list', 'HEAD...origin/master', '--count'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return False, f"Erro ao verificar commits: {result.stderr}"
            
            commit_count = int(result.stdout.strip())
            
            if commit_count > 0:
                # Obtém informações do último commit
                result = subprocess.run(['git', 'log', 'origin/master', '-1', '--pretty=format:%H|%an|%s|%ai'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    parts = result.stdout.strip().split('|')
                    commit_info = {
                        'sha': parts[0][:7],
                        'author': parts[1],
                        'message': parts[2],
                        'date': parts[3]
                    }
                    return True, commit_info
            
            return False, "Nenhum commit novo"
            
        except subprocess.TimeoutExpired:
            return False, "Timeout na verificação git"
        except Exception as e:
            return False, f"Erro na verificação local: {str(e)}"
    
    def execute_deploy(self):
        """Executa o deploy local (sem Docker Hub)"""
        try:
            self.log("🚀 Iniciando deploy local...")
            self.log("📍 Build será feito localmente (sem Docker Hub)")
            
            os.chdir(self.repo_path)
            
            # Escolhe o script apropriado
            if os.name == 'nt':  # Windows
                script = 'auto-deploy.bat'
                self.log("🖥️ Executando deploy no Windows...")
            else:  # Linux/Mac
                script = './auto-deploy.sh'
                self.log("🐧 Executando deploy no Linux/Mac...")
            
            # Executa o deploy local
            result = subprocess.run([script], 
                                  capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.log("✅ Deploy local concluído com sucesso!")
                self.log("🌐 Aplicação disponível em: http://localhost:5000")
                self.log("📊 Para ver logs: docker-compose logs -f app")
                return True, result.stdout
            else:
                self.log(f"❌ Erro no deploy local: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.log("⏰ Timeout no deploy local (>10min)")
            return False, "Deploy timeout - processo muito longo"
        except Exception as e:
            self.log(f"💥 Erro no deploy local: {str(e)}")
            return False, str(e)
    
    def run_monitor(self):
        """Loop principal do monitor"""
        self.log("👁️ Iniciando monitor de deploy...")
        self.log(f"📁 Repositório: {self.repo_path}")
        self.log(f"🔄 Intervalo: {self.check_interval}s")
        
        while True:
            try:
                self.log("🔍 Verificando novos commits...")
                
                # Tenta verificação local primeiro (mais rápida)
                has_new, info = self.check_local_commits()
                
                # Se falhar, tenta via API do GitHub
                if not has_new and isinstance(info, str) and "Erro" in info:
                    self.log("⚠️ Verificação local falhou, tentando via API...")
                    has_new, info = self.check_github_commits()
                
                if has_new:
                    self.log(f"🆕 Novo commit encontrado:")
                    self.log(f"   👤 Autor: {info['author']}")
                    self.log(f"   💬 Mensagem: {info['message']}")
                    self.log(f"   🔗 SHA: {info['sha']}")
                    self.log(f"   📅 Data: {info['date']}")
                    
                    # Executa deploy
                    success, output = self.execute_deploy()
                    
                    if success:
                        self.log("🎉 Deploy automático concluído!")
                    else:
                        self.log(f"💥 Falha no deploy: {output}")
                    
                    # Atualiza timestamp da última verificação
                    self.save_last_check_time()
                    
                else:
                    if isinstance(info, str):
                        self.log(f"ℹ️ {info}")
                    else:
                        self.log("✅ Repositório atualizado")
                
                # Aguarda próxima verificação
                self.log(f"⏳ Aguardando {self.check_interval}s...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("🛑 Monitor interrompido pelo usuário")
                break
            except Exception as e:
                self.log(f"💥 Erro no monitor: {str(e)}")
                time.sleep(self.check_interval)

def main():
    """Função principal"""
    monitor = DeployMonitor()
    
    # Verifica argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check-once':
            # Executa apenas uma verificação
            has_new, info = monitor.check_local_commits()
            if has_new:
                print(f"✅ Novo commit: {info}")
                return 0
            else:
                print(f"ℹ️ {info}")
                return 1
        elif sys.argv[1] == '--deploy-now':
            # Força um deploy imediato
            success, output = monitor.execute_deploy()
            if success:
                print("✅ Deploy concluído")
                return 0
            else:
                print(f"❌ Erro: {output}")
                return 1
    
    # Executa monitor contínuo
    monitor.run_monitor()
    return 0

if __name__ == '__main__':
    sys.exit(main())