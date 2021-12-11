import re

import pytest

from utils.models import BaseModel


def test_basemodel_unimplemented_create():
    with pytest.raises(
        NotImplementedError,
        match=re.escape("create(cls, fields) must be implemented by the child class."),
    ):
        BaseModel.create({})
