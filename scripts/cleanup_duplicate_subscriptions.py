from src.models.user import User, db
from src.models.subscription import Subscription
from src.main import app
from datetime import datetime

with app.app_context():
    # Buscar o usuário
    user = User.query.filter_by(email='r@teste.com').first()
    
    if user:
        print(f'=== LIMPEZA DE ASSINATURAS DUPLICADAS ===\n')
        print(f'Usuário: {user.email} (ID: {user.id})')
        
        # Buscar todas as assinaturas ativas
        active_subscriptions = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.created_at.desc()).all()
        
        print(f'\nAssinaturas ativas encontradas: {len(active_subscriptions)}')
        
        if len(active_subscriptions) > 1:
            # Manter apenas a mais recente (primeira da lista ordenada)
            most_recent = active_subscriptions[0]
            to_cancel = active_subscriptions[1:]
            
            print(f'\nMantendo assinatura mais recente:')
            print(f'  - ID: {most_recent.id}')
            print(f'  - Plano: {most_recent.plan_type}')
            print(f'  - Criada em: {most_recent.created_at}')
            print(f'  - Termina em: {most_recent.end_date}')
            
            print(f'\nCancelando {len(to_cancel)} assinaturas antigas:')
            for sub in to_cancel:
                print(f'  - Cancelando ID {sub.id} ({sub.plan_type}, criada em {sub.created_at})')
                sub.cancel()
            
            # Salvar mudanças
            db.session.commit()
            print(f'\n✅ Limpeza concluída! {len(to_cancel)} assinaturas canceladas.')
            
        elif len(active_subscriptions) == 1:
            print(f'\n✅ Apenas uma assinatura ativa encontrada. Nenhuma limpeza necessária.')
            sub = active_subscriptions[0]
            print(f'  - ID: {sub.id}')
            print(f'  - Plano: {sub.plan_type}')
            print(f'  - Criada em: {sub.created_at}')
            print(f'  - Termina em: {sub.end_date}')
        else:
            print(f'\n❌ Nenhuma assinatura ativa encontrada.')
        
        # Verificar resultado final
        print(f'\n=== VERIFICAÇÃO FINAL ===')
        final_active = Subscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).filter(
            Subscription.end_date > datetime.utcnow()
        ).count()
        
        print(f'Assinaturas ativas restantes: {final_active}')
        print(f'has_active_subscription(): {user.has_active_subscription()}')
        
    else:
        print('❌ Usuário não encontrado')