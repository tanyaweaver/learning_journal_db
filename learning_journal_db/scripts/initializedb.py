import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import MyModel


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

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    # engine = get_engine(settings)
    # Base.metadata.create_all(engine)

    # session_factory = get_session_factory(engine)

    # with transaction.manager:
    #     dbsession = get_tm_session(session_factory, transaction.manager)
    #     for entry in ENTRIES:
    #         row = MyModel(id=entry['id'], title=entry['title'],
    #                       date=entry['date'], body=entry['body'])
    #         dbsession.add(row)
