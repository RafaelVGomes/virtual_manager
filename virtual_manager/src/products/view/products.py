from ast import pattern
import re
import requests

from flask import Blueprint, flash, redirect, render_template, request, g, url_for

from virtual_manager.db import get_db
from virtual_manager.helpers import form_handle, updated_columns
from virtual_manager.src.auth.view.auth import login_required


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
  items = db.execute("SELECT id, item_name FROM items WHERE user_id = ?;", (g.user['id'],)).fetchall()
  
  if request.method == "POST":
    form = {
      'product_name': request.form.get("product_name"),
      'amount': request.form.get("amount", type=int),
      'measure': request.form.get("measure"),
      'quantity_alert': request.form.get("quantity_alert", type=int),
      'price': request.form.get("price", type=float),
      'has_recipe': request.form.get("has_recipe", type=int),
      'errors': 0
    }

    if not form['product_name']:
      flash("Please enter an product name.", 'product_name')
      form['errors'] += 1

    if not form['amount']:
      flash("Please enter an amount.", 'amount')
      form['errors'] += 1
      
    if not form['measure']:
      flash("Please select a measure.", 'measure')
      form['errors'] += 1
    elif form['measure'] not in ['Kg', 'L', 'Unit']:
      flash("Invalid measure.", 'measure')
      form['errors'] += 1

    if not form['quantity_alert']:
      flash("Please enter a quantity alert.", 'quantity_alert')
      form['errors'] += 1

    if not form['price']:
      flash("Please enter a price.", 'price')
      form['errors'] += 1

    if form['has_recipe'] not in [0, 1]:
      flash("Invalid option.", 'has_recipe')
      form['errors'] += 1

    # if form['has_recipe'] == 1 and not form['recipes']:
    #   flash("Please choose recipe items.", 'has_recipe')
    #   form['errors'] += 1


    if form['errors']:
      return render_template("create-product.html", data=form, items=items)
    else:
      form['user_id'] = g.user['id']
      
      prod_id = db.execute(
        """--sql
        INSERT INTO products (user_id, product_name, amount, measure, quantity_alert, price, has_recipe)
        VALUES (:user_id, :product_name, :amount, :measure, :quantity_alert, :price, :has_recipe);
        """, (form)
      ).lastrowid

      # db.execute(
      #   """--sql
      #   INSERT INTO products_log (user_id, operation, product_name)
      #   VALUES (:user_id, 'created', :product_name);
      #   """, (data)
      # )

      # data['total'] = data['amount'] * data['price']
      # db.execute(
      #   """--sql
      #   INSERT INTO products_history (user_id, product_name, trade, price, amount, measure, total)
      #   VALUES (:user_id, :product_name, 'purchase', :price, :amount, :measure, :total)
      #   """, (data)
      # )
      
      # purchase_value = round(data['amount'] * data['price'], 2)
      # db.execute("UPDATE users SET cash = users.cash - ? WHERE id = ?", (purchase_value, data['user_id']))

      db.commit()
      
      if form['has_recipe'] == 1:
        form_handle(prod_id, request)
      
      return redirect(url_for("products.create_product"))
    
  return render_template("create-product.html", items=items)


@bp.route("/update-product/<int:id>", methods=["GET", "POST"])
@login_required
def update_product(id):
  """Modify product"""
  db = get_db()
  product = db.execute("SELECT * FROM products WHERE id = ? AND user_id = ?;", (id, g.user['id'])).fetchone()

  if request.method == "POST":
    form = {
      'id': id,
      'amount': request.form.get("amount", type=int),
      'measure': request.form.get("measure"),
      'quantity_alert': request.form.get("quantity_alert", type=int),
      'price': request.form.get("price", type=float),
      'sale_price': request.form.get("sale_price", type=float),
      'has_recipe': request.form.get("has_recipe", type=int),
      'errors': 0
    }
    
    if not form['amount']:
      flash("Please enter a amount", 'amount')
      form['errors'] += 1
    
    if not form['measure']:
      flash("Please choose a measure", 'measure')
      form['errors'] += 1
    
    if not form['quantity_alert']:
      flash("Please enter an alert quantity", 'quantity_alert')
      form['errors'] += 1
    
    if not form['price']:
      flash("Please enter a price", 'price')
      form['errors'] += 1
    
    if form['errors']:
      return render_template("update-product.html", product=form)
    else:
      form['id'] = id
      db.execute(
        """--sql
        UPDATE products SET amount = :amount, price = :price, quantity_alert = :quantity_alert, measure = :measure, has_recipe = :has_recipe WHERE id = :id;
        """, (form)
      )

      # form['user_id'] = g.user['id']
      # form['item_name'] = item['item_name']
      # for col, values in updated_columns(product, form).items():
      #   form['item_field'] = col
      #   form['old_value'] = values['old']
      #   form['new_value'] = values['new']

      #   db.execute(
      #     """--sql
      #     INSERT INTO items_log (user_id, operation, item_name, item_field, old_value, new_value)
      #     VALUES (:user_id, 'updated', :item_name, :item_field, :old_value, :new_value);
      #     """, (form)
      #   )

      db.commit()
      return redirect(url_for("products.overview"))
  
  return render_template("update-product.html", product=product)


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