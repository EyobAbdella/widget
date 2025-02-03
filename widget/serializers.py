from django.conf import settings
from rest_framework import serializers
from widget.models import (
    AdminBrandInfo,
    AppointmentBackground,
    AppointmentData,
    AppointmentPrice,
    AppointmentService,
    AppointmentWidget,
    AppointmentWidth,
    Background,
    ButtonColors,
    ButtonSpacing,
    ButtonStyle,
    CornerRadius,
    CoverImage,
    DarkMode,
    DaySchedule,
    DisplaySettings,
    EmailNotification,
    Footer,
    FormTemplate,
    Gradient,
    Header,
    HoverColors,
    ImageSettings,
    ImageUpload,
    LabelStyle,
    Link,
    PreFill,
    PricingCustomPictureSize,
    PricingWidgetImageSettings,
    SpecialIntervals,
    SubmitButton,
    SubmittedData,
    Theme,
    TitleStyle,
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


class GradientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gradient
        fields = ["enabled", "start_color", "end_color", "angle"]


class CornerRadiusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CornerRadius
        fields = ["enabled", "value", "unit"]


class DarkModeSerializer(serializers.ModelSerializer):
    gradient = GradientSerializer()

    class Meta:
        model = DarkMode
        fields = ["primary_color", "background_color", "text_color", "gradient"]


class EmailNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailNotification
        fields = [
            "response_message",
            "response_subject",
            "auto_responder_email",
            "sender_name",
            "subject",
            "message",
            "email",
        ]


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


class ButtonStyleSerializers(serializers.ModelSerializer):
    class Meta:
        model = ButtonStyle
        fields = [
            "background_color",
            "text_color",
            "border_radius",
            "padding",
            "font_size",
            "hover_background_color",
        ]


class ImageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSettings
        fields = ["position", "size", "repeat"]


class BackgroundSerializers(serializers.ModelSerializer):
    image_settings = ImageSettingsSerializer(required=False)

    class Meta:
        model = Background
        fields = [
            "type",
            "value",
            "opacity",
            "file",
            "auto_play",
            "muted",
            "loop",
            "image_settings",
        ]


class DisplaySettingsSerializer(serializers.ModelSerializer):
    button_style = ButtonStyleSerializers(required=False)
    background = BackgroundSerializers(required=False)

    class Meta:
        model = DisplaySettings
        fields = [
            "mode",
            "trigger",
            "position",
            "button_text",
            "button_style",
            "background",
            "button_position",
            "delay",
            "scroll_percentage",
            "show_once",
        ]


class PreFillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreFill
        fields = ["field_id", "parameter_name"]
        read_only_fields = ["widget"]

    def create(self, validated_data):
        widget_id = self.context.get("widget_id")
        return PreFill.objects.create(widget_id=widget_id, **validated_data)


class LabelStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelStyle
        fields = ["font_size", "color", "font_weight"]


class FooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Footer
        fields = ["enabled", "text", "alignment", "font_size", "text_color"]


class ThemeSerializer(serializers.ModelSerializer):
    gradient = GradientSerializer()
    corner_radius = CornerRadiusSerializer()
    dark_mode = DarkModeSerializer()

    class Meta:
        model = Theme
        fields = [
            "mode",
            "primary_color",
            "background_color",
            "text_color",
            "gradient",
            "corner_radius",
            "dark_mode",
        ]


class ButtonSpacingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ButtonSpacing
        fields = ["horizontal", "vertical", "unit"]


class HoverColorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoverColors
        fields = ["background", "text", "border"]


class ButtonColorsSerializer(serializers.ModelSerializer):
    hover = HoverColorsSerializer()

    class Meta:
        model = ButtonColors
        fields = ["background", "text", "border", "hover"]


class SubmitButtonSerializer(serializers.ModelSerializer):
    spacing = ButtonSpacingSerializer(required=False)
    colors = ButtonColorsSerializer(required=False)

    class Meta:
        model = SubmitButton
        fields = [
            "text",
            "variant",
            "alignment",
            "size",
            "full_width",
            "spacing",
            "colors",
        ]


class TitleStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleStyle
        fields = ["bold", "italic", "underline"]


class CoverImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverImage
        fields = ["enabled", "image", "aspect_ratio", "corner_radius"]


class HeaderSerializer(serializers.ModelSerializer):
    cover_image = CoverImageSerializer()

    class Meta:
        model = Header
        fields = ["visible", "alignment", "cover_image"]


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ["image"]


class WidgetSerializer(serializers.ModelSerializer):
    total_submissions = serializers.SerializerMethodField()
    pre_fill_values = PreFillSerializer(source="pre_fill", many=True, required=False)
    pre_fill = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        write_only=True,
        required=False,
    )
    email_notification = EmailNotificationSerializer(required=False)
    admin_brand_info = AdminBrandInfoSerializer(read_only=True)
    user_brand_info = UserBrandInfoSerializer()
    script_url = serializers.SerializerMethodField()
    display_settings = DisplaySettingsSerializer()
    submit_button = SubmitButtonSerializer()
    theme = ThemeSerializer()
    footer = FooterSerializer()
    title_style = TitleStyleSerializer(required=False)
    header = HeaderSerializer()

    class Meta:
        model = WidgetData
        fields = [
            "id",
            "widget_type",
            "user",
            "name",
            "title",
            "description",
            "title_style",
            "header",
            "html",
            "script",
            "script_url",
            "sheet_id",
            "widget_fields",
            "redirect_url",
            "success_msg",
            "post_submit_action",
            "spam_protection",
            "display_settings",
            "font_family",
            "title_size",
            "text_size",
            "direction",
            "pre_fill",
            "pre_fill_values",
            "email_notification",
            "is_email_notification",
            "user_brand_info",
            "admin_brand_info",
            "submit_button",
            "theme",
            "default_language",
            "footer",
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
        display_settings_data = validated_data.pop("display_settings", None)
        user_brand_info_data = validated_data.pop("user_brand_info", None)
        user_id = self.context.get("user_id")
        footer_data = validated_data.pop("footer", None)
        theme_data = validated_data.pop("theme", None)
        submit_button_data = validated_data.pop("submit_button", None)
        title_style_data = validated_data.pop("title_style", None)
        header_data = validated_data.pop("header", None)

        if theme_data:
            gradient_data = theme_data.pop("gradient", None)
            corner_radius_data = theme_data.pop("corner_radius", None)
            dark_mode_data = theme_data.pop("dark_mode", None)

            gradient = (
                Gradient.objects.create(**gradient_data) if gradient_data else None
            )
            corner_radius = (
                CornerRadius.objects.create(**corner_radius_data)
                if corner_radius_data
                else None
            )

            if dark_mode_data:
                dark_mode_gradient_data = dark_mode_data.pop("gradient", None)
                dark_mode_gradient = (
                    Gradient.objects.create(**dark_mode_gradient_data)
                    if dark_mode_gradient_data
                    else None
                )
                dark_mode = DarkMode.objects.create(
                    gradient=dark_mode_gradient, **dark_mode_data
                )
            else:
                dark_mode = None

            theme = Theme.objects.create(
                gradient=gradient,
                corner_radius=corner_radius,
                dark_mode=dark_mode,
                **theme_data,
            )
            validated_data["theme"] = theme

        if submit_button_data:
            colors_data = submit_button_data.pop("colors", None)
            spacing_data = submit_button_data.pop("spacing", None)

            if colors_data:
                hover_data = colors_data.pop("hover", None)
                hover = HoverColors.objects.create(**hover_data) if hover_data else None
                colors = ButtonColors.objects.create(hover=hover, **colors_data)
            else:
                colors = None

            if spacing_data:
                spacing = ButtonSpacing.objects.create(**spacing_data)
            else:
                spacing = None

            submit_button = SubmitButton.objects.create(
                colors=colors, spacing=spacing, **submit_button_data
            )
            validated_data["submit_button"] = submit_button

        if footer_data:
            footer = Footer.objects.create(**footer_data)
            validated_data["footer"] = footer

        if title_style_data:
            title_style = TitleStyle.objects.create(**title_style_data)
            validated_data["title_style"] = title_style

        if header_data:
            cover_image_data = header_data.pop("cover_image", None)
            if cover_image_data:
                cover_image = CoverImage.objects.create(**cover_image_data)
            else:
                cover_image = None
            header = Header.objects.create(cover_image=cover_image, **header_data)
            validated_data["header"] = header

        if display_settings_data:
            background_data = display_settings_data.pop("background", None)

            if background_data:
                image_settings_data = background_data.pop("image_settings", None)

                print(image_settings_data)
                if image_settings_data:
                    image_settings = ImageSettings.objects.create(**image_settings_data)
                else:
                    image_settings = None

                background = Background.objects.create(
                    image_settings=image_settings, **background_data
                )
            else:
                background = None

            button_style_data = display_settings_data.pop("button_style", None)

            if button_style_data:
                button_style = ButtonStyle.objects.create(**button_style_data)
            else:
                button_style = None

            display_settings = DisplaySettings.objects.create(
                **display_settings_data,
                button_style=button_style,
                background=background,
            )
            validated_data["display_settings"] = display_settings

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
        display_settings_data = validated_data.pop("display_settings", None)
        footer_data = validated_data.pop("footer", None)
        theme_data = validated_data.pop("theme", None)
        submit_button_data = validated_data.pop("submit_button", None)
        title_style_data = validated_data.pop("title_style", None)
        header_data = validated_data.pop("header", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if theme_data:
            gradient_data = theme_data.pop("gradient", None)
            corner_radius_data = theme_data.pop("corner_radius", None)
            dark_mode_data = theme_data.pop("dark_mode", None)

            if gradient_data:
                if instance.theme and instance.theme.gradient:
                    gradient = instance.theme.gradient
                    for attr, value in gradient_data.items():
                        setattr(gradient, attr, value)
                    gradient.save()
                else:
                    gradient = Gradient.objects.create(**gradient_data)
            else:
                gradient = None

            if corner_radius_data:
                if instance.theme and instance.theme.corner_radius:
                    corner_radius = instance.theme.corner_radius
                    for attr, value in corner_radius_data.items():
                        setattr(corner_radius, attr, value)
                    corner_radius.save()
                else:
                    corner_radius = CornerRadius.objects.create(**corner_radius_data)
            else:
                corner_radius = None

            if dark_mode_data:
                dark_mode_gradient_data = dark_mode_data.pop("gradient", None)
                if dark_mode_gradient_data:
                    if (
                        instance.theme
                        and instance.theme.dark_mode
                        and instance.theme.dark_mode.gradient
                    ):
                        dark_mode_gradient = instance.theme.dark_mode.gradient
                        for attr, value in dark_mode_gradient_data.items():
                            setattr(dark_mode_gradient, attr, value)
                        dark_mode_gradient.save()
                    else:
                        dark_mode_gradient = Gradient.objects.create(
                            **dark_mode_gradient_data
                        )
                else:
                    dark_mode_gradient = None

                if instance.theme and instance.theme.dark_mode:
                    dark_mode = instance.theme.dark_mode
                    for attr, value in dark_mode_data.items():
                        setattr(dark_mode, attr, value)
                    dark_mode.gradient = dark_mode_gradient
                    dark_mode.save()
                else:
                    dark_mode = DarkMode.objects.create(
                        gradient=dark_mode_gradient, **dark_mode_data
                    )
            else:
                dark_mode = None

            if instance.theme:
                theme = instance.theme
                for attr, value in theme_data.items():
                    setattr(theme, attr, value)
                theme.gradient = gradient
                theme.corner_radius = corner_radius
                theme.dark_mode = dark_mode
                theme.save()
            else:
                theme = Theme.objects.create(
                    gradient=gradient,
                    corner_radius=corner_radius,
                    dark_mode=dark_mode,
                    **theme_data,
                )
            instance.theme = theme

        if submit_button_data:
            colors_data = submit_button_data.pop("colors", None)
            spacing_data = submit_button_data.pop("spacing", None)

            if colors_data:
                hover_data = colors_data.pop("hover", None)
                if instance.submit_button and instance.submit_button.colors:
                    colors = instance.submit_button.colors
                    if hover_data:
                        if colors.hover:
                            for attr, value in hover_data.items():
                                setattr(colors.hover, attr, value)
                            colors.hover.save()
                        else:
                            colors.hover = HoverColors.objects.create(**hover_data)
                    for attr, value in colors_data.items():
                        setattr(colors, attr, value)
                    colors.save()
                else:
                    hover = (
                        HoverColors.objects.create(**hover_data) if hover_data else None
                    )
                    colors = ButtonColors.objects.create(hover=hover, **colors_data)
            else:
                colors = None

            if spacing_data:
                if instance.submit_button and instance.submit_button.spacing:
                    spacing = instance.submit_button.spacing
                    for attr, value in spacing_data.items():
                        setattr(spacing, attr, value)
                    spacing.save()
                else:
                    spacing = ButtonSpacing.objects.create(**spacing_data)
            else:
                spacing = None

            if instance.submit_button:
                submit_button = instance.submit_button
                for attr, value in submit_button_data.items():
                    setattr(submit_button, attr, value)
                submit_button.colors = colors
                submit_button.spacing = spacing
                submit_button.save()
            else:
                submit_button = SubmitButton.objects.create(
                    colors=colors, spacing=spacing, **submit_button_data
                )
            instance.submit_button = submit_button

        if footer_data:
            if instance.footer:
                for attr, value in footer_data.items():
                    setattr(instance.footer, attr, value)
                instance.footer.save()
            else:
                footer = Footer.objects.create(**footer_data)
                instance.footer = footer

        if title_style_data:
            if instance.title_style:
                for attr, value in title_style_data.items():
                    setattr(instance.title_style, attr, value)
                instance.title_style.save()
            else:
                title_style = TitleStyle.objects.create(**title_style_data)
                instance.title_style = title_style

        if header_data:
            if instance.header:
                cover_image_data = header_data.pop("cover_image", None)
                if cover_image_data:
                    if instance.header.cover_image:
                        for attr, value in cover_image_data.items():
                            setattr(instance.header.cover_image, attr, value)
                        instance.header.cover_image.save()
                    else:
                        cover_image = CoverImage.objects.create(**cover_image_data)
                        instance.header.cover_image = cover_image
                for attr, value in header_data.items():
                    setattr(instance.header, attr, value)
                instance.header.save()
            else:
                cover_image_data = header_data.pop("cover_image", None)
                if cover_image_data:
                    cover_image = CoverImage.objects.create(**cover_image_data)
                else:
                    cover_image = None
                header = Header.objects.create(cover_image=cover_image, **header_data)
                instance.header = header

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

        if display_settings_data:
            button_style_data = display_settings_data.pop("button_style", None)
            if button_style_data:
                if instance.display_settings and instance.display_settings.button_style:
                    button_style = instance.display_settings.button_style
                    for attr, value in button_style_data.items():
                        setattr(button_style, attr, value)
                    button_style.save()
                else:
                    button_style = ButtonStyle.objects.create(**button_style_data)
            else:
                button_style = None

            background_data = display_settings_data.pop("background", None)
            if background_data:
                image_settings_data = background_data.pop("image_settings", None)

                if image_settings_data:
                    if (
                        instance.display_settings
                        and instance.display_settings.background
                        and instance.display_settings.background.image_settings
                    ):
                        image_settings = (
                            instance.display_settings.background.image_settings
                        )
                        for attr, value in image_settings_data.items():
                            setattr(image_settings, attr, value)
                        image_settings.save()
                    else:
                        image_settings = ImageSettings.objects.create(
                            **image_settings_data
                        )
                else:
                    image_settings = None

                if instance.display_settings and instance.display_settings.background:
                    background = instance.display_settings.background
                    for attr, value in background_data.items():
                        setattr(background, attr, value)
                    background.image_settings = image_settings
                    background.save()
                else:
                    background = Background.objects.create(
                        image_settings=image_settings, **background_data
                    )
            else:
                background = None

            if instance.display_settings:
                display_settings = instance.display_settings
                for attr, value in display_settings_data.items():
                    setattr(display_settings, attr, value)
                display_settings.button_style = button_style
                display_settings.background = background
                display_settings.save()
            else:
                display_settings = DisplaySettings.objects.create(
                    **display_settings_data,
                    button_style=button_style,
                    background=background,
                )
            instance.display_settings = display_settings

        if pre_fill_data is not None:
            instance.pre_fill.all().delete()
            PreFill.objects.bulk_create(
                [PreFill(widget=instance, **item) for item in pre_fill_data]
            )

        instance.save()
        return instance


class SubmittedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedData
        fields = ["id", "widget", "data"]


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
        colors_data = submit_button_data.pop("colors", None)
        hover_data = colors_data.pop("hover", None) if colors_data else None

        hover_instance = (
            HoverColors.objects.create(**hover_data) if hover_data else None
        )
        colors_instance = (
            ButtonColors.objects.create(hover=hover_instance, **colors_data)
            if colors_data
            else None
        )

        spacing_data = submit_button_data.pop("spacing", None)
        spacing_instance = (
            ButtonSpacing.objects.create(**spacing_data) if spacing_data else None
        )

        submit_button = SubmitButton.objects.create(
            colors=colors_instance, spacing=spacing_instance, **submit_button_data
        )

        return FormTemplate.objects.create(
            submit_button=submit_button, **validated_data
        )

    def update(self, instance, validated_data):
        submit_button_data = validated_data.pop("submit_button", None)

        instance = super().update(instance, validated_data)

        if submit_button_data:
            colors_data = submit_button_data.pop("colors", None)
            if colors_data:
                hover_data = colors_data.pop("hover", None)

                if instance.submit_button.colors:
                    if hover_data:
                        if instance.submit_button.colors.hover:
                            for key, value in hover_data.items():
                                setattr(instance.submit_button.colors.hover, key, value)
                            instance.submit_button.colors.hover.save()
                        else:
                            instance.submit_button.colors.hover = (
                                HoverColors.objects.create(**hover_data)
                            )

                    for key, value in colors_data.items():
                        setattr(instance.submit_button.colors, key, value)
                    instance.submit_button.colors.save()
                else:
                    hover_instance = (
                        HoverColors.objects.create(**hover_data) if hover_data else None
                    )
                    instance.submit_button.colors = ButtonColors.objects.create(
                        hover=hover_instance, **colors_data
                    )

            spacing_data = submit_button_data.pop("spacing", None)
            if spacing_data:
                if instance.submit_button.spacing:
                    for key, value in spacing_data.items():
                        setattr(instance.submit_button.spacing, key, value)
                    instance.submit_button.spacing.save()
                else:
                    instance.submit_button.spacing = ButtonSpacing.objects.create(
                        **spacing_data
                    )

            submit_button_serializer = SubmitButtonSerializer(
                instance.submit_button, data=submit_button_data, partial=True
            )
            submit_button_serializer.is_valid(raise_exception=True)
            submit_button_serializer.save()

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


class PricingCustomPictureSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingCustomPictureSize
        fields = ["width", "height"]


class PricingWidgetImageSettingsSerializer(serializers.ModelSerializer):
    custom_size = PricingCustomPictureSizeSerializer(required=False)

    class Meta:
        model = PricingWidgetImageSettings
        fields = [
            "is_background",
            "size",
            "custom_size",
            "position",
            "priority",
            "fit",
            "alignment",
        ]

    def create(self, validated_data):
        custom_size_data = validated_data.pop("custom_size", None)
        custom_size = (
            PricingCustomPictureSize.objects.create(**custom_size_data)
            if custom_size_data
            else None
        )
        return PricingWidgetImageSettings.objects.create(
            custom_size=custom_size, **validated_data
        )

    def update(self, instance, validated_data):
        custom_size_data = validated_data.pop("custom_size", None)

        if custom_size_data:
            if instance.custom_size:
                for attr, value in custom_size_data.items():
                    setattr(instance.custom_size, attr, value)
                instance.custom_size.save()
            else:
                instance.custom_size = PricingCustomPictureSize.objects.create(
                    **custom_size_data
                )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["link_type", "link_value", "new_tab"]


class ButtonSerializer(serializers.ModelSerializer):
    link = LinkSerializer()

    class Meta:
        model = Button
        fields = ["id", "text", "link", "caption"]

    def create(self, validated_data):
        link_data = validated_data.pop("link")
        link_instance = Link.objects.create(**link_data)
        button_instance = Button.objects.create(link=link_instance, **validated_data)
        return button_instance

    def update(self, instance, validated_data):
        link_data = validated_data.pop("link", None)
        if link_data:
            if instance.link:
                for attr, value in link_data.items():
                    setattr(instance.link, attr, value)
                instance.link.save()
            else:
                instance.link = Link.objects.create(**link_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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
    button = ButtonSerializer()
    featured_column = serializers.BooleanField(required=False)
    ribbon_text = serializers.CharField(required=False)
    features = serializers.ListField(child=FeaturesSerializer(), required=False)
    picture = serializers.ImageField(required=False, allow_null=True)
    image_settings = PricingWidgetImageSettingsSerializer(required=False)
    skin_color = serializers.CharField(required=False)

    def create(self, validated_data):
        price_data = validated_data.pop("price", None)
        button_data = validated_data.pop("button", None)
        features_data = validated_data.pop("features", [])
        image_settings_data = validated_data.pop("image_settings", None)

        price = Price.objects.create(**price_data) if price_data else None
        button_serializer = ButtonSerializer(data=button_data)
        button_serializer.is_valid(raise_exception=True)
        button = button_serializer.save()

        image_settings = None
        if image_settings_data:
            image_settings_serializer = PricingWidgetImageSettingsSerializer(
                data=image_settings_data
            )
            image_settings_serializer.is_valid(raise_exception=True)
            image_settings = image_settings_serializer.save()

        column = Column.objects.create(
            price=price, button=button, image_settings=image_settings, **validated_data
        )

        for feature_data in features_data:
            Features.objects.create(column=column, **feature_data)

        return column

    def update(self, instance, validated_data):
        price_data = validated_data.pop("price", None)
        button_data = validated_data.pop("button", None)
        features_data = validated_data.pop("features", [])
        image_settings_data = validated_data.pop("image_settings", None)

        if price_data:
            if instance.price:
                for attr, value in price_data.items():
                    setattr(instance.price, attr, value)
                instance.price.save()
            else:
                instance.price = Price.objects.create(**price_data)

        if button_data:
            button_serializer = ButtonSerializer(
                instance=instance.button, data=button_data
            )
            button_serializer.is_valid(raise_exception=True)
            instance.button = button_serializer.save()

        if image_settings_data:
            image_settings_serializer = PricingWidgetImageSettingsSerializer(
                instance=instance.image_settings, data=image_settings_data
            )
            image_settings_serializer.is_valid(raise_exception=True)
            instance.image_settings = image_settings_serializer.save()

        instance.features.all().delete()
        for feature_data in features_data:
            Features.objects.create(column=instance, **feature_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CreateContainerSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    layout = LayoutSerializer(required=False)
    content = serializers.ListField(
        child=CreateContentSerializer(), write_only=True, required=False
    )
    appearance = AppearanceSerializer(required=False)

    def create(self, validated_data):
        layout_data = validated_data.pop("layout")
        widget_title = validated_data.pop("title")
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
            user_id=user_id,
            title=widget_title,
            layout=layout,
            content=content,
            appearance=appearance,
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
    image_settings = PricingWidgetImageSettingsSerializer()

    class Meta:
        model = Column
        fields = [
            "id",
            "title",
            "caption",
            "price",
            "button",
            "picture",
            "image_settings",
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
        fields = ["id", "title", "content_id", "content", "layout", "appearance"]

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


# Appointment widget Serializers


class AppointmentPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentPrice
        fields = ["currency", "type", "price"]


class DayScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DaySchedule
        fields = ["id", "day", "is_open", "time_ranges"]


class SpecialIntervalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialIntervals
        fields = [
            "id",
            "type",
            "start_date",
            "end_date",
            "working_hours",
            "description",
        ]


class AppointmentWidthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentWidth
        fields = ["full_width", "custom_value"]


class AppointmentBackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentBackground
        fields = ["color", "border_radius"]


class AppointmentServiceSerializer(serializers.ModelSerializer):
    price = AppointmentPriceSerializer()

    class Meta:
        model = AppointmentService
        fields = ["name", "description", "picture", "duration", "price"]


class AppointmentWidgetSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    service = AppointmentServiceSerializer()
    day_schedules = DayScheduleSerializer(many=True)
    special_intervals = SpecialIntervalsSerializer(many=True)
    width = AppointmentWidthSerializer()
    background = AppointmentBackgroundSerializer()
    integration_google_sheets_id = serializers.CharField(read_only=True)

    class Meta:
        model = AppointmentWidget
        fields = [
            "id",
            "name",
            "service",
            "day_schedules",
            "special_intervals",
            "min_advance_minutes",
            "max_advance_days",
            "time_zone",
            "display_business_card",
            "business_name",
            "business_about",
            "business_contacts_phone",
            "business_contacts_email",
            "business_contacts_address",
            "business_contacts_website",
            "business_contacts_whatsapp",
            "business_contacts_instagram",
            "business_picture",
            "business_logo",
            "embed_type",
            "trigger_button_position",
            "trigger_button_text",
            "trigger_button_icon",
            "trigger_button_radius",
            "width",
            "background",
            "text_color",
            "accent_color",
            "font_url",
            "client_notification",
            "owner_notification",
            "owner_email",
            "integration_google_sheets",
            "integration_google_sheets_id",
            "created_at",
        ]

    def create(self, validated_data):
        user = self.context.get("request").user
        service_data = validated_data.pop("service")
        day_schedules_data = validated_data.pop("day_schedules", [])
        special_intervals_data = validated_data.pop("special_intervals", [])
        width_data = validated_data.pop("width", None)
        background_data = validated_data.pop("background", None)
        price_data = service_data.pop("price", None)

        price = AppointmentPrice.objects.create(**price_data)
        service = AppointmentService.objects.create(**service_data, price=price)

        width = None
        if width_data:
            width = AppointmentWidth.objects.create(**width_data)

        background = None
        if background_data:
            background = AppointmentBackground.objects.create(**background_data)

        appointment_widget = AppointmentWidget.objects.create(
            user=user,
            service=service,
            width=width,
            background=background,
            **validated_data,
        )

        for day_schedule_data in day_schedules_data:
            print(day_schedule_data)
            day_schedule = DaySchedule.objects.create(**day_schedule_data)
            appointment_widget.day_schedules.add(day_schedule)

        for special_interval_data in special_intervals_data:
            special_interval = SpecialIntervals.objects.create(**special_interval_data)
            appointment_widget.special_intervals.add(special_interval)

        return appointment_widget

    def update(self, instance, validated_data):
        service_data = validated_data.pop("service", None)
        day_schedules_data = validated_data.pop("day_schedules", [])
        special_intervals_data = validated_data.pop("special_intervals", [])
        width_data = validated_data.pop("width", None)
        background_data = validated_data.pop("background", None)

        if service_data:
            price_data = service_data.pop("price", None)

            if price_data:
                for attr, value in price_data.items():
                    setattr(instance.service.price, attr, value)
                instance.service.price.save()

            for attr, value in service_data.items():
                setattr(instance.service, attr, value)
            instance.service.save()

        if width_data:
            if instance.width:
                for attr, value in width_data.items():
                    setattr(instance.width, attr, value)
                instance.width.save()
            else:
                instance.width = AppointmentWidth.objects.create(**width_data)

        if background_data:
            if instance.background:
                for attr, value in background_data.items():
                    setattr(instance.background, attr, value)
                instance.background.save()
            else:
                instance.background = AppointmentBackground.objects.create(
                    **background_data
                )

        if day_schedules_data:
            instance.day_schedules.clear()
            for day_schedule_data in day_schedules_data:
                day_schedule = DaySchedule.objects.create(**day_schedule_data)
                instance.day_schedules.add(day_schedule)

        if special_intervals_data:
            instance.special_intervals.clear()
            for special_interval_data in special_intervals_data:
                special_interval = SpecialIntervals.objects.create(
                    **special_interval_data
                )
                instance.special_intervals.add(special_interval)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class AppointmentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentData
        fields = ["id", "date", "name", "email", "notes"]

    def create(self, validated_data):
        appointment_id = self.context.get("appointment_id")
        return AppointmentData.objects.create(
            appointment_id=appointment_id, **validated_data
        )
