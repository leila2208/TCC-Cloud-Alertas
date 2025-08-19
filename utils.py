from flask import abort
from flask_login import current_user
from models import SUPERADMIN, ADMIN, NURSE, PATIENT

def require_roles(*roles):
    def wrapper(func):
        def inner(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)
        inner.__name__ = func.__name__
        return inner
    return wrapper
