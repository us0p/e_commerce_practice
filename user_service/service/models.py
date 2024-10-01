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

    objects = models.Manager()
    # https://github.com/typeddjango/django-stubs/issues/1684#issuecomment-1929132279
    # https://docs.djangoproject.com/en/4.2/topics/db/managers/#manager-names

    def get_public_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone": self.phone,
        }
