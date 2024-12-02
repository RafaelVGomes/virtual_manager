from os import wait
from flask import Blueprint, flash, redirect, render_template, request, g, url_for

from virtual_manager.db import get_db
from virtual_manager.src.auth.view.auth import login_required


def validate_form(form):
  errors = {}

  if not form['product_name']:
    errors['product_name'] = "Please enter a product name."

  if not form['amount']:
    errors['amount'] = "Please enter an amount."
    
  if not form['measure']:
    errors['measure'] = "Please select a measure."
  elif form['measure'] not in ['kg', 'L', 'Unit']:
    errors['measure'] = "Invalid measure."

  if not form['quantity_alert']:
    errors['quantity_alert'] = "Please enter a quantity alert."

  if not form['price']:
    errors['price'] = "Please enter a price."

  if form['has_recipe'] not in [0, 1]:
    errors['has_recipe'] = "Invalid option."

  if errors:
    flash('Fill all required fields!#warning', 'messages')
    for field, message in errors.items():
      print(f"{field}: {message}")
      flash(message, field)
    return False
  else:
    return True


bp = Blueprint('products', __name__, url_prefix='/products', template_folder='../html', static_folder='../../products', static_url_path='/')

@bp.route("/overview")
@login_required
def overview():
  """List all products on stock"""
  db = get_db()
  user_id = g.user['id']
  products = db.execute("SELECT * FROM products WHERE user_id = ?;", (user_id,)).fetchall()
  return render_template("products.html", products=products)


@bp.route("/create-product", methods=["GET", "POST"])
@login_required
def create_product():
  """Create product"""
  db = get_db()
  form = {}

  if request.method == "GET":
    return render_template("product-detail.html")
  
  if request.method == "POST":
    form = {
      'product_name': request.form.get("product_name"),
      'amount': request.form.get("amount", type=int),
      'measure': request.form.get("measure"),
      'quantity_alert': request.form.get("quantity_alert", type=int),
      'price': request.form.get("price", type=float),
      'has_recipe': request.form.get("has_recipe", type=int)
    }
    
    if validate_form(form):
      try:    
        form['user_id'] = g.user['id']
        
        prod_id = db.execute(
          """--sql
          INSERT INTO products (user_id, product_name, amount, measure, quantity_alert, price, has_recipe)
          VALUES (:user_id, :product_name, :amount, :measure, :quantity_alert, :price, :has_recipe);
          """, (form)
        ).lastrowid

        db.commit()
        
        if form['has_recipe'] == 1:
          # TODO: Implement redirect to recipes giving users a choice to return to create more products
          pass

        flash(f"Product saved.#success", 'messages')
        return redirect(url_for("products.create_product"))
      except db.IntegrityError as e:
        e = str(e)

        print("Error:", e)
        flash(f"Product not created!#danger", 'messages')

        if e.split(" ")[0] == "UNIQUE" and e.split(".")[1] == "product_name":
          flash("Already in use.", "product_name")
          
        return render_template("product-detail.html", form=form)
    else:
      return render_template("product-detail.html", form=form)


@bp.route("/update-product/<int:id>", methods=["GET", "POST"])
@login_required
def update_product(id):
  """Modify product"""
  db = get_db()
  product = db.execute("SELECT * FROM products WHERE id = ? AND user_id = ?;", (id, g.user['id'])).fetchone()
  
  if request.method == "GET":
    return render_template("product-detail.html", form=product)

  if request.method == "POST" and id is product['id']:
    form = {
      'id': product['id'],
      'product_name': request.form.get("product_name"),
      'amount': request.form.get("amount", type=int),
      'measure': request.form.get("measure"),
      'quantity_alert': request.form.get("quantity_alert", type=int),
      'price': request.form.get("price", type=float),
      'has_recipe': request.form.get("has_recipe", type=int),
      'errors': 0
    }

    try:
      if validate_form(form):
        db.execute(
          """--sql
          UPDATE products SET
            product_name = :product_name,
            amount = :amount,
            measure = :measure,
            quantity_alert = :quantity_alert,
            price = :price,
            has_recipe = :has_recipe
          WHERE id = :id;
          """, (form)
        )

        db.commit()

        flash(f"Product updated.#success", 'messages')
        return redirect(url_for("products.overview"))
      else:
        return render_template("update-product.html", product=form)
    except db.IntegrityError as e:
        e = str(e)

        print("Error:", e)
        flash(f"Product not updated!#danger", 'messages')

        if e.split(" ")[0] == "UNIQUE" and e.split(".")[1] == "product_name":
          flash("Already in use.", "product_name")

        return render_template("update-product.html", product=form)
  else:
    flash(f"Product ID changed!.#danger", 'messages')
    return render_template("product-detail.html", form=form)


@bp.route("/delete-product/<int:id>")
@login_required
def delete_product(id):
    """Erase product"""
    db = get_db()

    user_id = g.user['id']
    # item_name = db.execute("SELECT product_name FROM products WHERE id = ? AND user_id = ?", (id, user_id)).fetchone()['product_name']
    
    db.execute("DELETE FROM products WHERE id = ? AND user_id = ?", (id, user_id))
    # TODO
    # db.execute(
    #   """--sql
    #   INSERT INTO products_log (user_id, operation, item_name)
    #   VALUES (?,?,?);
    #   """, (user_id, 'deleted', item_name)
    # )
    
    db.commit()
    return redirect(url_for("products.overview"))

@bp.route("/history")
@login_required
def history():
  """Historic of purchases and sales"""
  db = get_db()
  history = db.execute(
    """--sql
      SELECT DATETIME(h.date, 'localtime') as date, u.username, h.item_name, h.trade, h.price, h.amount, h.measure, h.total FROM users u, items_history h WHERE h.user_id = u.id AND u.id = ?;
    """,
    (g.user['id'],)
  ).fetchall()
  return render_template("items-history.html", history=history)

@bp.route("/log")
@login_required
def log():
  """Historic of purchases and sales"""
  db = get_db()
  log = db.execute(
    """--sql
      SELECT DATETIME(l.date, 'localtime') as date, u.username, l.item_name, l.operation, l.item_field, l.old_value, l.new_value FROM users as u, items_log as l WHERE l.user_id = u.id AND u.id = ?;
    """,
    (g.user['id'],)
  ).fetchall()
  return render_template("items-log.html", log=log)