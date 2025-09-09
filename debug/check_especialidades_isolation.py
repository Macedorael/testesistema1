#!/usr/bin/env python3
"""
Script para verificar isolamento de especialidades entre usuários
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.especialidade import Especialidade
from src.models.usuario import User
from src.models.base import db

def check_especialidades_isolation():
    """Verifica se há especialidades compartilhadas entre usuários"""
    with app.app_context():
        print("=== VERIFICAÇÃO DE ISOLAMENTO DE ESPECIALIDADES ===")
        
        # Buscar todas as especialidades
        especialidades = Especialidade.query.all()
        print(f"Total de especialidades no banco: {len(especialidades)}")
        
        if not especialidades:
            print("Nenhuma especialidade encontrada.")
            return
        
        # Agrupar por user_id
        especialidades_por_usuario = {}
        for esp in especialidades:
            if esp.user_id not in especialidades_por_usuario:
                especialidades_por_usuario[esp.user_id] = []
            especialidades_por_usuario[esp.user_id].append(esp)
        
        print(f"\nEspecialidades distribuídas entre {len(especialidades_por_usuario)} usuários:")
        
        for user_id, user_especialidades in especialidades_por_usuario.items():
            user = User.query.get(user_id)
            user_email = user.email if user else "Usuário não encontrado"
            print(f"\nUsuário ID {user_id} ({user_email}): {len(user_especialidades)} especialidades")
            
            for esp in user_especialidades:
                print(f"  - ID: {esp.id}, Nome: '{esp.nome}'")
        
        # Verificar nomes duplicados
        print("\n=== VERIFICAÇÃO DE NOMES DUPLICADOS ===")
        nomes_especialidades = {}
        for esp in especialidades:
            nome = esp.nome.lower().strip()
            if nome not in nomes_especialidades:
                nomes_especialidades[nome] = []
            nomes_especialidades[nome].append(esp)
        
        duplicados_encontrados = False
        for nome, especialidades_com_nome in nomes_especialidades.items():
            if len(especialidades_com_nome) > 1:
                duplicados_encontrados = True
                print(f"\nNome duplicado: '{nome}'")
                for esp in especialidades_com_nome:
                    user = User.query.get(esp.user_id)
                    user_email = user.email if user else "Usuário não encontrado"
                    print(f"  - ID: {esp.id}, User_ID: {esp.user_id} ({user_email})")
        
        if not duplicados_encontrados:
            print("Nenhum nome duplicado encontrado.")
        
        # Verificar constraint unique
        print("\n=== VERIFICAÇÃO DE CONSTRAINT UNIQUE ===")
        try:
            # Tentar criar duas especialidades com mesmo nome para usuários diferentes
            users = User.query.limit(2).all()
            if len(users) >= 2:
                test_name = "Teste Constraint Unique"
                
                # Verificar se já existe
                existing = Especialidade.query.filter_by(nome=test_name).first()
                if existing:
                    print(f"Especialidade de teste '{test_name}' já existe (User_ID: {existing.user_id})")
                else:
                    print(f"Tentando criar especialidade '{test_name}' para dois usuários diferentes...")
                    
                    # Criar primeira especialidade
                    esp1 = Especialidade(user_id=users[0].id, nome=test_name, descricao="Teste 1")
                    db.session.add(esp1)
                    db.session.commit()
                    print(f"Primeira especialidade criada para User_ID: {users[0].id}")
                    
                    try:
                        # Tentar criar segunda especialidade com mesmo nome
                        esp2 = Especialidade(user_id=users[1].id, nome=test_name, descricao="Teste 2")
                        db.session.add(esp2)
                        db.session.commit()
                        print(f"Segunda especialidade criada para User_ID: {users[1].id}")
                        print("PROBLEMA: Constraint unique não está funcionando corretamente!")
                        
                        # Limpar especialidades de teste
                        db.session.delete(esp1)
                        db.session.delete(esp2)
                        db.session.commit()
                        
                    except Exception as e:
                        db.session.rollback()
                        print(f"Constraint unique funcionando: {str(e)}")
                        
                        # Limpar primeira especialidade
                        db.session.delete(esp1)
                        db.session.commit()
            else:
                print("Não há usuários suficientes para testar constraint unique.")
                
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao testar constraint unique: {str(e)}")

if __name__ == '__main__':
    check_especialidades_isolation()