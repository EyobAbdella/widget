from django.conf import settings
from rest_framework import serializers
from widget.models import (
    AdminBrandInfo,
    EmailNotification,
    FormTemplate,
    PreFill,
    SubmitButton,
    SubmittedData,
    WidgetData,
    UserBrandInfo,
)


class EmailNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailNotification
        fields = ["sender_name", "subject", "message", "email"]


class AdminBrandInfoSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = AdminBrandInfo
        fields = ["logo", "name", "redirect_url"]

    def get_logo(self, obj):
        request = self.context.get("request")
        if obj.logo:
            if request:
                return request.build_absolute_uri(obj.logo.url)
            else:
                return f"{settings.MEDIA_URL}{obj.logo.url}"
        return None


class UserBrandInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBrandInfo
        fields = ["logo", "name", "redirect_url"]


class WidgetSerializer(serializers.ModelSerializer):
    total_submissions = serializers.SerializerMethodField()
    pre_fill = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        write_only=True,
        required=False,
    )
    email_notification = EmailNotificationSerializer(required=False)
    admin_brand_info = AdminBrandInfoSerializer(read_only=True)
    user_brand_info = UserBrandInfoSerializer()

    class Meta:
        model = WidgetData
        fields = [
            "id",
            "user",
            "name",
            "title",
            "description",
            "html",
            "script",
            "sheet_id",
            "widget_fields",
            "redirect_url",
            "success_msg",
            "post_submit_action",
            "spam_protection",
            "pre_fill",
            "email_notification",
            "is_email_notification",
            "user_brand_info",
            "admin_brand_info",
            "total_submissions",
        ]
        read_only_fields = ["id", "user", "total_submissions", "sheet_id"]

    def validate_pre_fill(self, value):
        for item in value:
            if not all(key in item for key in ["field_id", "parameter_name"]):
                raise serializers.ValidationError(
                    "Each pre-fill item must contain 'field_id' and 'parameter_name'."
                )
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        admin_brand_info = AdminBrandInfo.objects.first()
        if admin_brand_info:
            representation["admin_brand_info"] = AdminBrandInfoSerializer(
                admin_brand_info, context={"request": self.context.get("request")}
            ).data

        if not self.context.get("include_email_notification", True):
            representation.pop("email_notification", None)
            representation.pop("is_email_notification", None)

        return representation

    def get_total_submissions(self, obj):
        return SubmittedData.objects.filter(widget=obj).count()

    def create(self, validated_data):
        email_notification_data = validated_data.pop("email_notification", None)
        pre_fill_data = validated_data.pop("pre_fill", [])
        user_brand_info_data = validated_data.pop("user_brand_info", None)
        user_id = self.context.get("user_id")

        if user_brand_info_data:
            user_brand_info = UserBrandInfo.objects.create(**user_brand_info_data)
            validated_data["user_brand_info"] = user_brand_info

        widget = WidgetData.objects.create(user_id=user_id, **validated_data)

        if email_notification_data:
            email_notification = EmailNotification.objects.create(
                **email_notification_data
            )
            widget.email_notification = email_notification
            widget.save()

        PreFill.objects.bulk_create(
            [PreFill(widget=widget, **item) for item in pre_fill_data]
        )

        return widget

    def update(self, instance, validated_data):
        email_notification_data = validated_data.pop("email_notification", None)
        user_brand_info_data = validated_data.pop("user_brand_info", None)
        pre_fill_data = validated_data.pop("pre_fill", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if email_notification_data:
            if instance.email_notification:
                email_notification = instance.email_notification
                for attr, value in email_notification_data.items():
                    setattr(email_notification, attr, value)
                email_notification.save()
            else:
                email_notification = EmailNotification.objects.create(
                    **email_notification_data
                )
                instance.email_notification = email_notification

        if user_brand_info_data:
            if instance.user_brand_info:
                user_brand_info = instance.user_brand_info
                for attr, value in user_brand_info_data.items():
                    setattr(user_brand_info, attr, value)
                user_brand_info.save()
            else:
                user_brand_info = UserBrandInfo.objects.create(**user_brand_info_data)
                instance.user_brand_info = user_brand_info

        if pre_fill_data is not None:
            instance.pre_fill.all().delete()
            PreFill.objects.bulk_create(
                [PreFill(widget=instance, **item) for item in pre_fill_data]
            )

        instance.save()
        return instance


class PreFillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreFill
        fields = ["id", "widget", "field_id", "parameter_name"]
        read_only_fields = ["widget"]

    def create(self, validated_data):
        widget_id = self.context.get("widget_id")
        return PreFill.objects.create(widget_id=widget_id, **validated_data)


class SubmittedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedData
        fields = ["id", "widget", "data"]


class SubmitButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmitButton
        fields = ["text", "alignment"]


class FormTemplateSerializer(serializers.ModelSerializer):
    submit_button = SubmitButtonSerializer()

    class Meta:
        model = FormTemplate
        fields = [
            "id",
            "image",
            "fields",
            "header_enabled",
            "header_title",
            "header_caption",
            "submit_button",
            "footer",
            "embed_type",
            "color_scheme",
            "accent_color",
            "bg_color",
        ]

    def create(self, validated_data):
        submit_button_data = validated_data.pop("submit_button")
        submit_button = SubmitButton.objects.create(**submit_button_data)
        return FormTemplate.objects.create(
            submit_button=submit_button, **validated_data
        )

    def update(self, instance, validated_data):
        submit_button_data = validated_data.pop("submit_button", None)

        instance = super().update(instance, validated_data)

        if submit_button_data:
            submit_button_serializer = SubmitButtonSerializer(
                instance.submit_button, data=submit_button_data
            )
            submit_button_serializer.is_valid(raise_exception=True)
            submit_button_serializer.save()

        header_enabled = validated_data.get("header_enabled", instance.header_enabled)
        if not header_enabled:
            instance.header_title = ""
            instance.header_caption = ""

        instance.save()
        return instance
