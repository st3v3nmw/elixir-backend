from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from model_bakery import baker

from apps.authentication.models import User


class CustomUserManagerTestModel(TestCase):
    def setUp(self) -> None:
        gen_user = baker.make(User, phone_number="+254712345678")
        self.default_fields = gen_user.__dict__
        for field in ["email", "password", "_state", "uuid", "is_superuser"]:
            self.default_fields.pop(field)
        return super().setUp()

    def test_create_user(self):
        normal_user = User.objects.create_user(
            "email@provider.com", "some-password", **self.default_fields
        )
        self.assertEqual(normal_user.is_staff, False)

    def test_create_superuser(self):
        default_fields = {**self.default_fields}
        default_fields["is_superuser"] = False
        with self.assertRaises(ValueError) as e:
            User.objects.create_superuser(
                "email@provider.com", "some-password", **default_fields
            )
        self.assertEqual(str(e.exception), _("Superuser must have is_superuser=True."))

        default_fields["is_superuser"] = True
        admin = User.objects.create_superuser(
            "email@provider.com", "some-password", **default_fields
        )
        self.assertEqual(admin.is_staff, True)


class UserTestModel(TestCase):
    def setUp(self):
        self.normal_user = baker.make(
            User,
            first_name="Jane",
            last_name="Doe",
            is_superuser=False,
            phone_number="+254712345678",
        )
        self.admin = baker.make(User, is_superuser=True, phone_number="+254712345678")

    def test_string_representation(self):
        self.assertEqual(str(self.normal_user), "Jane Doe")

    def test_is_staff(self):
        self.assertEqual(self.normal_user.is_staff, False)
        self.assertEqual(self.admin.is_staff, True)

    def test_get_name(self):
        self.assertEqual(self.normal_user.get_full_name(), "Jane Doe")
        self.assertEqual(self.normal_user.get_short_name(), "Jane")
