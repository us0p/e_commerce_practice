from django.db import models
from .validators import validate_required


class Users(models.Model):

    class Meta:
        db_table = "users"

    id: models.BigAutoField
    name = models.CharField(validators=[validate_required])
    email = models.CharField(unique=True, validators=[validate_required])
    address = models.CharField(validators=[validate_required])
    phone = models.CharField(unique=True, validators=[validate_required])
    password = models.CharField(validators=[validate_required])
