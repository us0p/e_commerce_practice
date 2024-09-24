from .exceptions import MissingRequiredFields


def has_required_fields(required_fields: list[str], body: dict):
    missing_fields: list[str] = []

    for required_field in required_fields:
        field = body.get(required_field)
        if field is None:
            missing_fields.append(required_field)

    if len(missing_fields):
        raise MissingRequiredFields(missing_fields)
