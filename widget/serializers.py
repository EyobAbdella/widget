from rest_framework.serializers import ModelSerializer
from widget.models import WidgetData


class WidgetSerializer(ModelSerializer):
    class Meta:
        model = WidgetData
        fields = ["id", "user", "html", "widget_fields", "success_msg"]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        user_id = self.context.get("user_id")
        print(validated_data)
        return WidgetData.objects.create(user_id=user_id, **validated_data)
