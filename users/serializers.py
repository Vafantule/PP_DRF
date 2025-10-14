from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

User = get_user_model()


class UserRegistrationSerializer(ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
            avatar=validated_data.get("avatar", None),
        )
        return user
