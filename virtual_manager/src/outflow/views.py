from flask import (Blueprint, abort, flash, g, redirect, render_template, request,
                   url_for)

from virtual_manager.db import get_db
from virtual_manager.src.auth.views import login_required

bp = Blueprint('outflow', __name__, url_prefix='/outflow', template_folder='./html', static_folder='../outflow')

@bp.route("/overview")
@login_required
def overview():
  """List all registered items, products and recipes."""
  db = get_db()
  context = {}

  context['items'] = db.execute("""--sql
    SELECT id, item_name, amount, quantity_alert
    FROM items WHERE user_id = ?
    ORDER BY items.item_name ASC;""", (g.user['id'],)
  ).fetchall()

  context['products'] = db.execute("""--sql
    SELECT id, product_name, amount, quantity_alert, has_recipe
    FROM products WHERE user_id = ?
    ORDER BY products.product_name ASC;""", (g.user['id'],)
  ).fetchall()

  return render_template("outflow.html", **context)

@bp.route("/withdraw-item/<int:id>", methods=["GET", "POST"])
@login_required
def withdraw_item(id):
  """List all registered items."""
  db = get_db()
  form = db.execute("""--sql
    SELECT id, item_name, amount
    FROM items WHERE user_id = ? AND id = ?
    ORDER BY items.item_name ASC;""", (g.user['id'], id)
  ).fetchone()

  if not form:
    abort(404, description="Item not found.")

  if request.method == "GET":
    return render_template("withdraw-item-detail.html", form=form)
  
  if request.method == "POST":
    form = dict(form)
    form['amount'] = int(form['amount']) - int(request.form['amount'])

    try:
      db.execute(
        """--sql
        UPDATE items SET
          amount = :amount
        WHERE id = :id AND user_id = :user_id
        """, {**form, 'id': id, 'user_id': g.user['id']}
      )

      db.commit()

      flash(f"Item removed.#success", 'messages')
      return redirect(url_for("outflow.overview"))
    except db.IntegrityError as e:
      e = str(e)
      print("Error:", e)
      flash(f"Item not removed!#danger", 'messages')
    return render_template("withdraw-item-detail.html", form=form)
  
@bp.route("/withdraw-product/<int:id>", methods=["GET", "POST"])
@login_required
def withdraw_product(id):
  """List all registered products."""
  db = get_db()
  form = db.execute("""--sql
    SELECT id, product_name, amount
    FROM products WHERE user_id = ? AND id = ?
    ORDER BY products.product_name ASC;""", (g.user['id'], id)
  ).fetchone()

  if not form:
    abort(404, description="Product not found.")

  if request.method == "GET":
    return render_template("withdraw-product-detail.html", form=form)
  
  if request.method == "POST":
    form = dict(form)
    form['amount'] = int(form['amount']) - int(request.form['amount'])

    try:
      db.execute(
        """--sql
        UPDATE products SET
          amount = :amount
        WHERE id = :id AND user_id = :user_id
        """, {**form, 'id': id, 'user_id': g.user['id']}
      )

      db.commit()

      flash(f"Product removed.#success", 'messages')
      return redirect(url_for("outflow.overview"))
    except db.IntegrityError as e:
      e = str(e)
      print("Error:", e)
      flash(f"Product not removed!#danger", 'messages')
    return render_template("withdraw-item-detail.html", form=form)