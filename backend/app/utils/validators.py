from marshmallow import Schema, fields, validate, validates, ValidationError


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    org_name = fields.Str(validate=validate.Length(max=200))

    @validates("password")
    def validate_password_strength(self, value, **kwargs):
        if not any(c.isupper() for c in value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise ValidationError("Password must contain at least one digit.")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class AlertRuleSchema(Schema):
    route = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    airline = fields.Str(validate=validate.Length(max=100), allow_none=True, load_default=None)
    condition = fields.Str(
        required=True,
        validate=validate.OneOf(["price_below", "price_above", "demand_spike"]),
    )
    threshold_value = fields.Float(required=True, validate=validate.Range(min=0))
    is_active = fields.Bool(load_default=True)


class AlertRuleUpdateSchema(Schema):
    route = fields.Str(validate=validate.Length(min=3, max=100))
    airline = fields.Str(validate=validate.Length(max=100), allow_none=True)
    condition = fields.Str(
        validate=validate.OneOf(["price_below", "price_above", "demand_spike"]),
    )
    threshold_value = fields.Float(validate=validate.Range(min=0))
    is_active = fields.Bool()


class RouteQuerySchema(Schema):
    origin = fields.Str(validate=validate.Length(max=50))
    destination = fields.Str(validate=validate.Length(max=50))
    airline = fields.Str(validate=validate.Length(max=100))
    date_from = fields.Date()
    date_to = fields.Date()
    sort_by = fields.Str(
        validate=validate.OneOf(["price", "demand_score", "origin", "destination"]),
        load_default="demand_score",
    )
    order = fields.Str(validate=validate.OneOf(["asc", "desc"]), load_default="desc")
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)


class ProfileUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    notification_email = fields.Email(allow_none=True)
    webhook_url = fields.Url(allow_none=True)
    watched_routes = fields.List(fields.Str(validate=validate.Length(max=100)))


class ExportPDFSchema(Schema):
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    routes = fields.List(fields.Str(), load_default=[])
    include_forecast = fields.Bool(load_default=False)
