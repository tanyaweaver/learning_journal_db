import os



from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.exceptions import ConfigurationExecutionError
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow


def check_credentials(username, password):
    from passlib.apps import custom_app_context
    # stored_username = os.environ.get('AUTH_USERNAME', '')
    # stored_password = os.environ.get('AUTH_PASSWORD', '')
    stored_username = 'tw'
    stored_password = '$6$rounds=696756$UWRWhhuKcNTbArn.$cGYtf5qzBAq0mKBTVcro9K051.oxV0gblPIe5LK25GahlwQnnEHaXWWYwQ1lX.w1czy/Xe/zJlDc84lafp7mW0'
    is_authenticated = False
    if stored_username and stored_password:
        if username == stored_username:
            try:
                is_authenticated = custom_app_context.verify(password, stored_password)
            except ValueError:
                pass
    return is_authenticated



class MyRoot(object):
    def __init__(self, request):
        self.request = request

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'secret')
    ]


def includeme(config):
    """Security-related configuration."""
    auth_secret = os.environ.get('AUTH_SECRET', '')
    authn_policy = AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512'
    )
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    # config.set_default_permission('view')
    config.set_root_factory(MyRoot)