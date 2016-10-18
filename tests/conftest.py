import pytest

from cal import app as cal_app
from config import CalendarConfig
from models import db as cal_db


@pytest.fixture(scope="session")
def app(request):
    app = cal_app
    app.config.from_object(CalendarConfig(testing=True))
    ctx = app.test_request_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="class")
def db(request, app):
    cal_db.reflect()
    cal_db.drop_all()
    cal_db.create_all()

    def teardown():
        cal_db.session.close_all()
        cal_db.reflect()
        cal_db.drop_all()

    request.addfinalizer(teardown)
    return cal_db


@pytest.fixture(scope="class")
def session(request, db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
