from flask import Blueprint, jsonify, request
from . import db, logger
from .models import Snippet
import datetime

api = Blueprint('api', __name__)

# Health check — folosit de Docker si CI/CD
@api.route('/health')
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'ok'
    except Exception as e:
        logger.error(f'Database health check failed: {e}')
        db_status = 'error'

    status = 'ok' if db_status == 'ok' else 'degraded'
    logger.info(f'Health check: {status}')

    return jsonify({
        'status':    status,
        'database':  db_status,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }), 200 if status == 'ok' else 503

# GET toate snippeturile
@api.route('/snippets', methods=['GET'])
def get_snippets():
    snippets = Snippet.query.order_by(Snippet.created_at.desc()).all()
    return jsonify([s.to_dict() for s in snippets]), 200

# GET un snippet dupa ID
@api.route('/snippets/<int:id>', methods=['GET'])
def get_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    return jsonify(snippet.to_dict()), 200

# POST snippet nou
@api.route('/snippets', methods=['POST'])
def create_snippet():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'title and content are required'}), 400

    snippet = Snippet(
        title    = data['title'],
        content  = data['content'],
        language = data.get('language', 'text'),
        tags     = ','.join(data.get('tags', [])),
    )
    db.session.add(snippet)
    db.session.commit()
    return jsonify(snippet.to_dict()), 201

# DELETE snippet
@api.route('/snippets/<int:id>', methods=['DELETE'])
def delete_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    db.session.delete(snippet)
    db.session.commit()
    return jsonify({'message': 'deleted'}), 200