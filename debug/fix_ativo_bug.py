#!/usr/bin/env python3
"""
Script para corrigir o problema 'ativo' no campo created_at das especialidades
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.usuario import db
from src.models.especialidade import Especialidade
from src.main import app
from datetime import datetime
from sqlalchemy import text

def fix_ativo_bug():
    """Corrige registros com 'ativo' no campo created_at"""
    with app.app_context():
        print("🔧 CORREÇÃO DO BUG 'ATIVO' EM ESPECIALIDADES")
        print("=" * 50)
        
        try:
            # Verificar registros problemáticos usando SQL direto
            print("\n1. Verificando registros problemáticos...")
            
            # Para SQLite, verificar registros onde created_at não é uma data válida
            result = db.session.execute(text(
                "SELECT id, nome, created_at FROM especialidades WHERE created_at = 'ativo' OR created_at = 'ATIVO'"
            ))
            
            problematic_records = result.fetchall()
            
            if not problematic_records:
                print("   ✅ Nenhum registro problemático encontrado")
                return
            
            print(f"   ⚠️  Encontrados {len(problematic_records)} registros problemáticos:")
            for record in problematic_records:
                print(f"     ID: {record[0]}, Nome: {record[1]}, created_at: {record[2]}")
            
            # Corrigir os registros problemáticos
            print("\n2. Corrigindo registros...")
            
            current_time = datetime.utcnow()
            
            for record in problematic_records:
                record_id = record[0]
                record_name = record[1]
                
                # Atualizar o registro com a data atual
                db.session.execute(text(
                    "UPDATE especialidades SET created_at = :new_date, updated_at = :new_date WHERE id = :id"
                ), {
                    'new_date': current_time.isoformat(),
                    'id': record_id
                })
                
                print(f"   ✅ Corrigido ID {record_id} ({record_name}) - nova data: {current_time.isoformat()}")
            
            db.session.commit()
            print(f"\n✅ {len(problematic_records)} registros corrigidos com sucesso!")
            
            # Verificar se a correção funcionou
            print("\n3. Verificando correção...")
            
            try:
                especialidades = Especialidade.query.all()
                print(f"   ✅ Conseguiu carregar {len(especialidades)} especialidades")
                
                for esp in especialidades:
                    result = esp.to_dict()
                    print(f"   ID {esp.id}: {esp.nome} - created_at: {result['created_at']}")
                    
            except Exception as e:
                print(f"   ❌ Ainda há problemas: {e}")
                
        except Exception as e:
            print(f"❌ Erro durante a correção: {e}")
            db.session.rollback()
            
            # Tentar uma abordagem alternativa
            print("\n4. Tentando abordagem alternativa...")
            try:
                # Deletar registros problemáticos se não conseguir corrigir
                db.session.execute(text(
                    "DELETE FROM especialidades WHERE created_at = 'ativo' OR created_at = 'ATIVO'"
                ))
                db.session.commit()
                print("   ✅ Registros problemáticos removidos")
                
            except Exception as e2:
                print(f"   ❌ Erro na abordagem alternativa: {e2}")
                db.session.rollback()

def check_database_integrity():
    """Verifica a integridade do banco após a correção"""
    with app.app_context():
        print("\n🔍 VERIFICAÇÃO DE INTEGRIDADE")
        print("=" * 30)
        
        try:
            # Testar se consegue carregar todas as especialidades
            especialidades = Especialidade.query.all()
            print(f"✅ Carregadas {len(especialidades)} especialidades com sucesso")
            
            # Testar serialização
            for esp in especialidades:
                result = esp.to_dict()
                if 'created_at' in result and result['created_at']:
                    # Verificar se é uma data válida
                    try:
                        datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))
                        print(f"✅ ID {esp.id}: Data válida")
                    except:
                        print(f"❌ ID {esp.id}: Data inválida - {result['created_at']}")
                        
        except Exception as e:
            print(f"❌ Erro na verificação: {e}")

if __name__ == '__main__':
    fix_ativo_bug()
    check_database_integrity()
    
    print("\n" + "=" * 50)
    print("🎯 PRÓXIMOS PASSOS PARA PRODUÇÃO:")
    print("1. Execute este script no ambiente de produção")
    print("2. Verifique se o problema foi resolvido")
    print("3. Monitore logs para evitar recorrência")
    print("4. Considere adicionar validação no modelo para prevenir")