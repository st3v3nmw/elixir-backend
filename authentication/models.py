"""This module houses models for the authentication app."""

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import IntegrityError, models

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
    last_name = models.CharField(max_length=32)
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
        "last_name",
        "national_id",
        "gender",
        "date_of_birth",
        "phone_number",
    ]

    POST_REQUIRED_FIELDS = [USERNAME_FIELD, "password"] + REQUIRED_FIELDS
    SERIALIZATION_FIELDS = (
        ["uuid", USERNAME_FIELD]
        + REQUIRED_FIELDS
        + ["address", "relatives", "date_joined", "is_active"]
    )

    class Meta:  # noqa
        ordering = ["-date_joined"]

    @classmethod
    def create(cls, fields):
        """Create a User."""
        try:
            return True, User.objects.create_user(**fields)
        except IntegrityError as e:
            return False, str(e)

    def __str__(self) -> str:
        """Return string representation of User."""
        return f"{self.first_name} {self.last_name} ({self.uuid})"


class NextOfKin(BaseModel):
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
    SERIALIZATION_FIELDS = ["uuid"] + POST_REQUIRED_FIELDS

    class Meta:  # noqa
        unique_together = (
            "user",
            "next_of_kin",
        )
