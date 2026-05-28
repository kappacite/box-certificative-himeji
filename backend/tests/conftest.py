import pytest
from app import create_app
from dao import db as _db


@pytest.fixture(scope="session")
def app():
    """Session-wide Flask application configured for testing."""
    app = create_app("testing")
    return app


@pytest.fixture(scope="function")
def client(app):
    """A Flask test client for integration tests."""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def db_setup(app):
    """Function-scoped fixture to create and clean the database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
