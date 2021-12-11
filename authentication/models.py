from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from common.models import BaseModel, Entity
from common.constants import GENDERS


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, Entity, PermissionsMixin):
    GENDERS = BaseModel.preprocess_choices(GENDERS)

    first_name = models.CharField("First Name", max_length=32)
    surname = models.CharField("Last Name", max_length=32)
    national_id = models.CharField(
        "National ID Number", blank=True, null=True, max_length=32, unique=True
    )
    gender = models.CharField("Gender", choices=GENDERS, max_length=6)
    date_of_birth = models.DateField("Date of Birth")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "surname",
        "national_id",
        "gender",
        "date_of_birth",
        "phone_number",
    ]

    VALIDATION_FIELDS = [USERNAME_FIELD, "password"] + REQUIRED_FIELDS
    SERIALIZATION_FIELDS = (
        ["uuid", USERNAME_FIELD] + REQUIRED_FIELDS + ["date_joined", "is_active"]
    )

    class Meta:
        ordering = ["date_joined"]
        verbose_name = "user"
        verbose_name_plural = "users"

    @classmethod
    def create(cls, fields):
        return User.objects.create_user(**fields)

    def __str__(self) -> str:
        return f"{self.uuid}: {self.first_name} {self.surname}"
