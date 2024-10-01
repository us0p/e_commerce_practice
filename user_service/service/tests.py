import hashlib
import json
import unittest

from django.test import TestCase, RequestFactory
from django.urls import reverse

from .models import Users
from .views import create, get, login
from .utils import has_required_fields
from .exceptions import MissingRequiredFields


class TestHasRequiredFields(unittest.TestCase):
    def test_has_required_fields_fail(self):
        try:
            has_required_fields(
                ["name", "email", "phone", "password"],
                {"name": "test", "phone": "1234"},
            )
            raise Exception(
                "Should have failed with MissingRequiredFields"
            )
        except MissingRequiredFields as e:
            self.assertEqual(e.fields, ["email", "password"])


class TestCreate(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_unique_constraint_validations(self):
        body = {
            "name": "test",
            "email": "test@mail.com",
            "address": "test",
            "phone": "test",
            "password": "1234",
            "confirm_password": "1234",
        }

        mock_user_req = self.factory.post(
            path=reverse("service:create"),
            data=json.dumps(body).encode("utf-8"),
            content_type="application/json",
        )
        create(mock_user_req)
        duplicated_user_res = create(mock_user_req)
        self.assertEqual(
            json.loads(duplicated_user_res.content),
            {
                "error": "duplicated info error",
                "info": [
                    "Users with this Email already exists.",
                    "Users with this Phone already exists.",
                ],
            },
        )

    def test_user_created(self):
        req = self.factory.post(
            path=reverse("service:create"),
            data=json.dumps(
                {
                    "name": "test",
                    "email": "test@mail.com",
                    "address": "test",
                    "phone": "test",
                    "password": "1234",
                    "confirm_password": "1234",
                }
            ).encode("utf-8"),
            content_type="application/json",
        )

        res = create(req)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(
            res.content,
            json.dumps({"success": "user created"}).encode("utf-8"),
        )

        created_user = Users._default_manager.get(email="test@mail.com")
        if created_user is None:
            raise Exception("user wasn't stored to the database.")

        hashed_pass = hashlib.sha256()
        hashed_pass.update(b"1234")

        self.assertEqual(created_user.password, hashed_pass.hexdigest())

    def test_passwords_matching(self):
        req = self.factory.post(
            path=reverse("service:create"),
            data=json.dumps(
                {
                    "name": "test",
                    "email": "test@mail.com",
                    "address": "test",
                    "phone": "test",
                    "password": "1234",
                    "confirm_password": "4321",
                }
            ).encode("utf-8"),
            content_type="application/json",
        )

        res = create(req)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            json.loads(res.content), {"error": "passwords doesn't match"}
        )

    def test_required_fieds(self):
        req_bodies = [
            {
                "body": {
                    "email": "test@mail.com",
                    "address": "test",
                    "phone": "12345678",
                    "password": "test",
                    "confirm_password": "test",
                },
                "field_missing": "name",
            },
            {
                "body": {
                    "name": "test",
                    "address": "test",
                    "phone": "12345678",
                    "password": "test",
                    "confirm_password": "test",
                },
                "field_missing": "email",
            },
            {
                "body": {
                    "name": "test",
                    "email": "test@mail.com",
                    "phone": "12345678",
                    "password": "test",
                    "confirm_password": "test",
                },
                "field_missing": "address",
            },
            {
                "body": {
                    "name": "test",
                    "email": "test@mail.com",
                    "address": "test",
                    "password": "test",
                    "confirm_password": "test",
                },
                "field_missing": "phone",
            },
            {
                "body": {
                    "name": "test",
                    "email": "test@mail.com",
                    "address": "test",
                    "phone": "12345678",
                    "confirm_password": "test",
                },
                "field_missing": "password",
            },
            {
                "body": {
                    "name": "test",
                    "email": "test@mail.com",
                    "address": "test",
                    "phone": "12345678",
                    "password": "test",
                },
                "field_missing": "confirm_password",
            },
        ]

        for req in req_bodies:
            request = self.factory.post(
                path=reverse("service:create"),
                data=json.dumps(req["body"]).encode("utf-8"),
                content_type="application/json",
            )
            res = create(request)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(
                json.loads(res.content),
                {
                    "error": "missing required fields",
                    "fields": [req["field_missing"]],
                },
            )


class TestGetUser(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_unexisting_user(self):
        request = self.factory.get(path=reverse("service:get", args=(2,)))
        res = get(request, 3)  # created entries are deleted after each
        # TestCase execution, previous TestCase created 2 Users, that's
        # why we search for user_id 3.

        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            res.content,
            json.dumps({"error": "user with ID 3 doesn't exist"}).encode(
                "utf-8"
            ),
        )

    def test_get_user(self):
        mock_user = Users(
            name="test",
            email="test@mail.com",
            address="test address",
            phone="12345678",
            password="-9823yna;kdfjbhasd8y23",
        )

        mock_user.save()
        request = self.factory.get(path=reverse("service:get", args=(1,)))
        res = get(request, 3)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.content,
            json.dumps(mock_user.get_public_info()).encode("utf-8"),
        )


class TestLogin(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_required_fieds(self):
        req_bodies = [
            {
                "body": {
                    "email": "test@mail.com",
                },
                "field_missing": "password",
            },
            {
                "body": {
                    "password": "test",
                },
                "field_missing": "email",
            },
        ]

        for req in req_bodies:
            request = self.factory.post(
                path=reverse("service:login"),
                data=json.dumps(req["body"]).encode("utf-8"),
                content_type="application/json",
            )
            res = login(request)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(
                json.loads(res.content),
                {
                    "error": "missing required fields",
                    "fields": [req["field_missing"]],
                },
            )

    def test_invalid_credentials(self):
        request = self.factory.post(
            path=reverse("service:login"),
            data=json.dumps(
                {"email": "test@mail.com", "password": "1234"}
            ).encode("utf-8"),
            content_type="application/json",
        )
        res = login(request)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            res.content,
            json.dumps({"error": "invalid credentials"}).encode("utf-8"),
        )

    def test_login_user(self):
        create_user_request = self.factory.post(
            path=reverse("service:create"),
            data=json.dumps(
                {
                    "name": "test",
                    "email": "test@mail.com",
                    "address": "test",
                    "phone": "test",
                    "password": "1234",
                    "confirm_password": "1234",
                }
            ).encode("utf-8"),
            content_type="application/json",
        )
        create(create_user_request)

        login_request = self.factory.post(
            path=reverse("service:login"),
            data=json.dumps(
                {"email": "test@mail.com", "password": "1234"}
            ).encode("utf-8"),
            content_type="application/json",
        )
        res = login(login_request)
        body = json.loads(res.content)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(body.get("token"))
