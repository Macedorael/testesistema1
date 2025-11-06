from flask import jsonify

def validate_required(data: dict, required_fields: dict):
    """Valida campos obrigatórios.
    required_fields: dict {campo: rótulo}
    Retorna lista de dicts com field, label e message.
    """
    missing = []
    for field, label in required_fields.items():
        value = data.get(field)
        is_empty_list = isinstance(value, list) and len(value) == 0
        if value in (None, '') or is_empty_list:
            missing.append({
                'field': field,
                'label': label,
                'message': f'{label} é obrigatório'
            })
    return missing

def error_response_missing(missing: list, status: int = 400):
    """Formata resposta padrão para campos obrigatórios ausentes."""
    return jsonify({
        'success': False,
        'code': 'missing_fields',
        'message': 'Campos obrigatórios ausentes',
        'missing_fields': [m['field'] for m in missing],
        'details': [{'field': m['field'], 'message': m['message']} for m in missing]
    }), status