from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.paciente import Patient
from src.models.diario import DiaryEntry
from datetime import datetime
import logging
import json

# Logger específico
logger = logging.getLogger('diarios')
logger.setLevel(logging.DEBUG)

diaries_bp = Blueprint('diaries', __name__)

# ---------------------- PACIENTE LOGADO (role=patient) ----------------------
@diaries_bp.route('/patients/me/diary-entries', methods=['GET'])
@login_required
def get_my_diary_entries():
    """Lista registros diários do paciente autenticado (role=patient)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 401
        if current_user.role != 'patient':
            return jsonify({'success': False, 'message': 'Acesso não autorizado'}), 403

        patient = Patient.query.filter_by(email=current_user.email).first()
        if not patient:
            return jsonify({'success': False, 'message': 'Paciente não encontrado'}), 404

        entries = DiaryEntry.query.filter_by(patient_id=patient.id).order_by(DiaryEntry.data_registro.desc()).all()
        return jsonify({'success': True, 'data': [e.to_dict() for e in entries]})
    except Exception as e:
        logger.error(f"[GET /patients/me/diary-entries] Erro: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Erro ao buscar registros: {str(e)}'}), 500


@diaries_bp.route('/patients/me/diary-entries', methods=['POST'])
@login_required
def create_my_diary_entry():
    """Cria um novo registro diário pelo paciente autenticado (role=patient)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 401
        if current_user.role != 'patient':
            return jsonify({'success': False, 'message': 'Acesso não autorizado'}), 403

        patient = Patient.query.filter_by(email=current_user.email).first()
        if not patient:
            return jsonify({'success': False, 'message': 'Paciente não encontrado'}), 404

        data = request.get_json() or {}
        # Campos base obrigatórios
        base_required = ['situacao', 'pensamento', 'comportamento', 'consequencia']
        for field in base_required:
            if data.get(field) in (None, ''):
                return jsonify({'success': False, 'message': f'Campo obrigatório: {field}'}), 400

        # Normalizar entradas de emoções+intensidades (lista) ou legado (único)
        pairs = []
        if isinstance(data.get('emocao_intensidades'), list) and len(data['emocao_intensidades']) > 0:
            for idx, item in enumerate(data['emocao_intensidades']):
                if not isinstance(item, dict):
                    return jsonify({'success': False, 'message': f'emocao_intensidades[{idx}] deve ser um objeto'}), 400
                emocao_val = item.get('emocao')
                intensidade_val = item.get('intensidade')
                if emocao_val in (None, ''):
                    return jsonify({'success': False, 'message': f'Campo obrigatório: emocao em emocao_intensidades[{idx}]'}), 400
                try:
                    intensidade_int = int(intensidade_val)
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'message': f'Intensidade inválida em emocao_intensidades[{idx}]'}), 400
                if intensidade_int < 0 or intensidade_int > 100:
                    return jsonify({'success': False, 'message': f'Intensidade deve estar entre 0 e 100 em emocao_intensidades[{idx}]'}), 400
                pairs.append({'emocao': emocao_val, 'intensidade': intensidade_int})
        else:
            # Fallback: campos únicos legado
            if data.get('emocao') in (None, '') or data.get('intensidade') in (None, ''):
                return jsonify({'success': False, 'message': 'Informe pelo menos uma emoção e intensidade'}), 400
            try:
                intensidade_int = int(data['intensidade'])
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Intensidade deve ser um número inteiro'}), 400
            if intensidade_int < 0 or intensidade_int > 100:
                return jsonify({'success': False, 'message': 'Intensidade deve estar entre 0 e 100'}), 400
            pairs.append({'emocao': data['emocao'], 'intensidade': intensidade_int})

        # data_registro opcional (ISO8601)
        data_registro = datetime.utcnow()
        if data.get('data_registro'):
            try:
                data_registro = datetime.fromisoformat(data['data_registro'])
            except Exception:
                return jsonify({'success': False, 'message': 'data_registro inválida. Use ISO 8601'}), 400

        first_emocao = pairs[0]['emocao']
        first_intensidade = pairs[0]['intensidade']

        entry = DiaryEntry(
            user_id=patient.user_id,
            patient_id=patient.id,
            situacao=data['situacao'],
            pensamento=data['pensamento'],
            emocao=first_emocao,
            intensidade=first_intensidade,
            emocao_intensidades=json.dumps(pairs),
            comportamento=data['comportamento'],
            consequencia=data['consequencia'],
            data_registro=data_registro
        )
        db.session.add(entry)
        db.session.commit()

        return jsonify({'success': True, 'data': entry.to_dict()}), 201
    except Exception as e:
        logger.error(f"[POST /patients/me/diary-entries] Erro: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar registro: {str(e)}'}), 500


# ---------------------- PROFISSIONAL LOGADO ----------------------
@diaries_bp.route('/patients/<int:patient_id>/diary-entries', methods=['GET'])
@login_and_subscription_required
def get_patient_diary_entries(patient_id):
    """Lista registros diários de um paciente (profissional autenticado)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 401

        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({'success': False, 'message': 'Paciente não encontrado ou não autorizado'}), 404

        entries = DiaryEntry.query.filter_by(patient_id=patient_id, user_id=current_user.id).order_by(DiaryEntry.data_registro.desc()).all()
        return jsonify({'success': True, 'data': [e.to_dict() for e in entries]})
    except Exception as e:
        logger.error(f"[GET /patients/{patient_id}/diary-entries] Erro: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Erro ao buscar registros: {str(e)}'}), 500


@diaries_bp.route('/patients/<int:patient_id>/diary-entries', methods=['POST'])
@login_and_subscription_required
def create_patient_diary_entry(patient_id):
    """Cria um novo registro diário para um paciente (profissional autenticado)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 401

        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({'success': False, 'message': 'Paciente não encontrado ou não autorizado'}), 404

        data = request.get_json() or {}
        # Campos base obrigatórios
        base_required = ['situacao', 'pensamento', 'comportamento', 'consequencia']
        for field in base_required:
            if data.get(field) in (None, ''):
                return jsonify({'success': False, 'message': f'Campo obrigatório: {field}'}), 400

        # Normalizar entradas de emoções+intensidades (lista) ou legado (único)
        pairs = []
        if isinstance(data.get('emocao_intensidades'), list) and len(data['emocao_intensidades']) > 0:
            for idx, item in enumerate(data['emocao_intensidades']):
                if not isinstance(item, dict):
                    return jsonify({'success': False, 'message': f'emocao_intensidades[{idx}] deve ser um objeto'}), 400
                emocao_val = item.get('emocao')
                intensidade_val = item.get('intensidade')
                if emocao_val in (None, ''):
                    return jsonify({'success': False, 'message': f'Campo obrigatório: emocao em emocao_intensidades[{idx}]'}), 400
                try:
                    intensidade_int = int(intensidade_val)
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'message': f'Intensidade inválida em emocao_intensidades[{idx}]'}), 400
                if intensidade_int < 0 or intensidade_int > 100:
                    return jsonify({'success': False, 'message': f'Intensidade deve estar entre 0 e 100 em emocao_intensidades[{idx}]'}), 400
                pairs.append({'emocao': emocao_val, 'intensidade': intensidade_int})
        else:
            # Fallback: campos únicos legado
            if data.get('emocao') in (None, '') or data.get('intensidade') in (None, ''):
                return jsonify({'success': False, 'message': 'Informe pelo menos uma emoção e intensidade'}), 400
            try:
                intensidade_int = int(data['intensidade'])
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Intensidade deve ser um número inteiro'}), 400
            if intensidade_int < 0 or intensidade_int > 100:
                return jsonify({'success': False, 'message': 'Intensidade deve estar entre 0 e 100'}), 400
            pairs.append({'emocao': data['emocao'], 'intensidade': intensidade_int})

        data_registro = datetime.utcnow()
        if data.get('data_registro'):
            try:
                data_registro = datetime.fromisoformat(data['data_registro'])
            except Exception:
                return jsonify({'success': False, 'message': 'data_registro inválida. Use ISO 8601'}), 400

        first_emocao = pairs[0]['emocao']
        first_intensidade = pairs[0]['intensidade']

        entry = DiaryEntry(
            user_id=current_user.id,
            patient_id=patient.id,
            situacao=data['situacao'],
            pensamento=data['pensamento'],
            emocao=first_emocao,
            intensidade=first_intensidade,
            emocao_intensidades=json.dumps(pairs),
            comportamento=data['comportamento'],
            consequencia=data['consequencia'],
            data_registro=data_registro
        )
        db.session.add(entry)
        db.session.commit()

        return jsonify({'success': True, 'data': entry.to_dict()}), 201
    except Exception as e:
        logger.error(f"[POST /patients/{patient_id}/diary-entries] Erro: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar registro: {str(e)}'}), 500