import json
import hashlib

from django.core.exceptions import ValidationError
from django.core.serializers import serialize
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)

from .models import Users


def create(req: HttpRequest):
    body = json.loads(req.body)
    if "confirm_password" not in body:
        return HttpResponseBadRequest(
            json.dumps({"error": "confirm_password is required"}).encode("utf-8")
        )
    if "password" not in body:
        return HttpResponseBadRequest(
            json.dumps({"error": "password is required"}).encode("utf-8")
        )

    if body["password"] != body["confirm_password"]:
        return HttpResponseBadRequest(
            json.dumps({"error": "password doesn't match"}).encode("utf-8")
        )

    hashed_pass = hashlib.sha256()
    hashed_pass.update(str(body.get("password")).encode("utf-8"))

    try:
        user = Users(
            name=body.get("name"),
            email=body.get("email"),
            address=body.get("address"),
            phone=body.get("phone"),
            password=hashed_pass.hexdigest(),
        )
        user.full_clean()
        user.save()

        return HttpResponse(
            json.dumps({"success": f"user id: {user.id} created"}).encode("utf-8"),
            status=201,
        )
    except ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps(
                {"errors": [f"{v[0]} {k}" for k, v in e.message_dict.items()]}
            ).encode("utf-8")
        )


def get(req: HttpRequest, user_id: int):
    user = Users.objects.filter(id=user_id)

    if user is None:
        return HttpResponseNotFound(
            json.dumps({"error": f"{user_id} doesn't exist"}).encode("utf-8")
        )

    return HttpResponse(serialize("json", user))
