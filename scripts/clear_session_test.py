#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys

def test_clear_session():
    """Testa o acesso após limpar completamente a sessão"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== TESTE DE LIMPEZA DE SESSÃO ===")
    print(f"Testando: {base_url}")
    print()
    
    # Criar uma nova sessão completamente limpa
    session = requests.Session()
    
    try:
        # 1. Fazer logout para garantir que não há sessão
        print("1. Fazendo logout para limpar qualquer sessão...")
        logout_response = session.post(f"{base_url}/api/logout")
        print(f"   Status logout: {logout_response.status_code}")
        
        # 2. Limpar todos os cookies
        print("2. Limpando todos os cookies...")
        session.cookies.clear()
        
        # 3. Testar acesso à página principal
        print("3. Testando acesso à página principal...")
        response = session.get(f"{base_url}/", allow_redirects=False)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"   Redirecionamento para: {response.headers.get('Location')}")
            return False
        
        # Verificar o conteúdo da resposta
        content = response.text
        print(f"   Tamanho do conteúdo: {len(content)} bytes")
        
        # Verificar se é a landing page
        if "Sistema Completo para Consultórios" in content:
            print("   ✅ LANDING PAGE detectada!")
            return True
        elif "Login" in content and "email" in content.lower():
            print("   ❌ PÁGINA DE LOGIN detectada!")
            return False
        elif "Escolha seu Plano" in content:
            print("   ❌ PÁGINA DE ASSINATURA detectada!")
            return False
        else:
            print("   ❓ Página não identificada")
            print(f"   Primeiros 200 caracteres: {content[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("   Verifique se o servidor está rodando em http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")
        return False

def test_session_status():
    """Verifica o status da sessão atual"""
    base_url = "http://127.0.0.1:5000"
    
    print("\n=== VERIFICAÇÃO DE STATUS DA SESSÃO ===")
    
    session = requests.Session()
    
    try:
        # Testar endpoint /api/me para ver se há sessão ativa
        response = session.get(f"{base_url}/api/me")
        print(f"Status /api/me: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Usuário logado: {data}")
            return True
        else:
            print("Nenhum usuário logado")
            return False
            
    except Exception as e:
        print(f"Erro ao verificar sessão: {e}")
        return False

if __name__ == "__main__":
    print("DIAGNÓSTICO: Problema de redirecionamento para tela inicial\n")
    
    # Verificar se há sessão ativa
    has_session = test_session_status()
    
    # Testar com sessão limpa
    success = test_clear_session()
    
    print("\n=== RESUMO ===")
    if has_session:
        print("⚠️  Há uma sessão ativa detectada")
    else:
        print("✅ Nenhuma sessão ativa detectada")
        
    if success:
        print("✅ Landing page está funcionando corretamente")
        print("\n💡 SOLUÇÃO: O problema está no cache/cookies do navegador")
        print("   - Pressione Ctrl+Shift+R para recarregar forçado")
        print("   - Use modo incógnito")
        print("   - Limpe os cookies do site")
    else:
        print("❌ Problema detectado no servidor")
        print("\n🔧 INVESTIGAÇÃO NECESSÁRIA:")
        print("   - Verificar logs do servidor")
        print("   - Verificar configuração de sessão")
        print("   - Verificar banco de dados")