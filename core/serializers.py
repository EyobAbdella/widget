from rest_framework import serializers


class GoogleAPISerializer(serializers.Serializer):
    code = serializers.CharField()
    error = serializers.CharField(required=False)
    state = serializers.CharField()
