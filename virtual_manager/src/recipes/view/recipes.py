import re
import json

from flask import Blueprint, flash, jsonify, redirect, render_template, request, g, url_for

from virtual_manager.db import get_db
from virtual_manager.src.auth.view.auth import login_required


def form_handle(product_id, request):
  recipes = []
  pattern = re.compile(r"^recipe(\d+)$")
  
  for key in request.form.keys():
    match = pattern.match(key)
    if match:
      index = match.group(1)
      values = request.form.getlist(f"recipe{index}")
      print('VALUES:', values)
    
      recipes.append({
        "id": int(values[0]),
        "user_id": int(g.user['id']),
        "product_id": int(product_id),
        "item_id": int(values[1].split(",")[0]),
        "item_amount": int(values[2])
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

  if request.method == "POST":
    recipes = form_handle(product_id, request)
    print('CREATE:', recipes)

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

  return render_template("recipe-detail.html", product=product, items=items)

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
    print('UPDATE:', recipes)

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

@bp.route("/delete-recipe", methods=["POST"])
@login_required
def delete_recipe():
  # TODO: Fix js del button logic
  db = get_db()
  # ids = request.form.get('recipe_ids', type=list)
  # for id in ids:
  #   db.execute("""--sql
  #     DELETE FROM recipes WHERE id = ? AND user_id = ?
  #   """, (id, g.user['id']))

  # db.execute("""--sql
  #     DELETE FROM recipes WHERE id = ? AND user_id = ?
  #   """, (recipe_id, g.user['id']))

  # db.commit()
  return redirect(url_for("recipes.overview"))

@bp.route("/recipe-inline", methods=["GET", "POST"])
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

  return render_template("recipe-inline.html", items=items)