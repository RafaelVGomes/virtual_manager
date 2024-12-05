from flask import Blueprint, flash, redirect, render_template, request, g, url_for, abort
from virtual_manager.db import get_db
from virtual_manager.src.auth.view.auth import login_required

def validate_form(form):
  """Validate item form."""
  errors = {}

  if not form.get('item_name'):
    errors['item_name'] = "Please enter a name for this item."

  if not form.get('amount', None) or form['amount'] <= 0:
    errors['amount'] = "Amount must be greater than zero."

  if not form.get('measure'):
    errors['measure'] = "Please select a measure."
  elif form['measure'] not in ['kg', 'L', 'pcs']:
    errors['measure'] = "Invalid measure."

  if not form.get('quantity_alert', None) or form['quantity_alert'] < 0:
    errors['quantity_alert'] = "Quantity alert must be zero or greater."

  if not form.get('price', None) or form['price'] < 0:
    errors['price'] = "Price must be zero or greater."

  if errors:
    flash('Fill all required fields!#warning', 'messages')
    for field, message in errors.items():
      flash(message, field)
    return False
  return True

bp = Blueprint('items', __name__, url_prefix='/items', template_folder='../html', static_folder='../../items')

@bp.route("/overview")
@login_required
def overview():
  """List all items in stock."""
  db = get_db()
  items = db.execute("SELECT * FROM items WHERE user_id = ? ORDER BY items.item_name ASC;", (g.user['id'],)).fetchall()
  return render_template("items.html", items=items)

@bp.route("/create-item", methods=["GET", "POST"])
@login_required
def create_item():
  """Create item."""
  form = {}

  if request.method == "POST":
    form = {
      'item_name': request.form.get("item_name"),
      'amount': request.form.get("amount", type=int),
      'measure': request.form.get("measure"),
      'quantity_alert': request.form.get("quantity_alert", type=int),
      'price': request.form.get("price", type=float),
      'user_id': g.user['id']
    }
    
    if validate_form(form):
      try:
        db = get_db()
        db.execute(
          """--sql
          INSERT INTO items (user_id, item_name, amount, measure, quantity_alert, price)
          VALUES (:user_id, :item_name, :amount, :measure, :quantity_alert, :price);
          """, form
        )
        db.commit()
        flash("Item created successfully!#success", 'messages')
        return redirect(url_for("items.overview"))
      except db.IntegrityError:
        flash("Item not created. Name must be unique.#danger", 'messages')
    return render_template("item-detail.html", form=form)

  return render_template("item-detail.html", form=form)

@bp.route("/update-item/<int:id>", methods=["GET", "POST"])
@login_required
def update_item(id):
  """Modify item."""
  db = get_db()
  item = db.execute(
    "SELECT * FROM items WHERE id = ? AND user_id = ?;", (id, g.user['id'])
  ).fetchone()

  if not item:
    abort(404, description="Item not found or you do not have permission to access it.")

  if request.method == "POST":
    form = {
      'id': id,
      'item_name': request.form.get("item_name"),
      'amount': request.form.get("amount", type=int),
      'measure': request.form.get("measure"),
      'quantity_alert': request.form.get("quantity_alert", type=int),
      'price': request.form.get("price", type=float),
      'user_id': g.user['id']
    }
    
    if validate_form(form):
      try:
        db.execute(
          """--sql
          UPDATE items SET
            item_name = :item_name,
            amount = :amount,
            measure = :measure,
            quantity_alert = :quantity_alert,
            price = :price
          WHERE id = :id AND user_id = :user_id;
          """, form
        )
        db.commit()
        flash("Item updated successfully!#success", 'messages')
        return redirect(url_for("items.overview"))
      except db.IntegrityError:
        flash("Item not updated. Name must be unique.#danger", 'messages')
    return render_template("item-detail.html", form=form)

  return render_template("item-detail.html", form=dict(item))

@bp.route("/delete-item/<int:id>", methods=["POST"])
@login_required
def delete_item(id):
  """Erase item."""
  db = get_db()
  item = db.execute(
    "SELECT * FROM items WHERE id = ? AND user_id = ?;", (id, g.user['id'])
  ).fetchone()

  if not item:
    abort(404, description="Item not found or you do not have permission to delete it.")

  db.execute("DELETE FROM items WHERE id = ? AND user_id = ?;", (id, g.user['id']))
  db.commit()
  flash("Item deleted successfully!#success", 'messages')
  return redirect(url_for("items.overview"))
