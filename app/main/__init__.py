from flask import Blueprint


main = Blueprint('main', __name__)
# Put imports after main to avoid circular import errors
from . import views, errors
