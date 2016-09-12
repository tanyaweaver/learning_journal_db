from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from ..models import MyModel
from pyramid.httpexceptions import HTTPFound
import email.utils
from pyramid.security import remember, forget
from learning_journal_db.security import check_credentials


@view_config(route_name='home')
def home(request):
    if request.authenticated_userid:
        return HTTPFound(request.route_url('lists'))
    else:
        return HTTPFound(request.route_url('login'))


@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    msg = ''
    if request.method == 'POST':
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        if check_credentials(username, password):
            headers = remember(request, username)
            return HTTPFound(request.route_url('lists'), headers=headers)
        else:
            msg = "Can't recognize username/password. Please try again."
    return {'msg': msg}


@view_config(route_name='logout', permission='secret')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('login'), headers=headers)


def add_new_model(request):
    """
    Add new model to db using the values from the form.
    A helper function for update() and create()."""
    new_title = request.POST['title']
    new_body = request.POST['body']
    new_date = email.utils.formatdate(usegmt=True)
    entry = MyModel(title=new_title, body=new_body, date=new_date)
    request.dbsession.add(entry)
    return {'entry': entry}


@view_config(
    route_name='lists', renderer='templates/home_page.jinja2',
    permission='secret'
)
def lists(request):
    """Return all the entries from the database."""
    query = request.dbsession.query(MyModel)
    entries = query.all()
    return {"entries": entries}


@view_config(
    route_name='create', renderer='templates/new_entry.jinja2',
    permission='secret'
)
def create(request):
    """
    Display an empty form on "GET".
    Create a new model and return to the home_page on "POST".
    Display an err_msg if both 'title' and 'body' in the form are empty.
    """
    session = {}
    error_msg = ''
    if request.method == 'GET':
        session['title'] = ''
        session['body'] = ''
        return {'session': session, 'error_msg': error_msg}
    if request.method == 'POST':
        if request.POST['title'] != '' and request.POST['body'] != '':
            add_new_model(request)
            return HTTPFound(request.route_url('lists'))
        else:
            session['title'] = request.POST['title']
            session['body'] = request.POST['body']
            error_msg = "Title and Notes fields require at least 1 character."
            return {'session': session, 'error_msg': error_msg}


@view_config(
    route_name='detail', renderer='templates/single_entry.jinja2',
    permission='secret'
)
def detail(request):
    """Display details of the entry with a particular id."""
    query = request.dbsession.query(MyModel)
    entry = query.filter(MyModel.id ==
                         int(request.matchdict['id'])).first()
    return {'entry': entry}


@view_config(
    route_name='update', renderer='templates/edit_entry.jinja2',
    permission='secret'
)
def update(request):
    """
    Display details of particular entry on "GET".
    Create a new model and return to the home_page on "POST".
    """
    session = {}
    error_msg = ''

    query = request.dbsession.query(MyModel)
    entry = query.filter(MyModel.id ==
                         int(request.matchdict['id'])).first()
    session['title'] = entry.title
    session['body'] = entry.body
    session['id'] = request.matchdict['id']

    if request.method == 'GET':
            return {'entry': session, 'error_msg': error_msg}

    elif request.method == 'POST':
        if request.POST['title'] != '' and request.POST['body'] != '':
            add_new_model(request)
            return HTTPFound(request.route_url('lists'))
        else:
            error_msg = "Title and Notes fields require at least 1 character."
            return {'entry': session, 'error_msg': error_msg}
