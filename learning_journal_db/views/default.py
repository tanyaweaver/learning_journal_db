from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from ..models import MyModel
from pyramid.httpexceptions import HTTPFound
import email.utils

ENTRIES = [
     {
        "title": "Day1",
        "id": 1,
        "date": "August 21, 2016",
        "body": "Today I learned about Pyramid."
     },
     {
        "title": "Day2",
        "id": 2,
        "date": "August 22, 2016",
        "body": "Today I learned about heaps and templates."
     },
     {
        "title": "Day3",
        "id": 3,
        "date": "August 23, 2016",
        "body": "Today I learned about deploying to Heroku."
     },
     {
        "title": "Day4",
        "id": 4,
        "date": "August 25, 2016",
        "body": "Today I learned about deploying to birds."
     },
]


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


@view_config(route_name='lists', renderer='templates/home_page.jinja2')
def lists(request):
    """Return all the entries from the database."""
    try:
        query = request.dbsession.query(MyModel)
        entries = query.all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {"entries": entries}


@view_config(route_name='create', renderer='templates/new_entry.jinja2')
def create(request):
    """
    Display an empty form on "GET".
    Create a new model and return to the home_page on "POST".
    Display an err_msg if both 'title' and 'body' in the form are empty.
    """
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        if request.POST['title'] != '' or request.POST['body'] != '':
            add_new_model(request)
            return HTTPFound(request.route_url('lists'))
        else:
            error_msg = "Can't submit empty entry."
            return {'error_msg': error_msg}


@view_config(route_name='detail', renderer='templates/single_entry.jinja2')
def detail(request):
    """Display details of the entry with a particular id."""
    try:
        query = request.dbsession.query(MyModel)
        entry = query.filter(MyModel.id ==
                             int(request.matchdict['id'])).first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entry': entry}


@view_config(route_name='update', renderer='templates/edit_entry.jinja2')
def update(request):
    """
    Display details of particular entry on "GET".
    Create a new model and return to the home_page on "POST".
    """
    if request.method == "GET":
        return detail(request)
    elif request.method == 'POST':
        add_new_model(request)
        return HTTPFound(request.route_url('lists'))


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning_journal_db_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
