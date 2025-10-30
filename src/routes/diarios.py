from src.utils.auth import login_required, login_and_subscription_required, get_current_user
from flask import Blueprint, request, jsonify
from src.models.usuario import db
from src.models.paciente import Patient
from src.models.diario import DiaryEntry
from datetime import datetime, date
from sqlalchemy import func, and_
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
        # Gate: Diário TCC desativado
        if not bool(getattr(patient, 'diario_tcc_ativo', False)):
            return jsonify({'success': False, 'message': 'Diário TCC desativado para este paciente'}), 403

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
        # Gate: Diário TCC desativado
        if not bool(getattr(patient, 'diario_tcc_ativo', False)):
            return jsonify({'success': False, 'message': 'Diário TCC desativado para este paciente'}), 403

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
                if intensidade_int < 0 or intensidade_int > 10:
                    return jsonify({'success': False, 'message': f'Intensidade deve estar entre 0 e 10 em emocao_intensidades[{idx}]'}), 400
                pairs.append({'emocao': emocao_val, 'intensidade': intensidade_int})
        else:
            # Fallback: campos únicos legado
            if data.get('emocao') in (None, '') or data.get('intensidade') in (None, ''):
                return jsonify({'success': False, 'message': 'Informe pelo menos uma emoção e intensidade'}), 400
            try:
                intensidade_int = int(data['intensidade'])
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Intensidade deve ser um número inteiro'}), 400
            if intensidade_int < 0 or intensidade_int > 10:
                return jsonify({'success': False, 'message': 'Intensidade deve estar entre 0 e 10'}), 400
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
        # Gate: Diário TCC desativado
        if not bool(getattr(patient, 'diario_tcc_ativo', False)):
            return jsonify({'success': False, 'message': 'Diário TCC desativado para este paciente'}), 403

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
        # Gate: Diário TCC desativado
        if not bool(getattr(patient, 'diario_tcc_ativo', False)):
            return jsonify({'success': False, 'message': 'Diário TCC desativado para este paciente'}), 403

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
                if intensidade_int < 0 or intensidade_int > 10:
                    return jsonify({'success': False, 'message': f'Intensidade deve estar entre 0 e 10 em emocao_intensidades[{idx}]'}), 400
                pairs.append({'emocao': emocao_val, 'intensidade': intensidade_int})
        else:
            # Fallback: campos únicos legado
            if data.get('emocao') in (None, '') or data.get('intensidade') in (None, ''):
                return jsonify({'success': False, 'message': 'Informe pelo menos uma emoção e intensidade'}), 400
            try:
                intensidade_int = int(data['intensidade'])
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Intensidade deve ser um número inteiro'}), 400
            if intensidade_int < 0 or intensidade_int > 10:
                return jsonify({'success': False, 'message': 'Intensidade deve estar entre 0 e 10'}), 400
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


