import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    #verifică dacă condiția este adevarată
    assert response.get_json()['status'] == 'ok'

def test_create_snippet(client):
    response = client.post('/api/snippets', json={
        'title': 'Test snippet',
        'content': 'print("hello")',
        'language': 'python',
        'tags': ['test']
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test snippet'
    assert data['language'] == 'python'

def test_get_snippets(client):
    client.post('/api/snippets', json={
        'title': 'Snippet 1',
        'content': 'content 1'
    })
    response = client.get('/api/snippets')
    assert response.status_code == 200
    assert len(response.get_json()) == 1

def test_create_snippet_missing_fields(client):
    response = client.post('/api/snippets', json={})
    assert response.status_code == 400

def test_search_snippets(client):
    # Creezi două snippeturi diferite
    client.post('/api/snippets', json={
        'title': 'Flask routes',
        'content': 'cod flask',
        'language': 'python',
        'tags': ['flask', 'python']
    })
    client.post('/api/snippets', json={
        'title': 'SQL queries',
        'content': 'cod sql',
        'language': 'sql',
        'tags': ['sql', 'database']
    })

    # Caută după tag
    response = client.get('/api/snippets/search?q=flask')
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert response.get_json()[0]['title'] == 'Flask routes'

    # Caută după titlu
    response = client.get('/api/snippets/search?q=SQL')
    assert response.status_code == 200
    assert len(response.get_json()) == 1

    # Caută ceva care nu există
    response = client.get('/api/snippets/search?q=javascript')
    assert response.status_code == 200
    assert len(response.get_json()) == 0