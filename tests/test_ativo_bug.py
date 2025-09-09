#!/usr/bin/env python3
"""
Script para reproduzir e testar o problema 'ativo' no campo created_at
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.usuario import db
from src.models.especialidade import Especialidade
from src.main import app
from datetime import datetime
import json

def test_ativo_bug():
    """Testa diferentes cenários que poderiam causar o problema 'ativo'"""
    with app.app_context():
        print("🔍 TESTE DO BUG 'ATIVO' EM ESPECIALIDADES")
        print("=" * 50)
        
        # Teste 1: Criar especialidade normal
        print("\n1. Testando criação normal de especialidade...")
        esp_normal = Especialidade(
            nome="Teste Normal",
            descricao="Especialidade de teste normal"
        )
        db.session.add(esp_normal)
        db.session.commit()
        
        result_normal = esp_normal.to_dict()
        print(f"   created_at: {result_normal['created_at']}")
        print(f"   Tipo: {type(esp_normal.created_at)}")
        
        # Teste 2: Simular dados corrompidos
        print("\n2. Simulando dados corrompidos...")
        try:
            # Tentar inserir 'ativo' diretamente no campo created_at
            from sqlalchemy import text
            
            # Inserir dados corrompidos diretamente no banco
            db.session.execute(text(
                "INSERT INTO especialidades (nome, descricao, created_at) VALUES (:nome, :desc, :created)"
            ), {
                'nome': 'Teste Corrompido',
                'desc': 'Teste com dados corrompidos',
                'created': 'ativo'  # Inserindo string no campo de data
            })
            db.session.commit()
            
            print("   ✅ Dados corrompidos inseridos com sucesso")
            
        except Exception as e:
            print(f"   ❌ Erro ao inserir dados corrompidos: {e}")
            db.session.rollback()
        
        # Teste 3: Verificar todas as especialidades
        print("\n3. Verificando todas as especialidades no banco...")
        especialidades = Especialidade.query.all()
        
        for esp in especialidades:
            try:
                result = esp.to_dict()
                print(f"   ID {esp.id}: created_at = {result['created_at']} (tipo: {type(esp.created_at)})")
            except Exception as e:
                print(f"   ID {esp.id}: ERRO ao serializar - {e}")
                print(f"   Valor bruto created_at: {esp.created_at} (tipo: {type(esp.created_at)})")
        
        # Teste 4: Simular resposta da API
        print("\n4. Simulando resposta da API...")
        try:
            from src.routes.especialidades import especialidades_bp
            with app.test_client() as client:
                # Simular login
                with client.session_transaction() as sess:
                    sess['user_id'] = 1
                
                response = client.get('/api/especialidades')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   Status: {response.status_code}")
                    print(f"   Dados retornados: {json.dumps(data, indent=2, default=str)}")
                else:
                    print(f"   Erro na API: {response.status_code} - {response.data}")
        except Exception as e:
            print(f"   Erro ao testar API: {e}")
        
        # Teste 5: Verificar comportamento do JavaScript
        print("\n5. Testando formatação JavaScript...")
        test_values = ['ativo', 'ATIVO', None, '', '2025-01-09T16:43:56.708186']
        
        for value in test_values:
            print(f"   Testando valor: {repr(value)}")
            # Simular o que acontece no JavaScript
            if value:
                try:
                    from datetime import datetime
                    # Simular new Date(value) do JavaScript
                    if isinstance(value, str) and value not in ['ativo', 'ATIVO']:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        formatted = dt.strftime('%d/%m/%Y')
                        print(f"     Resultado: {formatted}")
                    else:
                        print(f"     Resultado: {value} (não é data válida)")
                except Exception as e:
                    print(f"     Erro: {e}")
            else:
                print("     Resultado: '-' (valor vazio)")
        
        # Limpeza
        print("\n6. Limpando dados de teste...")
        try:
            db.session.execute(text("DELETE FROM especialidades WHERE nome LIKE 'Teste%'"))
            db.session.commit()
            print("   ✅ Dados de teste removidos")
        except Exception as e:
            print(f"   ❌ Erro na limpeza: {e}")
            db.session.rollback()

if __name__ == '__main__':
    test_ativo_bug()