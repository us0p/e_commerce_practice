from datetime import datetime
import json
import hashlib
from os import getenv

from django.core.exceptions import ValidationError
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)

import jwt

from .exceptions import MissingRequiredFields
from .utils import has_required_fields

from .models import Users


def create(req: HttpRequest):
    body = json.loads(req.body)
    try:
        has_required_fields(
            [
                "name",
                "email",
                "address",
                "phone",
                "password",
                "confirm_password",
            ],
            body,
        )

        if body["password"] != body["confirm_password"]:
            return HttpResponseBadRequest(
                json.dumps({"error": "passwords doesn't match"}).encode(
                    "utf-8"
                )
            )

        hashed_pass = hashlib.sha256()
        hashed_pass.update(str(body.get("password")).encode("utf-8"))

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
            json.dumps({"success": "user created"}).encode("utf-8"),
            status=201,
        )
    except MissingRequiredFields as e:
        return HttpResponseBadRequest(
            json.dumps(
                {"error": "missing required fields", "fields": e.fields}
            ).encode("utf-8")
        )
    except ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps(
                {
                    "error": "duplicated info error",
                    "info": [v[0] for v in e.message_dict.values()],
                }
            ).encode("utf-8")
        )


def get(_: HttpRequest, user_id: int):
    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return HttpResponseNotFound(
            json.dumps(
                {"error": f"user with ID {user_id} doesn't exist"}
            ).encode("utf-8")
        )

    return HttpResponse(json.dumps(user.get_public_info()).encode("utf-8"))


def login(req: HttpRequest):
    body = json.loads(req.body)
    if "email" not in body:
        return HttpResponseBadRequest(
            json.dumps({"error": "email is required"}).encode("utf-8")
        )

    if "password" not in body:
        return HttpResponseBadRequest(
            json.dumps({"error": "password is required"}).encode("utf-8")
        )

    hashed_pass = hashlib.sha256()
    hashed_pass.update(str(body["password"]).encode("utf-8"))

    try:
        user = Users.objects.get(
            email=body["email"], password=hashed_pass.hexdigest()
        )
    except Users.DoesNotExist:
        return HttpResponseNotFound(
            json.dumps({"error": "invalid credentials"}).encode("utf-8")
        )

    token = jwt.encode(
        user.get_public_info(),
        getenv("SECRET"),
        algorithm="HS256",
        headers={"exp": datetime.now().toordinal() + 7},
    )
    return HttpResponse(json.dumps({"token": token}).encode("utf-8"))