# ---------------------- EMOÇÕES (semanal) ----------------------
@diaries_bp.route('/patients/<int:patient_id>/emotions/weekly', methods=['GET'])
@login_and_subscription_required
def get_patient_emotions_weekly(patient_id):
    """Retorna agregação semanal das emoções de um paciente para um ano.
    Parâmetros: year (YYYY, padrão ano atual), metric (avg|max|sum, padrão avg), period (day|week|month, padrão week)
    Segurança: isola por tenant (user_id do profissional atual)
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 401

        # Garantir que o paciente pertence ao profissional
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
        if not patient:
            return jsonify({'success': False, 'message': 'Paciente não encontrado ou não autorizado'}), 404
        # Gate: Diário TCC desativado
        if not bool(getattr(patient, 'diario_tcc_ativo', False)):
            return jsonify({'success': False, 'message': 'Diário TCC desativado para este paciente'}), 403

        # Parâmetros
        try:
            year_param = int(request.args.get('year') or date.today().year)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Parâmetro year inválido'}), 400

        metric = (request.args.get('metric') or 'avg').lower()
        if metric not in ('avg', 'max', 'sum'):
            return jsonify({'success': False, 'message': 'Parâmetro metric inválido (use avg|max|sum)'}), 400

        period = (request.args.get('period') or 'week').lower()
        if period not in ('day', 'week', 'month', 'year'):
            return jsonify({'success': False, 'message': 'Parâmetro period inválido (use day|week|month|year)'}), 400

        # Filtrar entradas pelo ano
        if period == 'year':
            # Agregar por anos no intervalo [year_param-4, year_param]
            start_date = date(year_param - 4, 1, 1)
            end_date = date(year_param, 12, 31)
        else:
            start_date = date(year_param, 1, 1)
            end_date = date(year_param, 12, 31)
        entries = DiaryEntry.query.filter(
            and_(
                DiaryEntry.patient_id == patient_id,
                DiaryEntry.user_id == current_user.id,
                func.date(DiaryEntry.data_registro) >= start_date,
                func.date(DiaryEntry.data_registro) <= end_date,
            )
        ).order_by(DiaryEntry.data_registro.asc()).all()

        # Agregar por emoção e período solicitado
        from collections import defaultdict
        by_emotion_period = defaultdict(lambda: defaultdict(list))
        labels_set = set()

        for e in entries:
            try:
                dt = e.data_registro or datetime.utcnow()
                if period == 'day':
                    label = dt.date().isoformat()  # YYYY-MM-DD
                elif period == 'month':
                    label = f"{dt.year}-{dt.month:02d}"  # YYYY-MM
                elif period == 'year':
                    label = f"{dt.year}"  # YYYY
                else:
                    iso_year, iso_week, _ = dt.isocalendar()
                    label = f"{iso_year}-{iso_week:02d}"  # YYYY-WW
                labels_set.add(label)

                pairs = []
                if e.emocao_intensidades:
                    try:
                        data_pairs = json.loads(e.emocao_intensidades)
                        if isinstance(data_pairs, list):
                            for p in data_pairs:
                                emocao_val = p.get('emocao')
                                intensidade_val = p.get('intensidade')
                                if emocao_val not in (None, ''):
                                    try:
                                        intensidade_int = int(intensidade_val)
                                    except (TypeError, ValueError):
                                        intensidade_int = None
                                    if intensidade_int is not None:
                                        # Garantir escala 0–10
                                        intensidade_int = max(0, min(10, intensidade_int))
                                        pairs.append({'emocao': emocao_val, 'intensidade': intensidade_int})
                    except Exception:
                        # Fallback para campos legado
                        pass

                if not pairs and e.emocao:
                    try:
                        intensidade_int = int(e.intensidade)
                    except (TypeError, ValueError):
                        intensidade_int = None
                    if intensidade_int is not None:
                        intensidade_int = max(0, min(10, intensidade_int))
                        pairs.append({'emocao': e.emocao, 'intensidade': intensidade_int})

                for p in pairs:
                    by_emotion_period[p['emocao']][label].append(p['intensidade'])
            except Exception:
                # Ignora registro problemático sem interromper toda agregação
                continue

        labels = sorted(list(labels_set))

        datasets = []
        for emotion, period_map in by_emotion_period.items():
            values = []
            for lbl in labels:
                intens_list = period_map.get(lbl, [])
                if not intens_list:
                    values.append(None)
                else:
                    if metric == 'avg':
                        values.append(round(sum(intens_list) / len(intens_list), 2))
                    elif metric == 'max':
                        values.append(max(intens_list))
                    else:  # sum
                        values.append(sum(intens_list))
            datasets.append({'emotion': emotion, 'values': values})

        # Para compatibilidade, devolvemos 'weeks' quando period=week e também um campo genérico 'labels'
        result = {'year': year_param, 'labels': labels, 'datasets': datasets}
        if period == 'week':
            result['weeks'] = labels
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"[GET /patients/{patient_id}/emotions/weekly] Erro: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Erro ao agregar emoções: {str(e)}'}), 500