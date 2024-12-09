from rest_framework import serializers
from widget.models import PreFill, WidgetData


class WidgetSerializer(serializers.ModelSerializer):
    pre_fill = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        write_only=True,
        required=False,
    )

    class Meta:
        model = WidgetData
        fields = [
            "id",
            "user",
            "html",
            "widget_fields",
            "redirect_url",
            "success_msg",
            "post_submit_action",
            "spam_protection",
            "pre_fill",
        ]
        read_only_fields = ["id", "user"]

    def validate_pre_fill(self, value):
        for item in value:
            if not all(key in item for key in ["field_id", "parameter_name"]):
                raise serializers.ValidationError(
                    "Each pre-fill item must contain 'field_id' and 'parameter_name'."
                )
        return value

    def create(self, validated_data):
        pre_fill_data = validated_data.pop("pre_fill", [])
        user_id = self.context.get("user_id")
        widget = WidgetData.objects.create(user_id=user_id, **validated_data)

        PreFill.objects.bulk_create(
            [PreFill(widget=widget, **item) for item in pre_fill_data]
        )
        return widget


class PreFillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreFill
        fields = ["id", "widget", "field_id", "parameter_name"]
        read_only_fields = ["widget"]

    def create(self, validated_data):
        widget_id = self.context.get("widget_id")
        return PreFill.objects.create(widget_id=widget_id, **validated_data)
