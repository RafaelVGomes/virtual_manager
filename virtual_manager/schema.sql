-- database: ../instance/project.sqlite

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  hash TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_users_is_active ON users (is_active);

CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  item_name TEXT NOT NULL,
  amount NUMERIC NOT NULL DEFAULT 0,
  measure TEXT NOT NULL,
  quantity_alert INTEGER NOT NULL DEFAULT 0,
  price REAL NOT NULL DEFAULT 0.0,
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  UNIQUE (user_id, item_name)
);
CREATE INDEX idx_item_user ON items (user_id, item_name);


CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  product_name TEXT NOT NULL,
  amount NUMERIC NOT NULL DEFAULT 0,
  measure TEXT NOT NULL,
  quantity_alert INTEGER DEFAULT 0,
  price REAL NOT NULL DEFAULT 0.0,
  has_recipe INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  UNIQUE (user_id, product_name)
);
CREATE INDEX idx_product_user ON products (user_id, product_name);

CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  item_id INTEGER,
  item_amount NUMERIC NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE SET NULL,
  UNIQUE (user_id, product_id, item_id)
);
CREATE INDEX idx_recipe_user ON recipes (user_id, product_id, item_id);
CREATE INDEX idx_recipe_product ON recipes (product_id);
CREATE INDEX idx_recipe_item ON recipes (item_id);
CREATE TRIGGER remove_recipes_on_has_recipe_change
AFTER UPDATE OF has_recipe ON products
FOR EACH ROW
WHEN NEW.has_recipe = 0
BEGIN
  DELETE FROM recipes WHERE product_id = NEW.id;
END;
