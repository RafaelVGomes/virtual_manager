from flask import Blueprint, g, render_template

from virtual_manager.db import get_db
from virtual_manager.src.auth.view.auth import login_required

bp = Blueprint('index', __name__, template_folder='../html')

@bp.route("/")
@login_required
def overview():
  """Shows items and products in stock"""
  db = get_db()
  user_id = g.user['id']
  items = db.execute("SELECT * FROM items WHERE user_id = ?;", (user_id,)).fetchall()
  products = db.execute("SELECT * FROM products WHERE user_id = ?;", (user_id,)).fetchall()
  return render_template("index.html", items=items, products=products)
  