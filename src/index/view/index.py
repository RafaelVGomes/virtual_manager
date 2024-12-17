from flask import Blueprint, flash, g, render_template

from ...auth.view.auth import login_required
from ...db import get_db

bp = Blueprint('index', __name__, template_folder='../html')

@bp.route("/")
@login_required
def index():
  """Shows items and products in stock"""
  db = get_db()
  user_id = g.user['id']
  items = db.execute("SELECT * FROM items WHERE user_id = ?;", (user_id,)).fetchall()
  products = db.execute("SELECT * FROM products WHERE user_id = ?;", (user_id,)).fetchall()
  # recipes = db.execute("SELECT * FROM recipes;").fetchall()
  return render_template("index.html", items=items, products=products)
  