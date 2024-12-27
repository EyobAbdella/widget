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
    # Pricing widget models
    Appearance,
    Button,
    ButtonAppearance,
    FeatureAppearance,
    Price,
    Content,
    Column,
    Features,
    Layout,
    Container,
    PriceAppearance,
    TitleAppearance,
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
    script_url = serializers.SerializerMethodField()

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
            "script_url",
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

    def get_script_url(self, obj):
        if not self.context.get("request"):
            return None
        if obj.script:
            request = self.context.get("request")
            return request.build_absolute_uri(f"/form-builder/script/{obj.id}.js")
        return None

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


# Pricing Widget
class LayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layout
        fields = [
            "id",
            "layout_type",
            "picture",
            "title",
            "features",
            "price",
            "button",
        ]


class TitleAppearanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleAppearance
        fields = ["color", "caption_color", "font"]


class FeatureAppearanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureAppearance
        fields = ["color", "font"]


class PriceAppearanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAppearance
        fields = ["color", "caption_color", "font"]


class ButtonAppearanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButtonAppearance
        fields = ["type", "size", "button_color", "label_color"]


class AppearanceSerializer(serializers.ModelSerializer):
    title = TitleAppearanceSerializer(required=False)
    feature = FeatureAppearanceSerializer(required=False)
    price = PriceAppearanceSerializer(required=False)
    button = ButtonAppearanceSerializer(required=False)

    class Meta:
        model = Appearance
        fields = ["title", "feature", "price", "button"]


class ButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Button
        fields = ["id", "text", "link", "caption"]


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ["id", "currency", "prefix", "amount", "postfix", "caption"]


class FeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Features
        fields = ["id", "text", "icon", "hint"]


class CreateContentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)
    caption = serializers.CharField(required=False)
    price = PriceSerializer(required=False)
    button = ButtonSerializer(required=False)
    featured_column = serializers.BooleanField(required=False)
    ribbon_text = serializers.CharField(required=False)
    features = serializers.ListField(child=FeaturesSerializer(), required=False)
    picture = serializers.ImageField(required=False, allow_null=True)
    skin_color = serializers.CharField(required=False)

    def create(self, validated_data):
        price_data = validated_data.pop("price", None)
        button_data = validated_data.pop("button", None)
        features_data = validated_data.pop("features", [])

        price = Price.objects.create(**price_data) if price_data else None
        button = Button.objects.create(**button_data) if button_data else None

        column = Column.objects.create(price=price, button=button, **validated_data)

        for feature_data in features_data:
            Features.objects.create(column=column, **feature_data)

        return column

    def update(self, instance, validated_data):
        price_data = validated_data.pop("price", None)
        button_data = validated_data.pop("button", None)
        features_data = validated_data.pop("features", [])

        if price_data:
            if instance.price:
                for attr, value in price_data.items():
                    setattr(instance.price, attr, value)
                instance.price.save()
            else:
                instance.price = Price.objects.create(**price_data)

        if button_data:
            if instance.button:
                for attr, value in button_data.items():
                    setattr(instance.button, attr, value)
                instance.button.save()
            else:
                instance.button = Button.objects.create(**button_data)

        instance.features.all().delete()
        for feature_data in features_data:
            Features.objects.create(column=instance, **feature_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CreateContainerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    layout = LayoutSerializer(required=False)
    content = serializers.ListField(
        child=CreateContentSerializer(), write_only=True, required=False
    )
    appearance = AppearanceSerializer(required=False)

    def create(self, validated_data):
        layout_data = validated_data.pop("layout")
        column_data = validated_data.pop("content")
        appearance_data = validated_data.pop("appearance", None)

        layout = Layout.objects.create(**layout_data)

        title_data = appearance_data.pop("title", None) if appearance_data else None
        feature_data = appearance_data.pop("feature", None) if appearance_data else None
        price_data = appearance_data.pop("price", None) if appearance_data else None
        button_data = appearance_data.pop("button", None) if appearance_data else None

        title = TitleAppearance.objects.create(**(title_data or {}))
        feature = FeatureAppearance.objects.create(**(feature_data or {}))
        price = PriceAppearance.objects.create(**(price_data or {}))
        button = ButtonAppearance.objects.create(**(button_data or {}))

        appearance = Appearance.objects.create(
            title=title,
            feature=feature,
            price=price,
            button=button,
        )

        content = Content.objects.create()

        for column in column_data:
            column_instance = CreateContentSerializer(data=column)
            column_instance.is_valid(raise_exception=True)
            column_instance.save(content=content)

        user_id = self.context.get("user_id")
        container = Container.objects.create(
            user_id=user_id, layout=layout, content=content, appearance=appearance
        )
        return container

    def update(self, instance, validated_data):
        layout_data = validated_data.pop("layout", None)
        appearance_data = validated_data.pop("appearance", None)
        content_data = validated_data.pop("content", [])

        if appearance_data:
            title_data = appearance_data.get("title", None)
            feature_data = appearance_data.get("feature", None)
            price_data = appearance_data.get("price", None)
            button_data = appearance_data.get("button", None)

            if title_data:
                if instance.appearance.title:
                    for attr, value in title_data.items():
                        setattr(instance.appearance.title, attr, value)
                    instance.appearance.title.save()
                else:
                    instance.appearance.title = TitleAppearance.objects.create(
                        **title_data
                    )

            if feature_data:
                if instance.appearance.feature:
                    for attr, value in feature_data.items():
                        setattr(instance.appearance.feature, attr, value)
                    instance.appearance.feature.save()
                else:
                    instance.appearance.feature = FeatureAppearance.objects.create(
                        **feature_data
                    )

            if price_data:
                if instance.appearance.price:
                    for attr, value in price_data.items():
                        setattr(instance.appearance.price, attr, value)
                    instance.appearance.price.save()
                else:
                    instance.appearance.price = PriceAppearance.objects.create(
                        **price_data
                    )

            if button_data:
                if instance.appearance.button:
                    for attr, value in button_data.items():
                        setattr(instance.appearance.button, attr, value)
                    instance.appearance.button.save()
                else:
                    instance.appearance.button = ButtonAppearance.objects.create(
                        **button_data
                    )

        instance.appearance.save()

        if layout_data:
            for attr, value in layout_data.items():
                setattr(instance.layout, attr, value)
            instance.layout.save()

        for column_data in content_data:
            column_id = column_data.get("id")
            if list(column_data.keys()) == ["id"] and column_id:
                try:
                    Column.objects.get(id=column_id).delete()
                except Column.DoesNotExist:
                    pass
            elif column_id:
                column_instance = Column.objects.get(id=column_id)
                CreateContentSerializer().update(column_instance, column_data)
            else:
                column_instance = CreateContentSerializer(data=column_data)
                column_instance.is_valid(raise_exception=True)
                column_instance.save(content=instance.content)
        instance.save()
        return instance


class ColumnSerializer(serializers.ModelSerializer):
    price = PriceSerializer()
    button = ButtonSerializer()
    features = FeaturesSerializer(many=True)

    class Meta:
        model = Column
        fields = [
            "id",
            "title",
            "caption",
            "price",
            "button",
            "picture",
            "features",
            "featured_column",
            "ribbon_text",
            "skin_color",
        ]


class ContainerSerializer(serializers.ModelSerializer):
    layout = LayoutSerializer()
    content = ColumnSerializer(source="content.columns", many=True)
    appearance = AppearanceSerializer()

    class Meta:
        model = Container
        fields = ["id", "content_id", "content", "layout", "appearance"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        view_layout = self.context.get("view_layout", True)
        if instance.layout and not view_layout:
            if not instance.layout.title:
                for rep in representation.get("content"):
                    rep.pop("title", None)
            if not instance.layout.picture:
                for rep in representation.get("content"):
                    rep.pop("picture", None)
            if not instance.layout.features:
                for rep in representation.get("content"):
                    rep.pop("features", None)
            if not instance.layout.price:
                for rep in representation.get("content"):
                    rep.pop("price", None)
            if not instance.layout.button:
                for rep in representation.get("content"):
                    rep.pop("button", None)
            representation.pop("layout")
            representation.pop("content_id")
            representation.pop("id")
        return representation
