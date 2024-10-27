import re

from flask import Blueprint, flash, jsonify, redirect, render_template, request, g, url_for

from virtual_manager.db import get_db
from virtual_manager.helpers import camelCase, form_handle
from virtual_manager.src.auth.view.auth import login_required


bp = Blueprint('recipes', __name__, url_prefix='/recipes', template_folder='../html', static_folder='../../recipes', static_url_path='/')

@bp.route("/overview")
@login_required
def overview():
  """List all products with recipes"""
  db = get_db()
  products = db.execute(
    """--sql
    SELECT id, product_name FROM products
    WHERE has_recipe = 1 AND user_id = ?;
    """, (g.user['id'],)
  ).fetchall()

  recipes = db.execute(
    """--sql
    SELECT DISTINCT product_id, r.id, item_id, item_amount, i.item_name FROM recipes r
    INNER JOIN items i ON i.id = r.item_id
    WHERE r.user_id = ?;
    """, (g.user['id'],)
  ).fetchall()

  # for p in products:
  #   print(p)
  
  data = {}
  for product in products:
    if product['id'] not in data.keys():
      data[product['id']] = {
        'productName': product['product_name'],
        'recipe': [],
        'recipe_ids': ""
      }
    for recipe in recipes:
      if recipe['product_id'] == product['id']:
        data[recipe['product_id']]['recipe'].append((recipe['item_name'], recipe['item_amount']))
        data[recipe['product_id']]['recipe_ids'] += str(recipe['id'])

  # print(pprint(data))

  # return render_template("tests.html", data=data)
  return render_template("recipes.html", data=data)


@bp.route("/create-recipe/<int:id>", methods=["GET", "POST"])
@login_required
def create_recipe(id):
  """Create recipes"""
  # TODO: Design GET and POST logic 
  db = get_db()
  product = db.execute("SELECT product_name, id FROM products WHERE has_recipe = 1 AND user_id = ? AND id = ?;", (g.user['id'], id)).fetchone()
  items = db.execute("SELECT id, item_name FROM items WHERE user_id = ? ORDER BY item_name ASC;", (g.user['id'],)).fetchall()
  
  if request.method == "POST":
    recipesData = {
      # 'recipes': [],
      # 'inlineFormsTotal': request.form.get("inlineFormsTotal", type=int),
      'recipesIndex': request.form.get("recipesIndex", type=int),
      'errors': 0
    }

    form_handle(id, request)

  return render_template(f"create-recipe.html", product=product, items=items)
# TODO
@bp.route("/update-recipe/<int:id>", methods=["GET", "POST"])
@login_required
def update_recipe(id):
  db = get_db()
  items = db.execute("SELECT * FROM items WHERE user_id = ?;", (g.user['id'],)).fetchall()
  prod_id = db.execute("SELECT product_id FROM recipes WHERE user_id = ? AND id = ?;", (g.user['id'], id)).fetchone()['product_id']
  product = db.execute("SELECT product_name FROM products WHERE user_id = ? AND id = ?;", (g.user['id'], prod_id)).fetchone()
  recipes = db.execute("SELECT * FROM recipes WHERE user_id = ? AND product_id = ?;", (g.user['id'], prod_id)).fetchall()
  recipesData = {
    'recipes': []
  }

  for i in range(0, len(recipes)):
    item = {
      f"recipeId": i
    }

    for recipe in recipes[i].keys():
      item[recipe] = recipes[i][recipe]
    recipesData['recipes'].append(item)
  
  print(recipesData['recipes'])


  if request.method == "POST":
    pass

  return render_template(f"update-recipe.html", product=product, items=items, recipesData=recipesData) # , recipesData=recipesData

@bp.route("/delete-recipe", methods=["POST"])
@login_required
def delete_recipe():
  db = get_db()
  ids = request.form.get('recipe_ids', type=list)
  for id in ids:
    db.execute("""--sql
      DELETE FROM recipes WHERE id = ? AND user_id = ?
    """, (id, g.user['id']))

  db.commit()
  return redirect(url_for("recipes.overview"))

@bp.route("/create-recipe-inline", methods=["GET", "POST"])
@login_required
def create_recipe_inline():
  """Create recipe as inline form"""
  db = get_db()
  items = db.execute("SELECT id, item_name FROM items WHERE user_id = ?;", (g.user['id'],)).fetchall()
  if request.method == "POST":
    print('json:', request.get_json(force=True))
    print('RECIPE method:', request.method)
    return jsonify("RECIPE POSTED!")
  
    # recipe_names_pattern = re.compile(r"recipe[0-9]+")
    # for key in request.form.keys():
    #   if recipe_names_pattern.match(key) and key != 'recipe0':
    #     print(key, request.form.getlist(key))
        # form['recipes'].append(request.form.getlist(key))

    # for i in range(data['inline_total']):
    #   inline_forms = request.form.getlist(f"recipe_items_{i}")
    #   id_and_name = inline_forms[0].split(',')
    #   item_id = id_and_name[0]
    #   item_name = id_and_name[1]
    #   item_amount = inline_forms[1]

    #   db.execute("INSERT INTO recipes (product_id, item_id, item_name, amount) VALUES (?,?,?,?)", product_id, item_id, item_name, item_amount)
    #   db.execute("UPDATE items SET amount = items.amount - ? WHERE id = ?", round(data['amount'] * item_amount, 1), item_id)

  return render_template("create-recipe-inline.html", items=items)