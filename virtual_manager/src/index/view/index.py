from flask import Blueprint, g, render_template

from virtual_manager.db import DatabaseManager
from virtual_manager.src.auth.views import login_required

bp = Blueprint('index', __name__, template_folder='../html')

@bp.route("/")
@login_required
def overview():
  """Shows items and products in stock"""
  db = DatabaseManager().connect()
  user_id = g.user['id']
  items = db.execute("SELECT * FROM items WHERE user_id = ?;", (user_id,)).fetchall()
  products = db.execute("SELECT * FROM products WHERE user_id = ?;", (user_id,)).fetchall()
  return render_template("index.html", items=items, products=products)
  