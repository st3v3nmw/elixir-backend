"""This module houses common abstract models."""

import uuid

from django.core.validators import RegexValidator
from django.db import IntegrityError, models


class BaseModel(models.Model):
    """Abstract model which this project's models inherit."""

    POST_REQUIRED_FIELDS = []
    SERIALIZATION_FIELDS = []

    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, primary_key=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, fields):
        """Wrap the cls.objects.update_or_create method to hoist errors up the call stack."""
        direct_saves, related_saves = {}, {}
        for key, value in fields.items():
            if isinstance(
                getattr(cls, key),
                models.fields.related_descriptors.ManyToManyDescriptor,
            ):
                related_saves[key] = value
            else:
                direct_saves[key] = value
        try:
            obj, _ = cls.objects.update_or_create(**direct_saves)
            for key, id_list in related_saves.items():
                for uuid in id_list:
                    getattr(obj, key).add(uuid)
        except IntegrityError as e:
            return False, str(e)
        return True, obj

    @staticmethod
    def preprocess_choices(choices):
        """Preprocess text[] for use in Django choicefield models."""
        result = []
        for choice in choices:
            code = choice.upper()
            code = code.replace("'", "").replace("-", " ")
            result.append(("_".join(code.split(" ")), choice))
        return result

    def serialize(self):
        """Convert self into a dictionary with self.SERIALIZATION_FIELDS keys."""
        result = {}
        for field in self.SERIALIZATION_FIELDS:
            obj = getattr(self, field)
            if isinstance(obj, (bool, str, int)) or obj is None:
                result[field] = obj
            elif isinstance(obj, models.Manager):
                result[field] = [x.serialize() for x in obj.all()]
            elif isinstance(obj, BaseModel):
                result[field] = obj.serialize()
            else:
                result[field] = str(obj)
        return result

    def fhir_serialize(self):
        """Serialize self as an FHIR resource."""
        raise NotImplementedError  # Implemented by child class

    class Meta:  # noqa
        abstract = True


class Entity(BaseModel):
    """Abstract model for users and organizations."""

    phone_regex = RegexValidator(
        regex=r"^\+254\d{9}$",
        message="Phone number must be entered in the format: '+254712345678'.",
    )

    email = models.EmailField(unique=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=13)
    address = models.TextField()

    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:  # noqa
        abstract = True
