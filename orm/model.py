from orm.fields import BaseField
from virtual_manager.db import DatabaseManager

class ModelMeta(type):
  """Metaclass to process model fields."""
  def __new__(cls, name, bases, dct):
    fields = {k: v for k, v in dct.items() if isinstance(v, BaseField)}
    dct['_fields'] = fields
    return super().__new__(cls, name, bases, dct)


class Model(metaclass=ModelMeta):
  """Base model class for ORM."""
  _db = DatabaseManager()

  def __init__(self, **kwargs):
    for field_name, field in self._fields.items():
      value = kwargs.get(field_name, field.default)
      setattr(self, field_name, value)
  
  def save(self):
    """Inserts or updates the record in the database."""
    fields = ', '.join(self._fields.keys())
    values = tuple(getattr(self, field) for field in self._fields)
    placeholders = ', '.join(['?' for _ in self._fields])
    
    query = f"INSERT INTO {self.__class__.__name__.lower()} ({fields}) VALUES ({placeholders})"
    self._db.execute(query, values)
    self._db.commit()

  @classmethod
  def filter(cls, **conditions):
    """Filters records based on provided conditions."""
    where_clause = ' AND '.join(f"{k} = ?" for k in conditions.keys())
    query = f"SELECT * FROM {cls.__name__.lower()} WHERE {where_clause}"
    return cls._db.execute(query, tuple(conditions.values())).fetchall()

  def delete(self):
    """Deletes the record from the database."""
    primary_key = next((k for k, v in self._fields.items() if hasattr(v, 'primary_key') and v.primary_key), None)
    if not primary_key:
      raise ValueError("No primary key found for delete operation.")
    query = f"DELETE FROM {self.__class__.__name__.lower()} WHERE {primary_key} = ?"
    self._db.execute(query, (getattr(self, primary_key),))
    self._db.commit()
