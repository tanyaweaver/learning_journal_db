def includeme(config):
    config.add_route('lists', '/')
    config.add_route('create', '/journal/new-entry')
    config.add_route('detail', r'/journal/{id:\d+}')
    config.add_route('update', r'/journal/{id:\d+}/edit-entry')
    config.add_static_view('static', 'learning_journal_db:static', cache_max_age=3600)