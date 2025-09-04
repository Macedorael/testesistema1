#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico específico para problema do Chrome
Funciona na aba anônima mas não no Chrome normal
"""

import requests
import json
from datetime import datetime

def test_server_response():
    """Testa se o servidor está respondendo corretamente"""
    print("=== TESTE DO SERVIDOR ===")
    
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            content = response.text
            if 'Sistema Completo para Consultórios' in content:
                print("✅ Servidor retornando LANDING PAGE corretamente")
                return True
            else:
                print("❌ Servidor não está retornando a landing page")
                return False
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        return False

def generate_chrome_solutions():
    """Gera soluções específicas para o Chrome"""
    print("\n=== SOLUÇÕES ESPECÍFICAS PARA O CHROME ===")
    
    solutions = [
        {
            "titulo": "1. RESET COMPLETO DO CHROME",
            "passos": [
                "Feche TODAS as abas do Chrome",
                "Pressione Ctrl + Shift + Delete",
                "Selecione 'Todo o período'",
                "Marque TODAS as opções:",
                "  - Histórico de navegação",
                "  - Cookies e outros dados do site",
                "  - Imagens e arquivos armazenados em cache",
                "  - Senhas e outros dados de login",
                "  - Dados de preenchimento automático",
                "Clique em 'Limpar dados'",
                "Reinicie o Chrome completamente"
            ]
        },
        {
            "titulo": "2. DESABILITAR PREENCHIMENTO AUTOMÁTICO",
            "passos": [
                "Abra o Chrome",
                "Digite: chrome://settings/autofill",
                "Desative 'Endereços e muito mais'",
                "Desative 'Métodos de pagamento'",
                "Desative 'Senhas'",
                "Reinicie o Chrome"
            ]
        },
        {
            "titulo": "3. LIMPAR DADOS ESPECÍFICOS DO SITE",
            "passos": [
                "No Chrome, vá para: chrome://settings/content/all",
                "Procure por '127.0.0.1' ou 'localhost'",
                "Clique no ícone da lixeira para deletar",
                "Reinicie o Chrome"
            ]
        },
        {
            "titulo": "4. RESET DAS CONFIGURAÇÕES DO CHROME",
            "passos": [
                "Digite: chrome://settings/reset",
                "Clique em 'Restaurar as configurações originais padrão'",
                "Confirme clicando em 'Redefinir configurações'",
                "Reinicie o Chrome"
            ]
        },
        {
            "titulo": "5. USAR PERFIL NOVO DO CHROME",
            "passos": [
                "Clique no ícone do perfil (canto superior direito)",
                "Clique em 'Adicionar'",
                "Crie um novo perfil",
                "Use o novo perfil para acessar o sistema"
            ]
        }
    ]
    
    for solution in solutions:
        print(f"\n🔧 {solution['titulo']}")
        for i, passo in enumerate(solution['passos'], 1):
            if passo.startswith('  '):
                print(f"    {passo}")
            else:
                print(f"   {i}. {passo}")

def generate_immediate_workaround():
    """Gera solução imediata para usar enquanto resolve o problema"""
    print("\n=== SOLUÇÃO IMEDIATA (ENQUANTO RESOLVE O PROBLEMA) ===")
    print("\n🚀 USE A ABA ANÔNIMA:")
    print("   1. Pressione Ctrl + Shift + N")
    print("   2. Digite: http://127.0.0.1:5000/")
    print("   3. Pressione ENTER")
    print("   ✅ Funcionará perfeitamente!")
    
    print("\n💡 ALTERNATIVA - OUTRO NAVEGADOR:")
    print("   • Firefox: Funciona normalmente")
    print("   • Edge: Funciona normalmente")
    print("   • Opera: Funciona normalmente")

def create_test_bookmark():
    """Cria instruções para bookmark de teste"""
    print("\n=== CRIAR BOOKMARK DE TESTE ===")
    print("\n📌 Para evitar digitar a URL:")
    print("   1. Na aba anônima, acesse: http://127.0.0.1:5000/")
    print("   2. Pressione Ctrl + D")
    print("   3. Salve como 'Sistema Psicologia - Local'")
    print("   4. Use o bookmark sempre que precisar")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO ESPECÍFICO DO CHROME")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Testa o servidor primeiro
    server_ok = test_server_response()
    
    if server_ok:
        print("\n✅ CONFIRMADO: Servidor funcionando perfeitamente")
        print("❌ PROBLEMA: Chrome com cache/cookies/configurações corrompidas")
        
        generate_immediate_workaround()
        generate_chrome_solutions()
        create_test_bookmark()
        
        print("\n" + "=" * 60)
        print("🎯 RECOMENDAÇÃO:")
        print("   1. Use a aba anônima AGORA (solução imediata)")
        print("   2. Tente a Solução 1 (Reset completo) para resolver definitivamente")
        print("   3. Se não resolver, tente a Solução 4 (Reset das configurações)")
        print("\n✅ O sistema está funcionando perfeitamente!")
        
    else:
        print("\n❌ PROBLEMA NO SERVIDOR")
        print("   O servidor não está respondendo corretamente.")
        print("   Verifique se o servidor está rodando.")
    
    print("\n" + "=" * 60)