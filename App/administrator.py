from werkzeug.exceptions import HTTPException
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from App.database_models import *
from flask import redirect, Response

basic_auth = BasicAuth()


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


admin = Admin(name='XeoSmartHome', template_mode='bootstrap3')


class MyModelView(ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class UsersView(MyModelView):
    column_searchable_list = ['email', 'username']
    create_modal = True
    edit_modal = True
    details_modal = True
    can_view_details = True
    can_export = False


admin.add_view(UsersView(User, db.session))
admin.add_view(MyModelView(File, db.session))
admin.add_view(MyModelView(Receiver, db.session))
