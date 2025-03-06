class BaseField:
  """Base class for all model fields."""
  def __init__(self, required=False, default=None, unique=False, html_type=None, **attrs):
    self.required = required
    self.default = default
    self.unique = unique
    self.html_type = html_type
    self.attrs = attrs  # Additional attributes (e.g., min, max, step)

  def to_html(self, name):
    """Generates an HTML input element for the field."""
    required = "required" if self.required else ""
    attrs = " ".join(f'{key}="{value}"' for key, value in self.attrs.items())
    return f'<input type="{self.html_type}" name="{name}" {required} {attrs}>'


class IntegerField(BaseField):
  """Integer field for model definitions."""
  def __init__(self, primary_key=False, **kwargs):
    super().__init__(**kwargs)
    self.primary_key = primary_key
    self.html_type = "number"


class StringField(BaseField):
  """String field with optional max length."""
  def __init__(self, max_length=255, **kwargs):
    super().__init__(**kwargs)
    self.max_length = max_length
    self.html_type = kwargs.get("html_type", "text")


class BooleanField(BaseField):
  """Boolean field, represented as a checkbox in HTML."""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.html_type = "checkbox"
