from django.core.exceptions import ValidationError


def validate_required(value):
    if value is None:
        raise ValidationError("field is required")
