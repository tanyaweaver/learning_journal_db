import pytest
import transaction
from pyramid import testing
from .models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from .models.mymodel import MyModel
from .models.meta import Base


@pytest.fixture(scope='session')
def sqlengine(request):
    config = testing.setUp(settings={
        'sqlalchemy.url': 'sqlite:///:memory:'
        })
    config.include('.models')
    settings = config.get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    def teardown():
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(engine)

    request.addfinalizer (teardown)
    return engine


@pytest.fixture(scope='session')
def new_session(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    session = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return session


def test_model_gets_added(new_session):
    assert len(new_session.query(MyModel).all()) == 0
    model = MyModel(title="test_day", body="test_body")
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(MyModel).all()) == 1
