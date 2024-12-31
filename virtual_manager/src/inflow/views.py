from flask import (Blueprint, abort, flash, g, redirect, render_template, request,
                   url_for)

from virtual_manager.db import get_db
from virtual_manager.src.auth.views import login_required

bp = Blueprint('inflow', __name__, url_prefix='/inflow', template_folder='./html', static_folder='../inflow')

def group_recipes(context):
  grouped_data = []
    
  # Iterate through products
  for product in context['products']:
    if product['has_recipe'] == 1:
      # Filter recipes for the current product
      product_recipes = [recipe for recipe in context['recipes'] if recipe['product_id'] == product['id']]
      
      # For each recipe, get the corresponding items and a list with max production numbers per item total/demand
      items = []
      max_production = []
      for recipe in product_recipes:
        for item in context['items']:
          if item['id'] == recipe['item_id']:
            items.append({
              'recipe_id': recipe['id'],
              'id': item['id'],
              'name': item['item_name'],
              'alert': item['quantity_alert'],
              'demand': recipe['item_amount'],
              'total': item['amount']
            })

            max_production.append(item['amount'] / recipe['item_amount'])
      
      # Add to the grouping if there are items
      if items:
        grouped_data.append({
          'product_id': product['id'],
          'product_name': product['product_name'],
          'product_alert': product['quantity_alert'],
          'product_amount': product['amount'],
          'max_production': int(min(max_production)),
          'items_list': items
        })
  
  return grouped_data

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

  recipes = db.execute("""--sql
    SELECT *
    FROM recipes WHERE user_id = ?
    """, (g.user['id'],)
  ).fetchall()

  context['recipes'] = group_recipes({**context, 'recipes': recipes})
  context['products'] = [product for product in context['products'] if product['has_recipe'] == 0]
  
  return render_template("inflow.html", **context)

@bp.route("/supply-item/<int:id>", methods=["GET", "POST"])
@login_required
def supply_item(id):
  """List all registered items."""
  db = get_db()
  form = db.execute("""--sql
    SELECT id, item_name, quantity_alert, amount
    FROM items WHERE user_id = ? AND id = ?
    ORDER BY items.item_name ASC;""", (g.user['id'], id)
  ).fetchone()

  if not form:
    abort(404, description="Item not found.")

  if request.method == "GET":
    return render_template("supply-item-detail.html", form=form)
  
  if request.method == "POST":
    form = request.form

    try:
      db.execute(
        """--sql
        UPDATE items SET
          quantity_alert = :quantity_alert, 
          amount = :amount
        WHERE id = :id AND user_id = :user_id
        """, {**form, 'id': id, 'user_id': g.user['id']}
      )

      db.commit()

      flash(f"Item restocked.#success", 'messages')
      return redirect(url_for("inflow.overview"))
    except db.IntegrityError as e:
      e = str(e)
      print("Error:", e)
      flash(f"Item not restocked!#danger", 'messages')
    return render_template("supply-item-detail.html", form=form)
  
@bp.route("/supply-product/<int:id>", methods=["GET", "POST"])
@login_required
def supply_product(id):
  """List all registered products."""
  db = get_db()
  form = db.execute("""--sql
    SELECT id, product_name, quantity_alert, amount, has_recipe
    FROM products WHERE has_recipe = 0 AND user_id = ? AND id = ?
    ORDER BY products.product_name ASC;""", (g.user['id'], id)
  ).fetchone()

  if not form:
    abort(404, description="Product not found.")

  if request.method == "GET":
    return render_template("supply-product-detail.html", form=form)
  
  if request.method == "POST":
    form = request.form

    try:
      db.execute(
        """--sql
        UPDATE products SET
          quantity_alert = :quantity_alert, 
          amount = :amount
        WHERE id = :id AND user_id = :user_id
        """, {**form, 'id': id, 'user_id': g.user['id']}
      )

      db.commit()

      flash(f"Product restocked.#success", 'messages')
      return redirect(url_for("inflow.overview"))
    except db.IntegrityError as e:
      e = str(e)
      print("Error:", e)
      flash(f"Product not restocked!#danger", 'messages')
    return render_template("supply-item-detail.html", form=form)
  
@bp.route("/produce-product/<int:id>", methods=["GET", "POST"])
@login_required
def produce_product(id):
  """List all registered products."""
  db = get_db()
  
  if request.method == "GET":
    context = {}

    context['items'] = db.execute("""--sql
      SELECT id, item_name, amount, quantity_alert
      FROM items WHERE user_id = ?
      ORDER BY item_name ASC;""", (g.user['id'],)
    ).fetchall()

    context['products'] = db.execute("""--sql
      SELECT id, product_name, amount, quantity_alert, has_recipe
      FROM products WHERE id = ? AND user_id = ?
      ORDER BY products.product_name ASC;""", (id, g.user['id'],)
    ).fetchall()

    recipes = db.execute("""--sql
      SELECT *
      FROM recipes WHERE product_id = ? AND user_id = ?
      """, (id, g.user['id'],)
    ).fetchall()

    form = group_recipes({**context, 'recipes': recipes})[0]

    if not form:
      abort(404, description="Recipe not found.")

    return render_template("produce-product-detail.html", form=form)
  
  if request.method == "POST":
    form = {}
    items = []
    
    for field in request.form:
      if field == 'quantity_alert' or field == 'amount':
        form[field] = request.form[field]
      else:
        items.append({
          'id': field,
          'amount': request.form[field]
        })
    
    try:
      db.execute(
        """--sql
        UPDATE products SET
          quantity_alert = :quantity_alert, 
          amount = :amount
        WHERE id = :id AND user_id = :user_id
        """, {**form, 'id': id, 'user_id': g.user['id']}
      )

      for item in items:
        db.execute(
          """--sql
          UPDATE items SET
            amount = :amount
          WHERE id = :id AND user_id = :user_id
          """, {'id': item['id'], 'amount': item['amount'], 'user_id': g.user['id']}
        )
      
      db.commit()

      flash(f"Product restocked.#success", 'messages')
      return redirect(url_for("inflow.overview"))
    except db.IntegrityError as e:
      e = str(e)
      print("Error:", e)
      flash(f"Product not restocked!#danger", 'messages')
    return render_template("supply-item-detail.html", form=form)