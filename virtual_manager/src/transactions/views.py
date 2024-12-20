


def validate_form(form):
  errors = {}

  if not form['product_name']:
    errors['product_name'] = "Please enter a name for this product."

  try:
    if form['amount'] is None or form['amount'] < 0:
      errors['amount'] = "Please enter a valid positive number."
  except ValueError:
    errors['amount'] = "Invalid amount. Must be a number."
    
  if not form['measure']:
    errors['measure'] = "Please select a measure."
  elif form['measure'] not in ['kg', 'L', 'pcs']:
    errors['measure'] = "Invalid measure."

  try:
    if form['quantity_alert'] is None or form['quantity_alert'] < 0:
      errors['quantity_alert'] = "Please enter a valid positive number."
  except ValueError:
    errors['quantity_alert'] = "Invalid quantity alert. Must be a number."

  if not form['price']:
    errors['price'] = "Please enter a price."

  if form['has_recipe'] not in [0, 1]:
    errors['has_recipe'] = "Invalid option."

  if errors:
    flash('Fill all required fields!#warning', 'messages')
    for field, message in errors.items():
      print(f"{field}: {message}")
      flash(message, field)
    return False
  else:
    return True