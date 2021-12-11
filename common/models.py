import re
import uuid

from django.db import models, IntegrityError
from django.core.validators import RegexValidator

from common.payload import ErrorCode


class BaseModel:
    VALIDATION_FIELDS = []
    SERIALIZATION_FIELDS = []

    @classmethod
    def save_wrapper(cls, fields):
        try:
            obj = cls.create(fields)
        except IntegrityError as e:
            extract_field_name_regex = r"Key \((?P<field_name>[_a-z]+)\)=\("
            match = re.search(extract_field_name_regex, e.__cause__.diag.message_detail)
            field_name = match.group("field_name")
            return False, {field_name: ErrorCode.UNIQUE_KEY_VIOLATION}
        return True, obj

    @staticmethod
    def preprocess_choices(choices):
        result = []
        for choice in choices:
            code = choice.upper()
            code = code.replace("'", "").replace("-", " ")
            result.append(("_".join(code.split(" ")), choice))
        return result

    def serialize(self):
        object = self.__dict__
        result = {}
        for field in self.SERIALIZATION_FIELDS:
            result[field] = str(object[field])
        return result


class Entity(models.Model, BaseModel):
    phone_regex = RegexValidator(
        regex=r"^\+254\d{9}$",
        message="Phone number must be entered in the format: '+254712345678'.",
    )

    uuid = models.UUIDField(
        "Universally Unique IDentifier",
        unique=True,
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
    )

    email = models.EmailField("Email Address", unique=True)
    phone_number = models.CharField(
        "Phone Number", validators=[phone_regex], max_length=13
    )
    address = models.TextField("Postal Address")

    date_joined = models.DateTimeField("Date Joined", auto_now_add=True)
    is_active = models.BooleanField("Is Active?", default=True)

    class Meta:
        abstract = True
