from apps.authentication.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "uuid",
            "url",
            "first_name",
            "last_name",
            "country",
            "national_id",
            "gender",
            "date_of_birth",
            "email",
            "phone_number",
            "date_joined",
            "is_active",
        ]
