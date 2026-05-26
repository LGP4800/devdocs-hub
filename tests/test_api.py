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