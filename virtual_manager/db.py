import os
import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
  if 'db' not in g:
    g.db = sqlite3.connect(
      current_app.config['DATABASE'],
      detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory = sqlite3.Row

  return g.db

def close_db(e=None):
  db = g.pop('db', None)

  if db is not None:
    db.close()
      
def remove_db():
  """Remove the existing database file."""
  db_path = current_app.config['DATABASE']
  if os.path.exists(db_path):
    os.remove(db_path)
    click.echo(f'Database removed: {db_path}')
  else:
    click.echo('No database file found to remove.')

def init_db():
  db = get_db()

  with current_app.open_resource('schema.sql') as f:
    db.executescript(f.read().decode('utf8'))

def insert_fixtures():
  """Insert development fixtures."""
  db = get_db()
  
  # Insert users
  users = [
    ('rafael', generate_password_hash('123'), 1),
    ('pedro', generate_password_hash('123'), 1),
    ('off', generate_password_hash('123'), 0)
  ]
  db.executemany(
    "INSERT INTO users (username, hash, is_active) VALUES (?, ?, ?)",
    users
  )
  
  # Insert items
  items = [
    (1, 'item a', 0, 'kg', 10, 0),  # user_id=1
    (1, 'item b', 0, 'pcs', 5, 0),  # user_id=1
    (2, 'item c', 0, 'L', 2, 0)   # user_id=2
  ]
  db.executemany(
    "INSERT INTO items (user_id, item_name, amount, measure, quantity_alert, price) VALUES (?, ?, ?, ?, ?, ?)",
    items
  )
  
  # Insert products
  products = [
    (1, 'product a', 0, 'pcs', 2, 0, 1),  # user_id=1
    (2, 'product b', 0, 'L', 3, 0, 1)   # user_id=2
  ]
  db.executemany(
    "INSERT INTO products (user_id, product_name, amount, measure, quantity_alert, price, has_recipe) VALUES (?, ?, ?, ?, ?, ?, ?)",
    products
  )
  
  db.commit()
  click.echo('Development fixtures inserted.')

@click.command('init-db')
@click.option('--renew', is_flag=True, help='Remove and recreate the database.')
@click.option('--fixtures', is_flag=True, help='Insert development fixtures.')
def init_db_command(renew, fixtures):
  """"Create tables if doesn't exists."""
  if renew:
    remove_db()
  init_db()
  if fixtures:
    insert_fixtures()
  click.echo('Database initialized' + (' after renewal' if renew else '') + (', with fixtures' if fixtures else ''))

def init_app(app):
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)
