import json
from pprint import pprint

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from virtual_manager.db import get_db
from virtual_manager.src.auth.views import login_required


def validate_form(form):
  errors = {}

  try:
    if form['amount'] is None or form['amount'] < 0:
      errors['amount'] = "Please enter a valid positive number."
  except ValueError as e:
    print(f'"Amount" validation error: {e}')
    errors['amount'] = "Invalid amount. Must be a number."
    
  try:
    if form['quantity_alert'] is None or form['quantity_alert'] < 0:
      errors['quantity_alert'] = "Please enter a valid positive number."
  except ValueError as e:
    print(f'"Quantity alert" validation error: {e}')
    errors['quantity_alert'] = "Invalid quantity alert. Must be a number."

  if not form['price']:
    errors['price'] = "Please enter a price."

  if not form['sell_price']:
    errors['sell_price'] = "Please enter a price."

  if errors:
    flash('Fill all required fields!#warning', 'messages')
    for field, message in errors.items():
      print(f"{field}: {message}")
      flash(message, field)
    return False
  else:
    return True
  

bp = Blueprint('transactions', __name__, url_prefix='/transaction', template_folder='./html', static_folder='../transactions')

@bp.route("/overview")
@login_required
def overview():
  """List all products and items with stock low"""
  db = get_db()
  context = {}

  db_recipes = db.execute(
    """--sql
    SELECT p.id AS product_id, p.product_name, p.amount AS product_amount,
      json_group_array(
        json_object(
          'recipe_id', r.id,
          'id', r.item_id,
          'name', r.item_name,
          'demand', r.item_amount
        )
      ) AS items_list
    FROM products p
    LEFT JOIN (
      SELECT r.id, r.product_id,r.user_id, r.item_id, r.item_amount, i.item_name
      FROM recipes r
      LEFT JOIN items i ON r.item_id = i.id
      ORDER BY i.item_name ASC
    ) r ON r.product_id = p.id AND r.user_id = ?
    WHERE p.has_recipe = 1 AND p.user_id = ?
    GROUP BY p.id, p.product_name;
    """, (g.user['id'], g.user['id'])
  ).fetchall()

  context['recipes'] = []
  for db_recipe in db_recipes:
    recipe = {}
    for k in db_recipe.keys():
      if k == 'items_list':
        recipe[k] = json.loads(db_recipe[k])
        if recipe['items_list'][0]['recipe_id'] == None:
          recipe['items_list'] = [None]
      else:
        recipe[k] = db_recipe[k]

    context['recipes'].append(recipe)

  # context['products'] = db.execute("""--sql
  #   SELECT id, product_name, measure, has_recipe
  #   FROM products WHERE user_id = ?
  #   ORDER BY products.product_name ASC;
  # """, (g.user['id'],)).fetchall()

  db_items = db.execute(
    """--sql
    SELECT id, quantity_alert, amount
    FROM items WHERE user_id = ?
    """, (g.user['id'],)
  ).fetchall()
  
  context['items'] = {}
  for db_item in db_items:
    for k in db_item.keys():
      if k == "id":
        context['items'][db_item[k]] = {}
      if k == "quantity_alert":
        context['items'][db_item['id']]['alert'] = db_item[k]
      elif k == "amount":
        context['items'][db_item['id']]['total'] = db_item[k]
  context['items'] = json.dumps(context['items'])
  
  return render_template("transactions.html", **context)

@bp.route("/restock", methods=["GET", "POST"])
@login_required
def restock():
  """Create product"""
  db = get_db()
  form = {}

  if request.method == "GET":
    return render_template("product-detail.html", form=form)
  
  if request.method == "POST":
    form = {
      'amount': request.form.get("amount", type=int),
      'quantity_alert': request.form.get("quantity_alert", type=int),
      'price': request.form.get("price", type=float)
    }
    
    if validate_form(form):
      try:    
        form['user_id'] = g.user['id']
        
        db.execute(
          """--sql
          INSERT INTO products (user_id, amount, quantity_alert, price)
          VALUES (:user_id, :amount, :quantity_alert, :price);
          """, (form)
        ).lastrowid

        db.commit()
        
        flash(f"Amount updated.#success", 'messages')
        return redirect(url_for("products.create_product"))
      except db.IntegrityError as e:
        e = str(e)

        print("Error:", e)

        flash(f"Amount not updated!#danger", 'messages')
          
        return render_template("product-detail.html", form=form)
    else:
      return render_template("product-detail.html", form=form)