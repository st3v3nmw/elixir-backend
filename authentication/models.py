"""This module houses models for the authentication app."""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from common.constants import GENDERS
from common.models import BaseModel, Entity


class CustomUserManager(BaseUserManager):
    """Manager for User model."""

    use_in_migrations = True

    def create_user(self, email, password, **kwargs):
        """Instantiate User model."""
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, Entity, PermissionsMixin):
    """User model."""

    GENDERS = BaseModel.preprocess_choices(GENDERS)

    first_name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    national_id = models.CharField(null=True, max_length=32, unique=True)
    gender = models.CharField(choices=GENDERS, max_length=6)
    date_of_birth = models.DateField()
    relatives = models.ManyToManyField(
        "self",
        through="NextOfKin",
        through_fields=("user", "next_of_kin"),
    )

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

    POST_REQUIRED_FIELDS = [USERNAME_FIELD, "password"] + REQUIRED_FIELDS
    SERIALIZATION_FIELDS = (
        ["uuid", USERNAME_FIELD]
        + REQUIRED_FIELDS
        + ["address", "records", "relatives", "date_joined", "is_active"]
    )

    class Meta:  # noqa
        ordering = ["-date_joined"]

    @property
    def full_name(self) -> str:
        """Return the User's full name."""
        return f"{self.first_name} {self.surname}"

    def __str__(self) -> str:
        """Return string representation of User."""
        return f"{self.first_name} {self.surname} ({self.uuid})"

    def fhir_serialize(self):
        """Serialize self as a Patient FHIR resource."""
        contacts = []
        for relative in self.relatives:
            contacts.append(
                {
                    "relationship": relative.relationship,
                    "name": relative.full_name,
                    "telecom": {"system": "phone", "value": self.phone_number},
                    "gender": relative.gender,
                }
            )

        return {
            "resourceType": "Patient",
            "identifier": [self.uuid],
            "active": self.is_active,
            "name": [
                {
                    "use": "official",
                    "text": self.full_name,
                    "family": self.surname,
                    "given": self.first_name,
                }
            ],
            "telecom": [{"system": "phone", "value": self.phone_number}],
            "gender": self.gender,
            "birthDate": self.date_of_birth,
            "address": {"text": self.address},
            "contact": contacts,
            "communication": [{"language": "en", "preferred": True}],
        }


class NextOfKin(models.Model):
    """NextOfKin model."""

    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    next_of_kin = models.ForeignKey(
        User, related_name="next_of_kin", on_delete=models.CASCADE
    )
    relationship = models.CharField(
        choices=[
            ("SPOUSE", "Spouse"),
            ("CHILD", "Child"),
            ("PARENT", "Parent"),
            ("SIBLING", "Sibling"),
            ("OTHER_RELATIVE", "Other Relative"),
        ],
        max_length=16,
    )
    can_consent = models.BooleanField(default=False)

    POST_REQUIRED_FIELDS = ["user_id", "next_of_kin_id", "relationship", "can_consent"]
    SERIALIZATION_FIELDS = POST_REQUIRED_FIELDS
