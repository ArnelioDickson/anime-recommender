import os

import flask

from . import db

app = flask.Flask(__name__, instance_relative_config=True)

app.config.from_mapping(SECRET_KEY='dev', DATABASE=os.path.join(
    app.instance_path, 'flask.sqlite'),)

app.app_context().push()

db.init_app(app)
