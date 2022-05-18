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
        direct_saves, many_to_many_saves, foreign_key_saves = {}, {}, {}
        foreign_key_models = {
            r.related_name: r.related_model for r in cls._meta.related_objects
        }

        for key, value in fields.items():
            if key in foreign_key_models:
                foreign_key_saves[key] = value
            elif isinstance(
                getattr(cls, key),
                models.fields.related_descriptors.ManyToManyDescriptor,
            ):
                many_to_many_saves[key] = value
            else:
                direct_saves[key] = value

        try:
            parent_obj, _ = cls.objects.update_or_create(**direct_saves)
            for field, objects in foreign_key_saves.items():
                for object in objects:
                    if not isinstance(value, str):
                        object[f"{parent_obj._meta.model_name}_id"] = parent_obj.uuid
                        created, value = foreign_key_models[field].create(object)
                    getattr(parent_obj, field).add(value)
            for field, id_list in many_to_many_saves.items():
                for uuid in id_list:
                    getattr(parent_obj, field).add(uuid)
        except IntegrityError as e:
            return False, str(e)
        return True, parent_obj

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
