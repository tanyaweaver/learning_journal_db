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

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope='function')
def new_session(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    dbsession = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return dbsession

# Testing the models.


def test_model_gets_added(new_session):
    """Test the creation of the new model."""
    assert len(new_session.query(MyModel).all()) == 0
    model = MyModel(title="test_day", body="test_body")
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(MyModel).all()) == 1


def test_model_gets_added_2(new_session):
    """Test the creation of 2 new models in the row."""
    assert len(new_session.query(MyModel).all()) == 0
    model = MyModel(title="test_day", body="test_body")
    new_session.add(model)
    new_session.flush()
    model = MyModel(title="test_day2", body="test_body2")
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(MyModel).all()) == 2

# Testing the views.


def dummy_http_request(new_session):
    test_request = testing.DummyRequest()
    test_request.dbsession = new_session
    return test_request


def dummy_http_request_post(title, body, date, new_session):
    """Define a dummy request with method="POST"."""
    test_request = testing.DummyRequest()
    test_request.dbsession = new_session
    test_request.method = 'POST'
    test_request.POST['title'] = title
    test_request.POST['body'] = body
    test_request.POST['date'] = date
    return test_request


def test_lists_title(new_session):
    """Test whether lists() pull out correct info from db."""
    from .views.default import lists
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    result = lists(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.title == 'test1'


def test_lists_body(new_session):
    """Test whether lists() pull out correct info from db."""
    from .views.default import lists
    new_session.add(MyModel(title='test_1', body='test2', date='test3'))
    new_session.flush()
    result = lists(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.body == 'test2'


def test_lists_date(new_session):
    """Test whether lists() pull out correct info from db."""
    from .views.default import lists
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    result = lists(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.date == 'test3'


def test_create(new_session):
    """
    Tests whether create() returns an empty {}
    on 'GET' request.
    """
    from .views.default import create
    assert create(dummy_http_request(new_session)) == {}


def test_add_new_model(new_session):
    """
    Test whether add_new_model() (a helper function) creates a new model.
    Check this using lists().
    """
    from .views.default import add_new_model, lists
    add_new_model(dummy_http_request_post('a', 'b', 'c', new_session))
    result = lists(dummy_http_request(new_session))
    for entry in result['entries']:
        assert entry.title == 'a'


def test_create_error(new_session):
    """
    Test whether an error msg shows up on the page
    in case an empty entry on the new_entry page is submitted.
    """
    from .views.default import create
    result = create(dummy_http_request_post('', '', '', new_session))
    assert result['error_msg'] == "Can't submit empty entry."


def test_detail_get(new_session):
    """Test whether right details are returned upon calling detail()."""
    from .views.default import detail
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    request = dummy_http_request(new_session)
    request.matchdict['id'] = 1
    result = detail(request)
    assert result['entry'].title == 'test1'


def test_update_get(new_session):
    """Test whether right details are returned upon calling update()."""
    from .views.default import update
    new_session.add(MyModel(title='test1', body='test2', date='test3'))
    new_session.flush()
    request = dummy_http_request(new_session)
    request.matchdict['id'] = 1
    result = update(request)
    assert result['entry'].title == 'test1'


# Getting this error when try to run test update() or
# create() with a POST request (example of the test is after the err-msg.)
############################
# def getUtility(self, provided, name=_u('')):
#         utility = self.utilities.lookup((), provided, name)
#         if utility is None:
# >           raise ComponentLookupError(provided, name)
# E           zope.interface.interfaces.ComponentLookupError:
# (<InterfaceClass pyramid.interfaces.IRoutesMapper>, '')
############################
# def test_update_post(new_session):
#     from .views.default import update, lists
#     new_session.add(MyModel(title='test1', body='test2', date='test3'))
#     new_session.flush()
#     update(dummy_http_request_post('a', 'b', 'c', new_session))
#     page_update = lists(dummy_http_request(new_session))
#     assert len(page_update['entries']) == 2
