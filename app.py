import os
from virtual_manager import create_app

app = create_app()

if __name__ == "__main__":
  debug_mode = os.getenv("FLASK_ENV") == "development"
  print(f"{debug_mode=}")
  app.run(debug=debug_mode)