#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def fix_user_isolation():
    """Redistribui registros entre usuários para corrigir isolamento"""
    
    db_path = os.path.join('src', 'database', 'app.db')
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== CORREÇÃO DE ISOLAMENTO DE USUÁRIOS ===")
    
    # Verificar usuários disponíveis
    cursor.execute('SELECT id, email FROM users ORDER BY id')
    usuarios = cursor.fetchall()
    
    print(f"\n👤 Usuários disponíveis: {len(usuarios)}")
    for user in usuarios:
        print(f"   ID {user[0]}: {user[1]}")
    
    if len(usuarios) < 2:
        print("\n❌ Precisa de pelo menos 2 usuários para redistribuir")
        return
    
    # Verificar estado atual
    cursor.execute('SELECT id, nome, user_id FROM especialidades')
    especialidades = cursor.fetchall()
    
    cursor.execute('SELECT id, nome, email, user_id FROM funcionarios')
    funcionarios = cursor.fetchall()
    
    print(f"\n📊 Estado atual:")
    print(f"   Especialidades: {len(especialidades)}")
    print(f"   Funcionários: {len(funcionarios)}")
    
    # Mostrar distribuição atual
    esp_por_user = {}
    func_por_user = {}
    
    for esp in especialidades:
        user_id = esp[2]
        esp_por_user[user_id] = esp_por_user.get(user_id, 0) + 1
    
    for func in funcionarios:
        user_id = func[3]
        func_por_user[user_id] = func_por_user.get(user_id, 0) + 1
    
    print(f"\n📈 Distribuição atual:")
    for user_id, email in usuarios:
        esp_count = esp_por_user.get(user_id, 0)
        func_count = func_por_user.get(user_id, 0)
        print(f"   Usuário {user_id} ({email}): {esp_count} especialidades, {func_count} funcionários")
    
    # Redistribuir registros
    print(f"\n🔄 Redistribuindo registros...")
    
    # Manter alguns registros para o usuário 1 (teste@email.com)
    # Mover alguns para o usuário 4 (teste2@email.com)
    
    user1_id = 1  # teste@email.com
    user4_id = 4  # teste2@email.com
    
    # Redistribuir especialidades - manter 3 para user1, mover resto para user4
    if len(especialidades) > 3:
        especialidades_para_mover = especialidades[3:]  # Mover especialidades ID 4 em diante
        
        for esp in especialidades_para_mover:
            esp_id = esp[0]
            cursor.execute('UPDATE especialidades SET user_id = ? WHERE id = ?', (user4_id, esp_id))
            print(f"   ✓ Especialidade '{esp[1]}' (ID {esp_id}) movida para usuário {user4_id}")
    
    # Redistribuir funcionários - manter 3 para user1, mover resto para user4
    if len(funcionarios) > 3:
        funcionarios_para_mover = funcionarios[3:]  # Mover funcionários ID 4 em diante
        
        for func in funcionarios_para_mover:
            func_id = func[0]
            cursor.execute('UPDATE funcionarios SET user_id = ? WHERE id = ?', (user4_id, func_id))
            print(f"   ✓ Funcionário '{func[1]}' (ID {func_id}) movido para usuário {user4_id}")
    
    # Confirmar mudanças
    conn.commit()
    
    # Verificar nova distribuição
    print(f"\n📊 Nova distribuição:")
    
    cursor.execute('SELECT user_id, COUNT(*) FROM especialidades GROUP BY user_id')
    esp_dist = cursor.fetchall()
    
    cursor.execute('SELECT user_id, COUNT(*) FROM funcionarios GROUP BY user_id')
    func_dist = cursor.fetchall()
    
    for user_id, email in usuarios:
        esp_count = next((count for uid, count in esp_dist if uid == user_id), 0)
        func_count = next((count for uid, count in func_dist if uid == user_id), 0)
        print(f"   Usuário {user_id} ({email}): {esp_count} especialidades, {func_count} funcionários")
    
    conn.close()
    
    print(f"\n✅ Redistribuição concluída!")
    print(f"\n💡 Agora teste o isolamento:")
    print(f"   - Login com teste@email.com (ID 1) - deve ver menos registros")
    print(f"   - Login com teste2@email.com (ID 4) - deve ver os registros movidos")

if __name__ == '__main__':
    fix_user_isolation()