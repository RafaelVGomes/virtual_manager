from flask import (Blueprint, abort, flash, g, redirect, render_template, request,
                   url_for)

from .form import get_data_to_save, get_form, validate_form
from virtual_manager.db import DatabaseManager
from virtual_manager.src.auth.views import login_required


bp = Blueprint('items', __name__, url_prefix='/items', template_folder='./html', static_folder='../../items')

@bp.route("/overview")
@login_required
def overview():
  """List all items in stock."""
  db = DatabaseManager().connect()
  items = db.execute("""--sql
    SELECT id, item_name, amount, measure
    FROM items WHERE user_id = ?
    ORDER BY items.item_name ASC;""", (g.user['id'],)
  ).fetchall()
  return render_template("items.html", items=items)

@bp.route("/create-item", methods=["GET", "POST"])
@login_required
def create_item():
  """Create item."""
  form = get_form()

  if request.method == "POST":
    form = get_form(request=request)
    
    if validate_form(form):
      form_to_save = get_data_to_save(form)
      
      try:
        db = DatabaseManager().connect()
        db.execute(
          """--sql
          INSERT INTO items (user_id, item_name, measure)
          VALUES (:user_id, :item_name, :measure);
          """, form_to_save
        )
        db.commit()
        flash("Item created successfully!#success", 'messages')
        return redirect(url_for("items.create_item"))
      except db.IntegrityError:
        flash("Item not created. Name must be unique.#danger", 'messages')
    return render_template("item-detail.html", form=form)

  return render_template("item-detail.html", form=form)

@bp.route("/update-item/<int:id>", methods=["GET", "POST"])
@login_required
def update_item(id):
  """Modify item."""
  db = DatabaseManager().connect()
  form = get_form(id=id)

  if request.method == "POST":
    form = get_form(request=request)
    
    if validate_form(form):
      form_to_save = get_data_to_save(form)

      try:
        db.execute(
          """--sql
          UPDATE items SET
            item_name = :item_name,
            measure = :measure
          WHERE id = :id AND user_id = :user_id;
          """, form_to_save
        )
        db.commit()
        flash("Item updated successfully!#success", 'messages')
        return redirect(url_for("items.overview"))
      except db.IntegrityError as e:
        e = str(e)

        print("Error:", e)

        if 'UNIQUE' in e and 'items.item_name' in e:
          flash("Item name already in use.", "item_name")
          flash(f"Choose a different name.#info", 'messages')
        else:
          flash(f"Item not updated!#danger", 'messages')
          return render_template("item-detail.html", form=form)
        
    return render_template("item-detail.html", form=form)

  return render_template("item-detail.html", form=form)

@bp.route("/delete-item/<int:id>", methods=["POST"])
@login_required
def delete_item(id):
  """Erase item."""
  db = DatabaseManager().connect()
  item = db.execute(
    "SELECT * FROM items WHERE id = ? AND user_id = ?;", (id, g.user['id'])
  ).fetchone()

  if not item:
    abort(404, description="Item not found or you do not have permission to delete it.")

  db.execute("DELETE FROM items WHERE id = ? AND user_id = ?;", (id, g.user['id']))
  db.commit()
  flash("Item deleted successfully!#success", 'messages')
  return redirect(url_for("items.overview"))
