from copy import deepcopy
from typing import Literal, Optional, TypedDict, Union

from flask import Request, abort, flash, g

from virtual_manager.db import DatabaseManager

class Attrs(TypedDict, total=False):
  min: int
  step: int

class FormField(TypedDict):
  name: str
  value: Union[str | int | float]
  type: Optional[Literal['text', 'number']]
  attrs: Optional[Attrs]

FORM_DATA: list[FormField] = [
  {
  'name': 'item_name',
  'value': '',
  'type': 'text'
  },
  {
    'name': 'amount',
    'value': 0,
    'type': 'number',
    'attrs': {'min':"0"}
  },
  {
    'name': 'measure',
    'type': None,
    'value': ''
  },
  {
    'name': 'quantity_alert',
    'value': 0,
    'type': 'number',
    'attrs': {'min':"0"}
  },
  {
    'name': 'price',
    'value': 0.0,
    'type': 'number',
    'attrs': {'step':"0.01", 'min':"0"}
  }
]

exclude = ['amount', 'price', 'quantity_alert']

def get_form(id: Optional[int]=None, request: Optional[Request]=None, exclude: Optional[list[str]]=exclude) -> list[FormField]:
  form = []
  
  if exclude:
    form = [field for field in deepcopy(FORM_DATA) if field['name'] not in exclude]
  else:
    form = [field for field in deepcopy(FORM_DATA)]

  if request:
    id = request.view_args.get('id')
    for field in form:
      if field['name'] not in exclude:
        if field['type'] == 'text':
          field['value'] = request.form.get(field['name']).lower()
        elif field['type'] == None:
          field['value'] = request.form.get(field['name'])
        elif field['type'] == 'number' and 'step' in field['attrs'].keys():
          field['value'] = request.form.get(field['name'], type=float)
        else:
          field['value'] = request.form.get(field['name'], type=int)
  elif id:
    db = DatabaseManager().connect()
    fields = [field['name'] for field in form]
    fields = ', '.join(fields)
    query = f"SELECT {fields} FROM items WHERE id = ? AND user_id = ?;"
    item = db.execute(query, (id, g.user['id'])).fetchone()

    if not item:
      abort(404, description="Item not found or you do not have permission to access it.")
    
    item_data = dict(item)
    
    for field in form:
      for key, value in item_data.items():
        if field['name'] == key:
          field['value'] = value
  
  if id:
    form.append({
      'name': 'id',
      'type': 'number',
      'value': int(id)
    })
  
  return form

def validate_form(form: list[FormField]) -> bool:
  """Validate item form."""
  errors = {}

  for field in form:
    if field['name'] == 'item_name' and not field['value']:
      errors['item_name'] = "Please enter a name for this item."

    if field['name'] == 'amount' and not (field['value'] or field['value'] <= 0):
      errors['amount'] = "Amount must be greater than zero."

    if field['name'] == 'measure' and not field['value']:
      errors['measure'] = "Please select a measure."
    elif field['name'] == 'measure' and field['value'] not in ['kg', 'L', 'pcs']:
      errors['measure'] = "Invalid measure."

    if field['name'] == 'quantity_alert' and not (field['value'] or field['value'] < 0):
      errors['quantity_alert'] = "Quantity alert must be zero or greater."

    if field['name'] == 'price' and not field['value']:
      errors['price'] = "Price must be zero or greater."

  if errors:
    flash('Fill all required fields!#warning', 'messages')
    for field, message in errors.items():
      flash(message, field)
    return False
  return True

def get_data_to_save(form: list[FormField]) -> dict:
  flat_form = {field['name']: field['value'] for field in form}
  flat_form['user_id'] = g.user['id']
  return flat_form