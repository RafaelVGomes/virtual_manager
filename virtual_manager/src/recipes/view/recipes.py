import json

from flask import (Blueprint, Request, flash, g, redirect, render_template, request,
                   url_for)

from virtual_manager.src.auth.views import login_required
from virtual_manager.db import get_db


def form_handle(product_id: int, request: Request) -> tuple[int, list[dict]]:
  """
    Handles form data to parse recipes.

    Args:
      product_id (int): The ID of the product being processed.
      request (Request): The Flask request object containing form data.

    Returns:
      tuple[int, list[dict]]: A tuple containing the highest index found and a list of recipe dictionaries.
    """
  recipes = []
  form = request.form
  start_index = form.get("recipesIndex", type=int)
  
  for i in range(1, start_index):
    item_data = form.get(f"itemRecipe{i}")
    
    if not item_data:
      continue

    try:
      item_id, item_name = item_data.split(',')
      recipe = {
        "user_id": int(g.user['id']),
        "product_id": product_id,
        "index": i,
        "id": form.get(f"recipeId{i}", type=int),
        "item_id": int(item_id),
        "item_name": item_name,
        "item_amount": form.get(f"amountRecipe{i}", type=int)
      }
      recipes.append(recipe)
    except Exception as e:
      print(f"Error processing recipe index: {i} -> {e}")

  return start_index + 1, recipes
  
def validate_forms(recipes: list[dict]) -> bool:
  errors = {}

  for recipe in recipes:
    if not recipe['item_id']:
      errors[f"itemRecipe{recipe['index']}"] = "Select a item."

  for recipe in recipes:
    if not recipe['item_amount']:
      errors[f"amountRecipe{recipe['index']}"] = "Enter an amount."

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
    SELECT p.id AS product_id, p.product_name,
      json_group_array(
        json_object(
          'recipe_id', r.id,
          'name', r.item_name,
          'recipe_amount', r.item_amount
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

  recipes = []
  for db_recipe in db_recipes:
    recipe = {}
    for k in db_recipe.keys():
      if k == 'items_list':
        recipe[k] = json.loads(db_recipe[k])
        if recipe['items_list'][0]['recipe_id'] == None:
          recipe['items_list'] = [None]
      else:
        recipe[k] = db_recipe[k]

    recipes.append(recipe)
  
  return render_template("recipes.html", recipes=recipes)


@bp.route("/create-recipe/<int:product_id>", methods=["GET", "POST"])
@login_required
def create_recipe(product_id: int):
  """Create recipes"""
  db = get_db()
  context = {}

  context['product'] = db.execute("""--sql
    SELECT id, product_name FROM products
    WHERE has_recipe = 1 AND user_id = ? AND id = ?;
  """, (g.user['id'], product_id)).fetchone()
  
  context['items'] = db.execute("""--sql
    SELECT id, item_name FROM items
    WHERE user_id = ? ORDER BY item_name ASC;
  """, (g.user['id'],)).fetchall()

  context['index'] = 1
  context['recipes'] = []

  if request.method == "GET":
    return render_template("recipe-detail.html", **context)

  if request.method == "POST":
    context['index'], context['recipes'] = form_handle(product_id, request)
    
    if validate_forms(context['recipes']):
      try:
        for recipe in context['recipes']:
          db.execute(
            """--sql
            INSERT INTO recipes (user_id, product_id, item_id, item_amount)
            VALUES (:user_id, :product_id, :item_id, :item_amount)
            """, recipe
          )
        db.commit()

        flash(f"Recipe created.#success", 'messages')
        return redirect(url_for("recipes.overview"))
      except db.IntegrityError as e:
        e = str(e)
        print("Error:", e)
        flash(f"Recipe not created!#danger", 'messages')
        return render_template("recipe-detail.html", **context)
    else:
      return render_template("recipe-detail.html", **context)


@bp.route("/update-recipe/<int:product_id>", methods=["GET", "POST"])
@login_required
def update_recipe(product_id: int):
  db = get_db()
  context = {}

  context['product'] = db.execute("""--sql
    SELECT id, product_name FROM products
    WHERE has_recipe = 1 AND user_id = ? AND id = ?;
  """, (g.user['id'], product_id)).fetchone()
  
  context['items'] = db.execute("""--sql
    SELECT id, item_name FROM items
    WHERE user_id = ? ORDER BY item_name ASC;
  """, (g.user['id'],)).fetchall()

  db_recipes = db.execute("""--sql
    SELECT id, item_id, item_amount FROM recipes
    WHERE user_id = ? AND product_id = ?;
  """, (g.user['id'], product_id)).fetchall()

  context['index'] = len(db_recipes) + 1
  
  context['recipes'] = []

  for recipe in db_recipes:
    recipe = dict(recipe)
    
    for item in context['items']:
      if recipe['item_id'] == item['id']:
        recipe['item_name'] = item['item_name']
    
    context['recipes'].append(recipe)

  if request.method == "GET":
    return render_template("recipe-detail.html", **context)
  
  if request.method == "POST":
    context['index'], context['recipes'] = form_handle(product_id, request)
    for recipe in context['recipes']:
      print('UPDATE:', recipe)

    if validate_forms(context['recipes']):
      try:
        for recipe in context['recipes']:
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

        flash(f"Recipe updated.#success", 'messages')
        return redirect(url_for("recipes.overview"))
      except db.IntegrityError as e:
        e = str(e)
        print("Error:", e)
        flash(f"Recipe not updated!#danger", 'messages')
        return render_template("recipe-detail.html", **context)
    else:
      return render_template("recipe-detail.html", **context)
  

@bp.route("/delete-recipe/<int:id>", methods=["POST"])
@login_required
def delete_recipe(id: int):
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
