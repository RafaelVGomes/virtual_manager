-- database: ../instance/virtual_manager.sqlite
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  hash TEXT NOT NULL,
  is_active INTEGER DEFAULT 1
);
CREATE INDEX idx_users ON users (id, username, is_active);


CREATE TABLE items (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  item_name TEXT NOT NULL UNIQUE,
  amount NUMERIC NOT NULL DEFAULT 0,
  measure TEXT NOT NULL,
  quantity_alert INTEGER NOT NULL DEFAULT 0,
  price NUMERIC  DEFAULT 0,
  is_product INTEGER NOT NULL DEFAULT 0,
  sale_price NUMERIC DEFAULT "-",
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX idx_items ON items (id, item_name, is_product);


CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  product_name TEXT NOT NULL UNIQUE,
  amount NUMERIC NOT NULL,
  measure TEXT NOT NULL,
  quantity_alert INTEGER,
  price NUMERIC NOT NULL,
  has_recipe INTEGER NOT NULL
);
CREATE INDEX idx_product ON products (id, product_name);


CREATE TABLE recipes (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  item_id INTEGER NOT NULL,
  item_amount NUMERIC NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);
CREATE INDEX idx_recipes ON recipes (id, user_id, product_id, item_id);
