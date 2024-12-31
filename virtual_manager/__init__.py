import os

from flask import Flask

from virtual_manager.helpers import camelCase, kebab_case, usd

# Application setup
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
      SECRET_KEY='dev',
      DATABASE=os.path.join(app.instance_path, 'project.sqlite'),
    )

    # Custom filters
    app.jinja_env.filters["usd"] = usd
    app.jinja_env.filters["kebab_case"] = kebab_case
    app.jinja_env.filters["camelCase"] = camelCase

    if test_config is None:
      # load the instance config, if it exists, when not testing
      app.config.from_pyfile('config.py', silent=True)
    else:
      # load the test config if passed in
      app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
      os.makedirs(app.instance_path)
    except OSError:
      pass

    # initialize DB
    from . import db
    db.init_app(app)

    # Package structure -> https://youtu.be/44PvX0Yv368
    # Blueprints registration
    from . import src
    app.register_blueprint(src.index.bp)
    app.register_blueprint(src.auth.bp)
    app.register_blueprint(src.items.bp)
    app.register_blueprint(src.products.bp)
    app.register_blueprint(src.recipes.bp)
    app.register_blueprint(src.transactions.bp)

    return app