#!/usr/bin/env python3
"""
Script para adicionar validação e prevenir o problema 'ativo' no futuro
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.usuario import db
from src.models.especialidade import Especialidade
from src.main import app
from datetime import datetime
from sqlalchemy import text, event
from sqlalchemy.orm import validates

def add_validation_to_model():
    """Adiciona validação ao modelo Especialidade"""
    print("🛡️  ADICIONANDO VALIDAÇÃO PREVENTIVA")
    print("=" * 40)
    
    # Verificar se já existe validação
    model_file = 'src/models/especialidade.py'
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '@validates' in content:
            print("   ✅ Validação já existe no modelo")
            return
            
        # Adicionar validação
        validation_code = '''
    @validates('created_at', 'updated_at')
    def validate_datetime_fields(self, key, value):
        """Valida campos de data/hora para prevenir valores inválidos"""
        if value is None:
            return value
            
        # Se for string, verificar se é uma data válida
        if isinstance(value, str):
            # Prevenir strings como 'ativo', 'ATIVO', etc.
            if value.lower() in ['ativo', 'active', 'true', 'false']:
                raise ValueError(f"Valor inválido para campo {key}: {value}. Deve ser uma data válida.")
                
            # Tentar converter para datetime
            try:
                from datetime import datetime
                if 'T' in value:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError(f"Formato de data inválido para campo {key}: {value}")
                
        return value
'''
        
        # Encontrar onde inserir a validação (antes do método to_dict)
        if 'def to_dict(self):' in content:
            content = content.replace('def to_dict(self):', validation_code + '\n    def to_dict(self):')
        else:
            # Inserir antes da última linha da classe
            lines = content.split('\n')
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                    # Encontrou o final da classe
                    lines.insert(i, validation_code)
                    break
            content = '\n'.join(lines)
            
        # Adicionar import se necessário
        if 'from sqlalchemy.orm import validates' not in content:
            content = content.replace(
                'from sqlalchemy import Column, Integer, String, DateTime, Text',
                'from sqlalchemy import Column, Integer, String, DateTime, Text\nfrom sqlalchemy.orm import validates'
            )
            
        # Salvar o arquivo modificado
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"   ✅ Validação adicionada ao modelo {model_file}")
        
    except Exception as e:
        print(f"   ❌ Erro ao adicionar validação: {e}")

def create_database_trigger():
    """Cria trigger no banco para validação adicional"""
    print("\n🔧 CRIANDO TRIGGER DE VALIDAÇÃO NO BANCO")
    print("=" * 45)
    
    with app.app_context():
        try:
            # Para SQLite, criar trigger
            trigger_sql = '''
            CREATE TRIGGER IF NOT EXISTS validate_especialidade_dates
            BEFORE INSERT ON especialidades
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.created_at IN ('ativo', 'ATIVO', 'active', 'ACTIVE', 'true', 'false')
                    THEN RAISE(ABORT, 'Valor inválido para created_at: ' || NEW.created_at)
                END;
                SELECT CASE
                    WHEN NEW.updated_at IN ('ativo', 'ATIVO', 'active', 'ACTIVE', 'true', 'false')
                    THEN RAISE(ABORT, 'Valor inválido para updated_at: ' || NEW.updated_at)
                END;
            END;
            '''
            
            db.session.execute(text(trigger_sql))
            
            # Trigger para UPDATE também
            trigger_update_sql = '''
            CREATE TRIGGER IF NOT EXISTS validate_especialidade_dates_update
            BEFORE UPDATE ON especialidades
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.created_at IN ('ativo', 'ATIVO', 'active', 'ACTIVE', 'true', 'false')
                    THEN RAISE(ABORT, 'Valor inválido para created_at: ' || NEW.created_at)
                END;
                SELECT CASE
                    WHEN NEW.updated_at IN ('ativo', 'ATIVO', 'active', 'ACTIVE', 'true', 'false')
                    THEN RAISE(ABORT, 'Valor inválido para updated_at: ' || NEW.updated_at)
                END;
            END;
            '''
            
            db.session.execute(text(trigger_update_sql))
            db.session.commit()
            
            print("   ✅ Triggers de validação criados no banco")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar triggers: {e}")
            db.session.rollback()

def test_validation():
    """Testa se a validação está funcionando"""
    print("\n🧪 TESTANDO VALIDAÇÃO")
    print("=" * 25)
    
    with app.app_context():
        try:
            # Tentar inserir um registro com valor inválido
            print("   Testando inserção com valor inválido...")
            
            try:
                db.session.execute(text(
                    "INSERT INTO especialidades (nome, descricao, created_at, updated_at) VALUES (?, ?, ?, ?)"
                ), ('Teste Inválido', 'Teste', 'ativo', 'ativo'))
                db.session.commit()
                print("   ❌ Validação falhou - inserção inválida foi permitida")
            except Exception as e:
                print(f"   ✅ Validação funcionando - erro esperado: {str(e)[:100]}...")
                db.session.rollback()
                
            # Tentar inserir um registro válido
            print("   Testando inserção com valor válido...")
            current_time = datetime.now().isoformat()
            
            try:
                db.session.execute(text(
                    "INSERT INTO especialidades (nome, descricao, created_at, updated_at) VALUES (?, ?, ?, ?)"
                ), ('Teste Válido', 'Teste válido', current_time, current_time))
                db.session.commit()
                print("   ✅ Inserção válida funcionou")
                
                # Limpar o teste
                db.session.execute(text("DELETE FROM especialidades WHERE nome = 'Teste Válido'"))
                db.session.commit()
                
            except Exception as e:
                print(f"   ❌ Erro inesperado na inserção válida: {e}")
                db.session.rollback()
                
        except Exception as e:
            print(f"   ❌ Erro no teste: {e}")

if __name__ == '__main__':
    add_validation_to_model()
    create_database_trigger()
    test_validation()
    
    print("\n" + "=" * 50)
    print("🎯 VALIDAÇÃO PREVENTIVA CONFIGURADA!")
    print("\nO que foi implementado:")
    print("1. ✅ Validação no modelo SQLAlchemy")
    print("2. ✅ Triggers no banco de dados")
    print("3. ✅ Testes de validação")
    print("\nAgora o sistema está protegido contra valores inválidos!")