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
from .views.default import (
    detail, create, lists, update, add_new_model
)
from passlib.apps import custom_app_context
from .security import check_credentials
import os

DB_SETTINGS = {'sqlalchemy.url': 'sqlite:///:memory:'}


@pytest.fixture(scope='session')
def sqlengine(request):
    config = testing.setUp(settings=DB_SETTINGS)
    config.testing_securitypolicy(userid='user', permissive=True)
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


@pytest.fixture()
def app():
    '''testapp fixture'''
    from learning_journal_db import main
    app = main({}, **DB_SETTINGS)
    from webtest import TestApp
    return TestApp(app)


# Testing security
PRIVATE_ROUTES = [
    ('/list'),
    ('/journal/1'),
    ('/journal/new-entry'),
    ('/journal/1/edit-entry'),
    ('/logout'),
]


def test_redirection_from_home_page(app):
    '''Test that any user will be redirected from '/'. '''
    response = app.get('/', status='3*')
    assert response.status_code == 302


def test_login_view_is_public(app):
    '''Test that any user can view '/login' '''
    response = app.get('/login', status='2*')
    assert response.status_code == 200


@pytest.mark.parametrize('route', PRIVATE_ROUTES)
def test_no_access_to_private_views_if_no_auth(route, app):
    """Test that unathurized user can't access private routes."""
    response = app.get(route, status='4*')
    assert response.status_code == 403


@pytest.fixture()
def auth_env():
    username = 'user'
    password = 'password'
    os.environ['AUTH_USERNAME'] = username
    os.environ['AUTH_PASSWORD'] = custom_app_context.encrypt(password)
    return username, password


def test_check_cred(auth_env):
    """
    Test that check_credentials() returns True
    when user's credentials match stored values.
    """
    act_user, act_pass = auth_env
    assert check_credentials(act_user, act_pass)


def test_bad_password_fails_check_cred(auth_env):
    """Test that check_credentials() returns False for a bad password."""
    act_user, act_pass = auth_env
    fake_pass = act_pass + 'aaa'
    assert not check_credentials(act_user, fake_pass)


def test_bad_username_fails_check_cred(auth_env):
    """Test that check_credentials() returns False for a bad username."""
    act_user, act_pass = auth_env
    fake_user = act_user + 'aaa'
    assert not check_credentials(fake_user, act_pass)


def test_auth_user_redirected_after_login(app, auth_env):
    """Test that authorized user will be redirected from login_page."""
    act_user, act_pass = auth_env
    auth_data = {
        'username': act_user,
        'password': act_pass
    }
    response = app.post('/login', params=auth_data, status='3*')
    assert response.status_code == 302


def test_unauth_user_fails_login(app, auth_env):
    """Test that unauthorized user will not be redirected from login_page."""
    act_user, act_pass = auth_env
    auth_data = {
        'username': act_user + 'fake',
        'password': act_pass
    }
    response = app.post('/login', params=auth_data, status='2*')
    assert response.status_code == 200


def test_unauth_user_fails_login_error_msg(app, auth_env):
    """
    Test that unauthorized user will see an error_msg after trying to log in.
    """
    act_user, act_pass = auth_env
    auth_data = {
        'username': act_user + 'fake',
        'password': act_pass
    }
    response = app.post('/login', params=auth_data, status='2*')
    assert "Please try again" in response.text


# Testing the models.


def test_model_gets_added(new_session):
    """Test the creation of the new model."""
    assert len(new_session.query(MyModel).all()) == 0
    model = MyModel(title="test_day", body="test_body")
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(MyModel).all()) == 1


# Testing the views.


def dummy_http_request(new_session):
    test_request = testing.DummyRequest()
    test_request.dbsession = new_session
    return test_request


def dummy_http_request_post(title, body, new_session):
    """Define a dummy request with method="POST"."""
    test_request = testing.DummyRequest()
    test_request.dbsession = new_session
    test_request.method = 'POST'
    test_request.POST['title'] = title
    test_request.POST['body'] = body
    return test_request


ATTR_VAL = [
    ('title', 'test1'),
    ('body', 'test2')
]


@pytest.mark.parametrize('attr, val', ATTR_VAL)
def test_lists(attr, val, new_session):
    """Test whether lists() pull out correct info from db."""
    new_session.add(MyModel(title='test1', body='test2'))
    new_session.flush()
    result = lists(dummy_http_request(new_session))
    for entry in result['entries']:
        assert getattr(entry, attr) == val


def test_create(new_session):
    """
    Test whether create() returns appropriate values
    on 'GET' request.
    """
    assert create(dummy_http_request(new_session)) == {'error_msg': '', 'session': {'body': '', 'title': ''}}


def test_create_error(new_session):
    """
    Test whether an error_msg shows up on the page
    in case an empty entry on the new_entry page is submitted.
    """
    result = create(dummy_http_request_post('', '', new_session))
    assert result['error_msg'] == "Title and Notes fields require at least"\
        " 1 character."


@pytest.mark.parametrize('attr, val', ATTR_VAL)
def test_add_new_model(attr, val, new_session):
    """
    Test whether add_new_model() (a helper function) creates a new model.
    Check this using lists().
    """
    add_new_model(dummy_http_request_post('test1', 'test2', new_session))
    result = lists(dummy_http_request(new_session))
    for entry in result['entries']:
        assert getattr(entry, attr) == val


@pytest.mark.parametrize('attr, val', ATTR_VAL)
def test_detail_get(attr, val, new_session):
    """Test whether right details are returned upon calling detail()."""
    new_session.add(MyModel(title='test1', body='test2'))
    new_session.flush()
    request = dummy_http_request(new_session)
    request.matchdict['id'] = 1
    result = detail(request)
    assert getattr(result['entry'], attr) == val


@pytest.mark.parametrize('attr, val', ATTR_VAL)
def test_update_get(val, attr, new_session):
    """Test whether right details are returned upon calling update()."""
    new_session.add(MyModel(title='test1', body='test2'))
    new_session.flush()
    request = dummy_http_request(new_session)
    request.matchdict['id'] = 1
    assert update(request) == {
        'entry': {'title': 'test1', 'body': 'test2', 'id': 1},
        'error_msg': ''
    }
