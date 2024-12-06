import re
import json

from flask import Blueprint, flash, jsonify, redirect, render_template, request, g, url_for

from virtual_manager.db import get_db
from virtual_manager.src.auth.view.auth import login_required


def form_handle(product_id, request):
  recipes = []
  recipe_names_pattern = re.compile(r"recipe(?!0)\d+")
  
  for key in request.form.keys():
    if recipe_names_pattern.match(key):
      values = request.form.getlist(key)
      
      recipes.append({
        "userId": int(g.user['id']),
        "productId": int(product_id),
        "recipeId": int(values[0]),
        "itemId": int(values[1].split(",")[0]),
        "itemAmount": int(values[2])
      })

  return recipes

bp = Blueprint('recipes', __name__, url_prefix='/recipes', template_folder='../html', static_folder='../../recipes', static_url_path='/')

@bp.route("/overview")
@login_required
def overview():
  """List all products with recipes"""
  db = get_db()
  db_recipes = db.execute(
    """--sql
    SELECT
      r.id,
      p.product_name,
      json_group_object(i.item_name, r.item_amount) AS items_list
    FROM recipes r
    INNER JOIN products p ON r.product_id = p.id
    INNER JOIN items i ON r.item_id = i.id
    WHERE r.user_id = ?
    GROUP BY p.product_name;
    """, (g.user['id'],)
  ).fetchall()

  recipes = []
  for db_recipe in db_recipes:
    
    recipe = {}
    for k in db_recipe.keys():
      if k == 'items_list':
        recipe[k] = json.loads(db_recipe['items_list'])
      else:
        recipe[k] = db_recipe[k]

    recipes.append(recipe)
  
  return render_template("recipes.html", recipes=recipes)


@bp.route("/create-recipe/<int:product_id>", methods=["GET", "POST"])
@login_required
def create_recipe(product_id):
  """Create recipes"""
  # TODO: Design GET and POST logic 
  db = get_db()
  product = db.execute("""--sql
    SELECT product_name, id FROM products
    WHERE has_recipe = 1 AND user_id = ? AND id = ?;
  """, (g.user['id'], product_id)).fetchone()
  
  items = db.execute("""--sql
    SELECT id, item_name FROM items
    WHERE user_id = ? ORDER BY item_name ASC;
  """, (g.user['id'],)).fetchall()
  
  if request.method == "POST":
    recipe = form_handle(product_id, request)

    db.execute(
        """--sql
        INSERT INTO recipes (user_id, product_id, item_id, item_amount)
        VALUES (:userId, :productId, :itemId, :itemAmount)
        """, (recipe)
      )

    db.commit()

  return render_template(f"create-recipe.html", product=product, items=items)
# TODO
@bp.route("/update-recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def update_recipe(recipe_id):
  db = get_db()
  items = db.execute("SELECT * FROM items WHERE user_id = ?;", (g.user['id'],)).fetchall()
  prod_id = db.execute("SELECT product_id FROM recipes WHERE user_id = ? AND id = ?;", (g.user['id'], recipe_id)).fetchone()['product_id']
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

@bp.route("/delete-recipe/<int:recipe_id>", methods=["POST"])
@login_required
def delete_recipe(recipe_id):
  db = get_db()
  # ids = request.form.get('recipe_ids', type=list)
  # for id in ids:
  #   db.execute("""--sql
  #     DELETE FROM recipes WHERE id = ? AND user_id = ?
  #   """, (id, g.user['id']))

  db.execute("""--sql
      DELETE FROM recipes WHERE id = ? AND user_id = ?
    """, (recipe_id, g.user['id']))

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