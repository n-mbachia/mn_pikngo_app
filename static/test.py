import os
import tempfile
import pytest
from app import app, db, Content, ContentForm

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_admin_login(client):
    response = client.post('/admin/login', data={'username': 'admin', 'password': 'password'})
    assert b'Logged in successfully' in response.data

def test_admin_dashboard(client):
    response = client.post('/admin/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
    assert b'Admin Dashboard' in response.data

def test_content_creation(client):
    response = client.post('/admin/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
    assert b'Admin Dashboard' in response.data

    response = client.post('/admin/dashboard', data={'title': 'Test Content', 'body': 'Test Body'}, follow_redirects=True)
    assert b'Content added successfully' in response.data

def test_content_edit(client):
    response = client.post('/admin/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
    assert b'Admin Dashboard' in response.data

    # Create a dummy content
    content = Content(title='Test Content', body='Test Body')
    db.session.add(content)
    db.session.commit()

    response = client.post(f'/admin/edit_content/{content.id}', data={'title': 'Updated Content', 'body': 'Updated Body'}, follow_redirects=True)
    assert b'Content updated successfully' in response.data

def test_index(client):
    response = client.get('/')
    assert b'Latest Posts' in response.data

def test_post(client):
    # Create a dummy content
    content = Content(title='Test Content', body='Test Body')
    db.session.add(content)
    db.session.commit()

    response = client.get(f'/post/{content.id}')
    assert b'Test Content' in response.data
    assert b'Test Body' in response.data
