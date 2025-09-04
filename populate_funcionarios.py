#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com funcionários de teste
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from flask import Flask
    from src.models.base import db
    from src.models.funcionario import Funcionario
    from src.models.especialidade import Especialidade
    
    # Criar aplicação Flask
    app = Flask(__name__)
    
    # Configurar banco de dados
    if os.getenv('DATABASE_URL'):
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"[DEBUG] Usando PostgreSQL: {database_url[:50]}...")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
        print("[DEBUG] Usando SQLite local")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'temp-key-for-script'
    
    db.init_app(app)
    
    with app.app_context():
        print("[DEBUG] Iniciando população do banco de dados...")
        
        # Verificar se já existem funcionários
        funcionarios_existentes = Funcionario.query.count()
        print(f"[DEBUG] Funcionários existentes: {funcionarios_existentes}")
        
        if funcionarios_existentes > 0:
            resposta = input("Já existem funcionários no banco. Deseja continuar e adicionar mais? (s/n): ")
            if resposta.lower() != 's':
                print("[INFO] Operação cancelada pelo usuário")
                sys.exit(0)
        
        # Criar especialidades se não existirem
        especialidades_data = [
            {'nome': 'Psicologia Clínica', 'descricao': 'Atendimento psicológico individual e familiar'},
            {'nome': 'Psicologia Infantil', 'descricao': 'Especialização em atendimento a crianças e adolescentes'},
            {'nome': 'Terapia de Casal', 'descricao': 'Atendimento especializado para casais'},
            {'nome': 'Neuropsicologia', 'descricao': 'Avaliação e reabilitação neuropsicológica'},
            {'nome': 'Medicina Geral', 'descricao': 'Clínica médica geral'}
        ]
        
        especialidades_criadas = []
        for esp_data in especialidades_data:
            especialidade = Especialidade.query.filter_by(nome=esp_data['nome']).first()
            if not especialidade:
                especialidade = Especialidade(
                    nome=esp_data['nome'],
                    descricao=esp_data['descricao']
                )
                db.session.add(especialidade)
                print(f"[DEBUG] Criando especialidade: {esp_data['nome']}")
            else:
                print(f"[DEBUG] Especialidade já existe: {esp_data['nome']}")
            especialidades_criadas.append(especialidade)
        
        db.session.commit()
        print(f"[DEBUG] {len(especialidades_criadas)} especialidades processadas")
        
        # Criar funcionários de teste
        funcionarios_data = [
            {
                'nome': 'Dr. João Silva',
                'telefone': '(11) 99999-1111',
                'email': 'joao.silva@consultorio.com',
                'especialidade': 'Psicologia Clínica',
                'obs': 'Psicólogo com 10 anos de experiência'
            },
            {
                'nome': 'Dra. Maria Santos',
                'telefone': '(11) 99999-2222',
                'email': 'maria.santos@consultorio.com',
                'especialidade': 'Psicologia Infantil',
                'obs': 'Especialista em terapia infantil'
            },
            {
                'nome': 'Dr. Pedro Oliveira',
                'telefone': '(11) 99999-3333',
                'email': 'pedro.oliveira@consultorio.com',
                'especialidade': 'Terapia de Casal',
                'obs': 'Terapeuta familiar e de casal'
            },
            {
                'nome': 'Dra. Ana Costa',
                'telefone': '(11) 99999-4444',
                'email': 'ana.costa@consultorio.com',
                'especialidade': 'Neuropsicologia',
                'obs': 'Neuropsicóloga clínica'
            },
            {
                'nome': 'Dr. Carlos Ferreira',
                'telefone': '(11) 99999-5555',
                'email': 'carlos.ferreira@consultorio.com',
                'especialidade': 'Medicina Geral',
                'obs': 'Médico clínico geral'
            }
        ]
        
        funcionarios_criados = 0
        for func_data in funcionarios_data:
            # Verificar se já existe funcionário com esse email
            funcionario_existente = Funcionario.query.filter_by(email=func_data['email']).first()
            if funcionario_existente:
                print(f"[DEBUG] Funcionário já existe: {func_data['nome']} ({func_data['email']})")
                continue
            
            # Buscar especialidade
            especialidade = Especialidade.query.filter_by(nome=func_data['especialidade']).first()
            if not especialidade:
                print(f"[WARNING] Especialidade não encontrada: {func_data['especialidade']}")
                continue
            
            # Criar funcionário
            funcionario = Funcionario(
                nome=func_data['nome'],
                telefone=func_data['telefone'],
                email=func_data['email'],
                especialidade_id=especialidade.id,
                obs=func_data['obs']
            )
            
            db.session.add(funcionario)
            funcionarios_criados += 1
            print(f"[DEBUG] Criando funcionário: {func_data['nome']} - {func_data['especialidade']}")
        
        db.session.commit()
        print(f"[SUCCESS] {funcionarios_criados} funcionários criados com sucesso!")
        
        # Verificar resultado final
        total_funcionarios = Funcionario.query.count()
        print(f"[INFO] Total de funcionários no banco: {total_funcionarios}")
        
        # Listar funcionários criados
        funcionarios = Funcionario.query.all()
        print("\n[INFO] Funcionários no banco de dados:")
        for func in funcionarios:
            especialidade_nome = func.especialidade.nome if func.especialidade else 'Sem especialidade'
            print(f"  ID: {func.id}, Nome: '{func.nome}', Especialidade: '{especialidade_nome}'")
        
except Exception as e:
    print(f"[ERROR] Erro ao popular banco de dados: {e}")
    import traceback
    print(f"[ERROR] Traceback: {traceback.format_exc()}")