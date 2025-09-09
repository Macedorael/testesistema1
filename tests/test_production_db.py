#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar conexão e dados no banco PostgreSQL de produção
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.production')

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

try:
    import psycopg2
    from urllib.parse import urlparse
    
    # Obter URL do banco de dados
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL não encontrada no .env.production")
        sys.exit(1)
    
    print(f"[DEBUG] Conectando ao banco: {database_url[:50]}...")
    
    # Parse da URL
    parsed = urlparse(database_url)
    
    # Conectar ao banco
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],  # Remove a barra inicial
        user=parsed.username,
        password=parsed.password
    )
    
    print("[DEBUG] Conexão estabelecida com sucesso!")
    
    cursor = conn.cursor()
    
    # Verificar se a tabela funcionarios existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'funcionarios'
        );
    """)
    
    table_exists = cursor.fetchone()[0]
    print(f"[DEBUG] Tabela 'funcionarios' existe: {table_exists}")
    
    if table_exists:
        # Contar funcionários
        cursor.execute("SELECT COUNT(*) FROM funcionarios;")
        count = cursor.fetchone()[0]
        print(f"[DEBUG] Total de funcionários: {count}")
        
        if count > 0:
            # Buscar alguns funcionários
            cursor.execute("""
                SELECT f.id, f.nome, e.nome as especialidade_nome
                FROM funcionarios f
                LEFT JOIN especialidades e ON f.especialidade_id = e.id
                LIMIT 10;
            """)
            
            funcionarios = cursor.fetchall()
            print(f"[DEBUG] Funcionários encontrados:")
            for func in funcionarios:
                print(f"  ID: {func[0]}, Nome: '{func[1]}', Especialidade: '{func[2] or 'Sem especialidade'}'")
        else:
            print("[INFO] Nenhum funcionário encontrado no banco")
    
    # Verificar se a tabela especialidades existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'especialidades'
        );
    """)
    
    esp_table_exists = cursor.fetchone()[0]
    print(f"[DEBUG] Tabela 'especialidades' existe: {esp_table_exists}")
    
    if esp_table_exists:
        cursor.execute("SELECT COUNT(*) FROM especialidades;")
        esp_count = cursor.fetchone()[0]
        print(f"[DEBUG] Total de especialidades: {esp_count}")
        
        if esp_count > 0:
            cursor.execute("SELECT id, nome FROM especialidades LIMIT 5;")
            especialidades = cursor.fetchall()
            print(f"[DEBUG] Especialidades encontradas:")
            for esp in especialidades:
                print(f"  ID: {esp[0]}, Nome: '{esp[1]}'")
    
    cursor.close()
    conn.close()
    print("[DEBUG] Conexão fechada")
    
except ImportError:
    print("[ERROR] psycopg2 não está instalado. Instale com: pip install psycopg2-binary")
except Exception as e:
    print(f"[ERROR] Erro ao conectar ao banco: {e}")
    import traceback
    print(f"[ERROR] Traceback: {traceback.format_exc()}")