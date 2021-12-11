import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField

from utils.models import BaseModel


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"

    uuid = models.UUIDField(
        "UUID", unique=True, default=uuid.uuid4, editable=False, primary_key=True
    )
    first_name = models.CharField("First Name", max_length=32)
    last_name = models.CharField("Last Name", max_length=32)
    country = CountryField("Country of Residence")
    national_id = models.CharField(
        "National ID Number", blank=True, null=True, max_length=32, unique=True
    )
    gender = models.CharField("Gender", max_length=6, choices=Gender.choices)
    date_of_birth = models.DateField("Date of Birth")
    email = models.EmailField("Email Address", unique=True)
    phone_number = PhoneNumberField("Phone Number")
    date_joined = models.DateTimeField("Date Joined", auto_now_add=True)
    is_active = models.BooleanField("Is Active", default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "country",
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
        return f"{self.first_name} {self.last_name}"
