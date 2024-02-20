import pytest
from app import db, User, Content

from app import app  # Import the app object from the app module

@pytest.fixture(scope='module')
def test_client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_create_user(test_client):
    new_user = User(username='test_user', email='test@example.com', password='password')
    db.session.add(new_user)
    db.session.commit()

    assert new_user.id is not None

def test_create_content(test_client):
    new_content = Content(title='Test Content', body='This is a test content')
    db.session.add(new_content)
    db.session.commit()

    assert new_content.id is not None
