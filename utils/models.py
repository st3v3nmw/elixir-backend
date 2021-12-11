import re

from django.db import IntegrityError

from utils.payload import ErrorCode


class BaseModel:
    VALIDATION_FIELDS = []
    SERIALIZATION_FIELDS = []

    @classmethod
    def create(cls, _):
        raise NotImplementedError(
            "create(cls, fields) must be implemented by the child class."
        )

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

    def serialize(self):
        object = self.__dict__
        result = {}
        for field in self.SERIALIZATION_FIELDS:
            result[field] = str(object[field])
        return result
