import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    yield app


@pytest.fixture(autouse=True)
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(db):
    from app.models.user import User, Organization

    org = Organization(name="Test Hostel")
    db.session.add(org)
    db.session.flush()

    user = User(
        email="test@example.com",
        name="Test User",
        organization_id=org.id,
        email_verified=True,
    )
    user.set_password("TestPass123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers(client, sample_user):
    """Get JWT auth headers for the sample user."""
    from flask_jwt_extended import create_access_token

    with client.application.app_context():
        token = create_access_token(identity=sample_user.id)
        return {"Authorization": f"Bearer {token}"}
