from app import ma
from marshmallow import fields, validate

class CategoriaSchema(ma.Schema):
    """Schema para serializar y validar las Categorías."""
    id = fields.Int(dump_only=True)
    
    # El nombre es requerido y debe ser único
    nombre = fields.Str(required=True, validate=validate.Length(min=3, max=64)) 
    
    class Meta:
        load_instance = True