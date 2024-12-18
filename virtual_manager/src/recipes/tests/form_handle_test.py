import pytest
from flask import Flask, g, request

from src.recipes.view.recipes import form_handle


# Fixture to create a Flask application instance
@pytest.fixture()
def app():
  app = Flask(__name__)
  app.config.update({
    "TESTING": True,  # Enable testing mode for the application
  })
  return app

# Fixture to create a test client for the application
@pytest.fixture()
def client(app):
  return app.test_client()

# Test case for the `form_handle` function
def test_form_handle(app, client):
  # Simulate an application and request context with form data
  with app.test_request_context(
    data={
      "recipesIndex": 3,  # Index indicating the number of recipes
      "itemRecipe1": "101,Flour",  # First recipe item data
      "amountRecipe1": "2",  # First recipe item amount
      "recipeId1": "201",  # First recipe ID
      "itemRecipe2": "102,Sugar",  # Second recipe item data
      "amountRecipe2": "3",  # Second recipe item amount
      "recipeId2": "202",  # Second recipe ID
    }
  ):
    # Set the `g.user` global object to simulate an authenticated user
    g.user = {"id": 1}
    product_id = 10  # Product ID to be processed

    # Call the function to test its behavior
    index, recipes = form_handle(product_id, request)

    # Assert that the returned index matches the expected value
    assert index == 3

    # Define the expected recipes data
    expected_recipes = [
      {
        "user_id": 1,  # User ID from `g.user`
        "product_id": 10,  # Provided product ID
        "index": 1,  # Recipe index
        "id": 201,  # Recipe ID from form data
        "item_id": 101,  # Item ID parsed from form data
        "item_name": "Flour",  # Item name parsed from form data
        "item_amount": 2,  # Item amount from form data
      },
      {
        "user_id": 1,
        "product_id": 10,
        "index": 2,
        "id": 202,
        "item_id": 102,
        "item_name": "Sugar",
        "item_amount": 3,
      },
    ]

    # Assert that the returned recipes match the expected data
    assert recipes == expected_recipes
