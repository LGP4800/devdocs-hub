from flask import Blueprint, jsonify, request
from . import db, logger
from .models import Snippet
import datetime

# Grupul de rute cu prefix /api — toate rutele de aici devin /api/...
api = Blueprint('api', __name__)


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────
# Verifică dacă Flask și PostgreSQL sunt vii
# Folosit de Docker, CI/CD și punctul verde din interfață
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


# ─── SNIPPETS CRUD ────────────────────────────────────────────────────────────

# GET toate snippeturile — returnează lista completă sortată după dată
@api.route('/snippets', methods=['GET'])
def get_snippets():
    snippets = Snippet.query.order_by(Snippet.created_at.desc()).all()
    logger.info(f'Fetched {len(snippets)} snippets')
    return jsonify([s.to_dict() for s in snippets]), 200


# GET un snippet după ID — returnează 404 automat dacă nu există
@api.route('/snippets/<int:id>', methods=['GET'])
def get_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    return jsonify(snippet.to_dict()), 200


# POST snippet nou — validează că title și content există
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
    logger.info(f'Created snippet: {snippet.title}')
    return jsonify(snippet.to_dict()), 201


# DELETE snippet după ID — șterge din DB și returnează confirmare
@api.route('/snippets/<int:id>', methods=['DELETE'])
def delete_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    db.session.delete(snippet)
    db.session.commit()
    logger.info(f'Deleted snippet: {id}')
    return jsonify({'message': 'deleted'}), 200


# ─── SEARCH ───────────────────────────────────────────────────────────────────

# GET search — caută în taguri și titlu, case-insensitive
# Exemplu: /api/snippets/search?q=python
@api.route('/snippets/search', methods=['GET'])
def search_snippets():
    query = request.args.get('q', '').strip() #citeste parametru din URL

    if not query:
        return jsonify([]), 200

    snippets = Snippet.query.filter(
        Snippet.tags.ilike(f'%{query}%') |
        Snippet.title.ilike(f'%{query}%')
    ).order_by(Snippet.created_at.desc()).all()

    logger.info(f'Search: "{query}" → {len(snippets)} results')
    return jsonify([s.to_dict() for s in snippets]), 200