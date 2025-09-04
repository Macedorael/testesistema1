#!/usr/bin/env python3
"""
Script para corrigir user_ids nulos no banco de dados
"""

import sys
import os
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from src.models.usuario import User, db
from src.models.paciente import Patient
from src.models.consulta import Appointment, Session
from src.models.pagamento import Payment

def fix_null_user_ids():
    """Corrige user_ids nulos no banco de dados"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        print("🔧 Corrigindo user_ids nulos no banco de dados...\n")
        
        # Verificar e corrigir appointments com user_id nulo
        appointments_null = Appointment.query.filter(Appointment.user_id.is_(None)).all()
        print(f"📅 Agendamentos com user_id nulo: {len(appointments_null)}")
        
        for appointment in appointments_null:
            # Tentar encontrar o usuário através do paciente
            patient = Patient.query.get(appointment.patient_id)
            if patient and patient.user_id:
                print(f"   Corrigindo agendamento {appointment.id}: user_id {patient.user_id}")
                appointment.user_id = patient.user_id
            else:
                # Se não conseguir encontrar, atribuir ao primeiro usuário disponível
                first_user = User.query.first()
                if first_user:
                    print(f"   Corrigindo agendamento {appointment.id}: atribuindo ao usuário {first_user.id}")
                    appointment.user_id = first_user.id
                    # Também corrigir o paciente se necessário
                    if patient and not patient.user_id:
                        patient.user_id = first_user.id
        
        # Verificar e corrigir patients com user_id nulo
        patients_null = Patient.query.filter(Patient.user_id.is_(None)).all()
        print(f"👤 Pacientes com user_id nulo: {len(patients_null)}")
        
        for patient in patients_null:
            # Atribuir ao primeiro usuário disponível
            first_user = User.query.first()
            if first_user:
                print(f"   Corrigindo paciente {patient.id}: atribuindo ao usuário {first_user.id}")
                patient.user_id = first_user.id
        
        # Verificar e corrigir payments com user_id nulo
        payments_null = Payment.query.filter(Payment.user_id.is_(None)).all()
        print(f"💰 Pagamentos com user_id nulo: {len(payments_null)}")
        
        for payment in payments_null:
            # Tentar encontrar o usuário através do paciente
            patient = Patient.query.get(payment.patient_id)
            if patient and patient.user_id:
                print(f"   Corrigindo pagamento {payment.id}: user_id {patient.user_id}")
                payment.user_id = patient.user_id
            else:
                # Se não conseguir encontrar, atribuir ao primeiro usuário disponível
                first_user = User.query.first()
                if first_user:
                    print(f"   Corrigindo pagamento {payment.id}: atribuindo ao usuário {first_user.id}")
                    payment.user_id = first_user.id
        
        # Salvar todas as alterações
        try:
            db.session.commit()
            print("\n✅ Todas as correções foram salvas no banco de dados!")
            
            # Verificar se ainda há registros com user_id nulo
            appointments_null_after = Appointment.query.filter(Appointment.user_id.is_(None)).count()
            patients_null_after = Patient.query.filter(Patient.user_id.is_(None)).count()
            payments_null_after = Payment.query.filter(Payment.user_id.is_(None)).count()
            
            print(f"\n📊 Verificação pós-correção:")
            print(f"   📅 Agendamentos com user_id nulo: {appointments_null_after}")
            print(f"   👤 Pacientes com user_id nulo: {patients_null_after}")
            print(f"   💰 Pagamentos com user_id nulo: {payments_null_after}")
            
            if appointments_null_after == 0 and patients_null_after == 0 and payments_null_after == 0:
                print("\n🎉 Todos os user_ids nulos foram corrigidos com sucesso!")
                return True
            else:
                print("\n⚠️ Ainda existem registros com user_id nulo.")
                return False
                
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao salvar correções: {e}")
            return False

def main():
    """Executa a correção de user_ids nulos"""
    print("🚀 Iniciando correção de user_ids nulos...\n")
    
    try:
        success = fix_null_user_ids()
        
        if success:
            print("\n✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n🔒 Todos os registros agora possuem user_id válido.")
            print("\n📋 Próximos passos:")
            print("   1. Execute novamente o teste de isolamento")
            print("   2. Verifique se a aplicação está funcionando corretamente")
        else:
            print("\n❌ PROBLEMAS DURANTE A CORREÇÃO!")
            print("\n🔍 Verifique os logs acima para mais detalhes.")
            
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False
    
    return success

if __name__ == '__main__':
    main()