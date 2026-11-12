import pytest

from blog import create_app, db


@pytest.fixture()
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
            "WTF_CSRF_ENABLED": False,
        }
    )
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def registered_user(client):
    client.post(
        "/register",
        data={
            "name": "Test Writer",
            "email": "writer@example.com",
            "password": "TestPass123",
            "confirm_password": "TestPass123",
        },
        follow_redirects=True,
    )
    return {"email": "writer@example.com", "password": "TestPass123"}
