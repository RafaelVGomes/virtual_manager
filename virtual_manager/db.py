import os
import sqlite3
from flask import current_app, g

class DatabaseManager:
  """Manages the database connection and operations."""
  
  def __init__(self, db_path=None):
    """
    Initializes the database manager.
    
    Args:
      db_path (str, optional): The path to the database file. If not provided, 
                               it will be retrieved from Flask's config.
    """
    self.db_path = db_path

  def get_db_path(self):
    """
    Retrieves the database file path.

    Returns:
      str: The database file path.

    Raises:
      RuntimeError: If the database path is not set.
    """
    if self.db_path:
      return self.db_path
    if current_app:
      return current_app.config["DATABASE"]
    raise RuntimeError("Database path is not set.")

  def connect(self):
    """
    Opens a new database connection if it does not exist in the request context.

    Returns:
      sqlite3.Connection: The database connection.
    """
    if 'db' not in g:
      g.db = sqlite3.connect(
        self.get_db_path(),
        detect_types=sqlite3.PARSE_DECLTYPES
      )
      g.db.row_factory = sqlite3.Row
    return g.db

  def close(self, e=None):
    """Closes the database connection if it exists."""
    db = g.pop('db', None)
    if db is not None:
      db.close()

  def execute(self, query, params=()):
    """
    Executes a query on the database.

    Args:
      query (str): The SQL query to execute.
      params (tuple, optional): The parameters for the query.

    Returns:
      sqlite3.Cursor: The cursor resulting from the execution.
    """
    db = self.connect()
    return db.execute(query, params)

  def commit(self):
    """Commits the current transaction."""
    self.connect().commit()

  def rollback(self):
    """Rolls back the current transaction."""
    self.connect().rollback()

  def remove_db(self):
    """
    Removes the existing database file.
    
    If the file does not exist, it prints a message.
    """
    db_path = self.get_db_path()
    if os.path.exists(db_path):
      os.remove(db_path)
      print(f"Database removed: {db_path}")
    else:
      print("No database file found to remove.")

  def init_db(self):
    """Initializes the database by executing schema.sql."""
    with current_app.app_context():
      with current_app.open_resource("schema.sql") as f:
        self.connect().executescript(f.read().decode("utf8"))

  def insert_fixtures(self):
    """Inserts development fixtures into the database."""
    db = self.connect()
    
    users = [
      ("rafael", "123", 1),
      ("pedro", "123", 1),
      ("off", "123", 0)
    ]
    db.executemany("INSERT INTO users (username, hash, is_active) VALUES (?, ?, ?)", users)

    items = [
      (1, "item a", 0, "kg", 10, 0),
      (1, "item b", 0, "pcs", 5, 0),
      (2, "item c", 0, "L", 2, 0)
    ]
    db.executemany("INSERT INTO items (user_id, item_name, amount, measure, quantity_alert, price) VALUES (?, ?, ?, ?, ?, ?)", items)

    products = [
      (1, "product a", 0, "pcs", 2, 0, 1),
      (2, "product b", 0, "L", 3, 0, 1)
    ]
    db.executemany("INSERT INTO products (user_id, product_name, amount, measure, quantity_alert, price, has_recipe) VALUES (?, ?, ?, ?, ?, ?, ?)", products)

    db.commit()
    print("Development fixtures inserted.")

# Flask CLI command
import click
from flask import current_app

@click.command("init-db")
@click.option("--renew", is_flag=True, help="Remove and recreate the database.")
@click.option("--fixtures", is_flag=True, help="Insert development fixtures.")
def init_db_command(renew, fixtures):
  """Initializes the database with optional renewal and fixtures."""
  db = DatabaseManager()

  with current_app.app_context():
    if renew:
      db.remove_db()
    db.init_db()
    if fixtures:
      db.insert_fixtures()

  print("Database initialized" + (" after renewal" if renew else "") + (", with fixtures" if fixtures else ""))

def init_app(app):
  """Registers database management functions with the Flask app."""
  app.teardown_appcontext(DatabaseManager().close)
  app.cli.add_command(init_db_command)
