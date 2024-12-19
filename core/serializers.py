from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class GoogleAPISerializer(serializers.Serializer):
    code = serializers.CharField()
    error = serializers.CharField(required=False)
    state = serializers.CharField()


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        data["is_oauth"] = self.user.is_oauth
        data["is_admin"] = self.user.is_staff
        return data
