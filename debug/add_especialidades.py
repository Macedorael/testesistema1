#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.main import app, db
from src.models.especialidade import Especialidade
from datetime import datetime

def add_especialidades():
    app.app_context().push()
    
    # Lista de especialidades médicas comuns
    especialidades = [
        {'nome': 'Cardiologia', 'descricao': 'Especialidade médica que se dedica ao diagnóstico e tratamento das doenças do coração'},
        {'nome': 'Dermatologia', 'descricao': 'Especialidade médica voltada ao diagnóstico, prevenção e tratamento de doenças da pele'},
        {'nome': 'Endocrinologia', 'descricao': 'Especialidade que trata dos distúrbios das glândulas endócrinas e hormônios'},
        {'nome': 'Gastroenterologia', 'descricao': 'Especialidade médica que cuida do sistema digestivo e suas doenças'},
        {'nome': 'Ginecologia', 'descricao': 'Especialidade médica que trata da saúde do sistema reprodutor feminino'},
        {'nome': 'Neurologia', 'descricao': 'Especialidade médica que trata dos distúrbios do sistema nervoso'},
        {'nome': 'Oftalmologia', 'descricao': 'Especialidade médica que trata das doenças dos olhos e da visão'},
        {'nome': 'Ortopedia', 'descricao': 'Especialidade médica que cuida do sistema locomotor'},
        {'nome': 'Pediatria', 'descricao': 'Especialidade médica dedicada aos cuidados médicos de bebês, crianças e adolescentes'},
        {'nome': 'Psiquiatria', 'descricao': 'Especialidade médica que trata dos transtornos mentais e comportamentais'},
        {'nome': 'Urologia', 'descricao': 'Especialidade médica que trata do sistema urinário e reprodutor masculino'},
        {'nome': 'Pneumologia', 'descricao': 'Especialidade médica que trata das doenças do sistema respiratório'},
        {'nome': 'Reumatologia', 'descricao': 'Especialidade médica que trata das doenças do sistema músculo-esquelético'},
        {'nome': 'Oncologia', 'descricao': 'Especialidade médica que trata do câncer e tumores'},
        {'nome': 'Anestesiologia', 'descricao': 'Especialidade médica responsável pela anestesia e cuidados perioperatórios'}
    ]
    
    # Verificar quais já existem
    existentes = [e.nome for e in Especialidade.query.all()]
    print(f'Especialidades existentes: {len(existentes)} - {existentes}')
    
    # Adicionar apenas as que não existem
    adicionadas = 0
    for esp_data in especialidades:
        if esp_data['nome'] not in existentes:
            nova_esp = Especialidade(
                nome=esp_data['nome'],
                descricao=esp_data['descricao'],
                created_at=datetime.now(),
                ativo=True
            )
            db.session.add(nova_esp)
            adicionadas += 1
            print(f'✅ Adicionada: {esp_data["nome"]}')
        else:
            print(f'📋 Já existe: {esp_data["nome"]}')
    
    if adicionadas > 0:
        try:
            db.session.commit()
            print(f'\n🎉 {adicionadas} especialidades adicionadas com sucesso!')
        except Exception as e:
            db.session.rollback()
            print(f'❌ Erro ao salvar: {e}')
    else:
        print('\n📋 Nenhuma especialidade nova foi adicionada.')
    
    print(f'\n📊 Total de especialidades no banco: {Especialidade.query.count()}')

if __name__ == '__main__':
    add_especialidades()