import functools
from flask import Blueprint, flash, redirect, render_template, request, session, g, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from virtual_manager.db import get_db

def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))
    return view(**kwargs)

  return wrapped_view

def validate_registration_data(data):
  errors = {}
  db = get_db()
  
  if not data['username']:
    errors['username'] = 'Username is required.'
  else:
    # Verifies if username is taken. (This is a redundant measure.)
    user_exists = db.execute(
      "SELECT username FROM users WHERE username = ?", (data['username'],)
    ).fetchone()
    
    if user_exists:
      errors['username'] = 'Username is already taken.'
  # Verifies if passwords and confirmation matches.
  if not data['password']:
    errors['password'] = 'Password is required.'
  elif data['password'] != data['confirmation']:
    errors['confirmation'] = "Password confirmation doesn't match."
  
  return errors


bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../html', static_folder='../../auth')

@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')

  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()


@bp.route('/check-username', methods=('GET',))
def check_username():
  query = request.args.get('q')
  
  if query:
    username = get_db().execute("SELECT username FROM users WHERE username = ?", (query.lower(),)).fetchone()
    if username:
      return ('false', 'true')[query == username['username']]
    else:
      return 'false'

@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    form = request.form
    data = {
      'username': form.get('username').lower(),
      'password': form.get('password'),
      'confirmation': form.get('confirmation')
    }

    errors = validate_registration_data(data)

    if errors:
      for field, message in errors.items():
          flash(message, field)
      return render_template('register.html', data=data)
    
    try:
      db = get_db()
      data['password'] = generate_password_hash(data['password'])

      db.execute(
        "INSERT INTO users (username, hash) VALUES (:username, :password)",
        (data),
      )

      db.commit()
    except db.IntegrityError:
      flash(f"User {data['username']} is already registered.", 'username')
      return render_template('register.html', data=data)
    else:
      return redirect(url_for("auth.login"))
  else:
    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
  if request.method == 'POST':
    db = get_db()
    username = request.form['username']
    password = request.form['password']
    user = False
    hash = False
    errors = 0
    
    if not username:
      flash("Enter a username.", 'username')
      errors += 1
    else:
      user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    
    if not password :
      flash("Enter a password.", 'password')
      errors += 1
    
    if user:
      hash = check_password_hash(user['hash'], password)
    
    if user == None or hash == False:
      flash("Invalid username or password.", 'password')
      errors += 1
    elif not user['is_active']:
      flash("Contact an administrator.", 'password')
      errors += 1

    if errors:
      return redirect(url_for('auth.login'))
    else:
      session.clear()
      session['user_id'] = user['id']
      return redirect(url_for('index'))
  return render_template('login.html')


@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))