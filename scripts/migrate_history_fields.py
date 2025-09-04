#!/usr/bin/env python3
"""
Script para migrar o banco de dados e adicionar os novos campos
previous_plan_type e previous_price à tabela subscription_history
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
import sqlite3

def migrate_subscription_history():
    """Adiciona as novas colunas à tabela subscription_history"""
    db_path = os.path.join('src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(subscription_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Adicionar previous_plan_type se não existir
        if 'previous_plan_type' not in columns:
            print("Adicionando coluna previous_plan_type...")
            cursor.execute(
                "ALTER TABLE subscription_history ADD COLUMN previous_plan_type VARCHAR(20)"
            )
            print("✓ Coluna previous_plan_type adicionada")
        else:
            print("✓ Coluna previous_plan_type já existe")
        
        # Adicionar previous_price se não existir
        if 'previous_price' not in columns:
            print("Adicionando coluna previous_price...")
            cursor.execute(
                "ALTER TABLE subscription_history ADD COLUMN previous_price FLOAT"
            )
            print("✓ Coluna previous_price adicionada")
        else:
            print("✓ Coluna previous_price já existe")
        
        conn.commit()
        conn.close()
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        if 'conn' in locals():
            conn.close()
        return False
    
    return True

if __name__ == '__main__':
    print("🔄 Iniciando migração do histórico de assinaturas...")
    print("Adicionando campos para rastrear planos anteriores em renovações\n")
    
    success = migrate_subscription_history()
    
    if success:
        print("\n🎉 Migração concluída! Agora o histórico mostrará:")
        print("   • Plano anterior nas renovações")
        print("   • Preço anterior nas renovações")
        print("   • Comparação visual entre planos antigo e novo")
    else:
        print("\n💥 Falha na migração. Verifique os erros acima.")
        sys.exit(1)