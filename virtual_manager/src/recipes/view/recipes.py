import re
import json

from flask import Blueprint, flash, jsonify, redirect, render_template, request, g, url_for

from virtual_manager.db import get_db
from virtual_manager.src.auth.view.auth import login_required


def form_handle(product_id, request):
  errors = {}
  recipes = []
  pattern = re.compile(r"^recipe([1-9]\d*)$")
  
  for key in request.form.keys():
    match = pattern.match(key)
    if match:
      index = match.group(1)
      values = request.form.getlist(f"recipe{index}")
      print('HANDLER:', values)
      
      recipe = {
        "index": index,
        "user_id": int(g.user['id']),
        "product_id": int(product_id),
        "id": int(values[0]),
        "item_id": int(values[1].split(",")[0]),
        "item_amount": int(values[2])
      }

      recipes.append(recipe)

  return recipes
  
def validate_forms(recipes):
  errors = {}

  for recipe in recipes:
    if not recipe['item_id']:
      errors[f"itemRecipe{recipe['index']}"] = "Select a item."

  if errors:
    for field, message in errors.items():
      print(f"{field}: {message}")
      flash(message, field)
    return False
  else:
    return True


bp = Blueprint('recipes', __name__, url_prefix='/recipes', template_folder='../html', static_folder='../../recipes', static_url_path='/')

@bp.route("/overview")
@login_required
def overview():
  """List all products with recipes"""
  db = get_db()
  db_recipes = db.execute(
    """--sql
    SELECT
      p.id AS product_id,
      p.product_name,
      json_group_array(
        CASE
          WHEN r.id IS NOT NULL THEN
            json_object(
              'recipe_id', r.id,
              'name', i.item_name,
              'recipe_amount', r.item_amount
            )
          ELSE NULL
        END
      ) AS items_list
    FROM products p
    LEFT JOIN recipes r ON r.product_id = p.id AND r.user_id = ?
    LEFT JOIN items i ON r.item_id = i.id
    WHERE p.has_recipe = 1 AND p.user_id = ?
    GROUP BY p.id, p.product_name;
    """, (g.user['id'], g.user['id'])
  ).fetchall()

  recipes = []
  for db_recipe in db_recipes:
    
    recipe = {}
    for k in db_recipe.keys():
      if k == 'items_list':
        recipe[k] = json.loads(db_recipe[k])
      else:
        recipe[k] = db_recipe[k]

    recipes.append(recipe)
  
  return render_template("recipes.html", recipes=recipes)


@bp.route("/create-recipe/<int:product_id>", methods=["GET", "POST"])
@login_required
def create_recipe(product_id):
  """Create recipes"""
  db = get_db()
  product = db.execute("""--sql
    SELECT id, product_name FROM products
    WHERE has_recipe = 1 AND user_id = ? AND id = ?;
  """, (g.user['id'], product_id)).fetchone()
  
  items = db.execute("""--sql
    SELECT id, item_name FROM items
    WHERE user_id = ? ORDER BY item_name ASC;
  """, (g.user['id'],)).fetchall()

  recipes = []

  if request.method == "GET":
    return render_template("recipe-detail.html", product=product, items=items)

  if request.method == "POST":
    recipes = form_handle(product_id, request)
    
    if validate_forms(recipes):
      try:
        for recipe in recipes:
          db.execute(
            """--sql
            INSERT INTO recipes (user_id, product_id, item_id, item_amount)
            VALUES (:user_id, :product_id, :item_id, :item_amount)
            """, recipe
          )
        db.commit()

        flash(f"Recipe created!#success", 'messages')
        return redirect(url_for("recipes.overview"))
      except db.IntegrityError as e:
        e = str(e)
        print("Error:", e)
        flash(f"Recipe not created!#danger", 'messages')
        return render_template("recipe-detail.html", product=product, items=items, recipes=recipes)
    else:
      return render_template("recipe-detail.html", product=product, items=items, recipes=recipes)


@bp.route("/update-recipe/<int:product_id>", methods=["GET", "POST"])
@login_required
def update_recipe(product_id):
  db = get_db()
  product = db.execute("""--sql
    SELECT id, product_name FROM products
    WHERE has_recipe = 1 AND user_id = ? AND id = ?;
  """, (g.user['id'], product_id)).fetchone()
  
  items = db.execute("""--sql
    SELECT id, item_name FROM items
    WHERE user_id = ? ORDER BY item_name ASC;
  """, (g.user['id'],)).fetchall()

  db_recipes = db.execute("""--sql
    SELECT id, item_id, item_amount FROM recipes
    WHERE user_id = ? AND product_id = ?;
  """, (g.user['id'], product_id)).fetchall()

  recipes = []
  for recipe in db_recipes:
    recipes.append(dict(recipe))
  
  if request.method == "POST":
    recipes = form_handle(product_id, request)
    for recipe in recipes:
      print('UPDATE:', recipe)

    try:
      for recipe in recipes:
        if recipe['id'] > 0:
          db.execute(
            """--sql
            UPDATE recipes
              SET 
                item_id = :item_id,
                item_amount = :item_amount
              WHERE id = :id
            """, recipe
          )
        else:
          db.execute(
          """--sql
          INSERT INTO recipes (user_id, product_id, item_id, item_amount)
          VALUES (:user_id, :product_id, :item_id, :item_amount)
          """, recipe
        )
      db.commit()

      flash(f"Recipe updated!#success", 'messages')
      return redirect(url_for("recipes.overview"))
    except db.IntegrityError as e:
      e = str(e)
      print("Error:", e)
      flash(f"Recipe not updated!#danger", 'messages')

      return render_template("recipe-detail.html", product=product, items=items, recipes=recipes)

  return render_template("recipe-detail.html", product=product, items=items, recipes=recipes)

@bp.route("/delete-recipe/<int:id>", methods=["POST"])
@login_required
def delete_recipe(id):
  db = get_db()

  try:
    db.execute("""--sql
      DELETE FROM recipes WHERE id = ? AND user_id = ?
    """, (id, g.user['id']))
    db.commit()
    return '', 200
  except db.IntegrityError as e:
    e = str(e)
    print("Error:", e)
    return '', 500
