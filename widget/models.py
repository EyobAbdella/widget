from django.db import models
from django.core.validators import URLValidator, validate_email, MinValueValidator
from django.conf import settings
from uuid import uuid4
from django.core.exceptions import ValidationError
import re


CURRENCY_USD = "USD"
CURRENCY_EURO = "EUR"
CURRENCY_CHOICES = [(CURRENCY_USD, "USD"), (CURRENCY_EURO, "EURO")]


class EmailNotification(models.Model):
    sender_name = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    email = models.JSONField()

    def clean(self):
        if not isinstance(self.email, list):
            raise ValidationError(
                "The 'email' field must be a list of email addresses."
            )
        for email in self.email:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError(f"Invalid email address: {email}")


class AdminBrandInfo(models.Model):
    logo = models.ImageField(upload_to="admin/brand_logo")
    name = models.CharField(max_length=255)
    redirect_url = models.URLField(null=True, blank=True)


class UserBrandInfo(models.Model):
    logo = models.ImageField(upload_to="user/brand_logo", blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    redirect_url = models.URLField(null=True, blank=True)


class ButtonStyle(models.Model):
    background_color = models.CharField(max_length=100, blank=True, null=True)
    text_color = models.CharField(max_length=100, blank=True, null=True)
    border_radius = models.CharField(max_length=50, blank=True, null=True)
    padding = models.CharField(max_length=50, blank=True, null=True)
    font_size = models.CharField(max_length=50, blank=True, null=True)


class Background(models.Model):
    BACKGROUND_TYPE_CHOICES = [
        ("Image", "Image"),
        ("Video", "Video"),
    ]
    type = models.CharField(
        max_length=10, choices=BACKGROUND_TYPE_CHOICES, blank=True, null=True
    )
    value = models.TextField(blank=True, null=True)
    opacity = models.FloatField(blank=True, null=True)
    file = models.FileField(upload_to="background_files/", blank=True, null=True)


class DisplaySettings(models.Model):
    MODE_CHOICES = [
        ("Inline", "Inline"),
        ("Popup", "Popup"),
        ("Sidebar", "Sidebar"),
    ]
    TRIGGER_CHOICES = [
        ("Immediate", "Immediate"),
        ("Delay", "Delay"),
        ("Scroll", "Scroll"),
        ("Exit", "Exit"),
    ]
    POSITION_CHOICES = [
        ("Left", "Left"),
        ("Right", "Right"),
    ]

    mode = models.CharField(max_length=10, choices=MODE_CHOICES, null=True, blank=True)
    trigger = models.CharField(
        max_length=10, choices=TRIGGER_CHOICES, null=True, blank=True
    )
    position = models.CharField(
        max_length=5, choices=POSITION_CHOICES, null=True, blank=True
    )
    button_text = models.CharField(max_length=100, null=True, blank=True)
    button_style = models.OneToOneField(ButtonStyle, on_delete=models.CASCADE)
    background = models.OneToOneField(Background, on_delete=models.CASCADE)


class WidgetData(models.Model):
    WIDGET_CONTACT_FORM = "CONTACT_US"
    WIDGET_FORM_BUILDER = "FORM"
    SUCCESS_MESSAGE = "MSG"
    REDIRECT_TO_URL = "REDIRECT_URL"
    HIDE_FORM = "HIDE_FORM"
    POST_SUBMIT_ACTION = [
        (SUCCESS_MESSAGE, "msg"),
        (REDIRECT_TO_URL, "redirect_url"),
        (HIDE_FORM, "hide_form"),
    ]
    WIDGET_TYPE_CHOICES = [
        (WIDGET_CONTACT_FORM, "Contact_Form"),
        (WIDGET_FORM_BUILDER, "Form_Builder"),
    ]
    id = models.UUIDField(default=uuid4, primary_key=True)
    widget_type = models.CharField(max_length=10, choices=WIDGET_TYPE_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="widgets"
    )
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    html = models.TextField()
    script = models.TextField(null=True, blank=True)
    widget_fields = models.JSONField(default=list)
    sheet_id = models.CharField(max_length=255, blank=True, null=True)
    post_submit_action = models.CharField(max_length=20, choices=POST_SUBMIT_ACTION)
    success_msg = models.TextField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    spam_protection = models.BooleanField(default=False)
    display_settings = models.OneToOneField(
        DisplaySettings, on_delete=models.SET_NULL, null=True, blank=True
    )
    font_family = models.CharField(max_length=255, blank=True, null=True)
    title_size = models.CharField(max_length=255, blank=True, null=True)
    text_size = models.CharField(max_length=255, blank=True, null=True)
    direction = models.CharField(max_length=255, blank=True, null=True)
    email_notification = models.OneToOneField(
        EmailNotification, on_delete=models.CASCADE, null=True, blank=True
    )
    is_email_notification = models.BooleanField(default=False)
    user_brand_info = models.OneToOneField(
        UserBrandInfo, on_delete=models.CASCADE, null=True, blank=True
    )


class WidgetFile(models.Model):
    widget = models.ForeignKey(WidgetData, on_delete=models.CASCADE)
    file = models.FileField(upload_to="widget/files")


class SubmittedData(models.Model):
    widget = models.ForeignKey(
        WidgetData,
        on_delete=models.CASCADE,
        related_name="form_data",
    )
    data = models.JSONField()


class PreFill(models.Model):
    widget = models.ForeignKey(
        WidgetData,
        on_delete=models.CASCADE,
        related_name="pre_fill",
    )
    field_id = models.CharField(max_length=100)
    parameter_name = models.CharField(max_length=255)


class SubmitButton(models.Model):
    LEFT = "LEFT"
    CENTER = "CENTER"
    RIGHT = "RIGHT"
    ALIGNMENT_CHOICES = [(LEFT, "left"), (CENTER, "center"), (RIGHT, "right")]
    text = models.CharField(max_length=100)
    alignment = models.TextField(default=LEFT, max_length=6, choices=ALIGNMENT_CHOICES)


class FormTemplate(models.Model):
    INLINE = "INLINE"
    FLOATING_PANEL = "FLOATING_PANEL"

    EMBED_TYPE_CHOICES = [(INLINE, "inline"), (FLOATING_PANEL, "floating_panel")]

    DARK = "DARK"
    LIGHT = "LIGHT"
    COLOR_SCHEMA_CHOICES = [(DARK, "dark"), (LIGHT, "light")]

    image = models.ImageField(upload_to="template")
    fields = models.JSONField(default=list)
    header_enabled = models.BooleanField()
    header_title = models.CharField(max_length=255, null=True, blank=True)
    header_caption = models.TextField(null=True, blank=True)
    submit_button = models.OneToOneField(SubmitButton, on_delete=models.CASCADE)
    footer = models.TextField(null=True, blank=True)
    embed_type = models.CharField(
        max_length=14, default=INLINE, choices=EMBED_TYPE_CHOICES
    )
    color_scheme = models.CharField(
        max_length=5, default=LIGHT, choices=COLOR_SCHEMA_CHOICES
    )
    accent_color = models.CharField(max_length=50)
    bg_color = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if not self.header_enabled:
            self.header_title = ""
            self.header_caption = ""
        super().save(*args, **kwargs)


# Pricing Widget


class Link(models.Model):
    link_type = models.CharField(
        max_length=5, choices=[("URL", "Url"), ("EMAIL", "Email"), ("PHONE", "Phone")]
    )
    link_value = models.CharField(max_length=255)
    new_tab = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        if self.link_type == "URL":
            validator = URLValidator()
            try:
                validator(self.link_value)
            except ValidationError:
                raise ValidationError({"link": "Invalid URL"})

        elif self.link_type == "EMAIL":
            try:
                validate_email(self.link_value)
            except ValidationError:
                raise ValidationError({"Email": "Invalid email address"})

        elif self.link_type == "PHONE":
            phone_pattern = r"^\+?\d{7,15}$"
            if not re.match(phone_pattern, self.link_value):
                raise ValidationError({"Phone": "Invalid phone number"})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Button(models.Model):
    text = models.CharField(max_length=100)
    link = models.OneToOneField(Link, on_delete=models.SET_NULL, null=True)
    caption = models.TextField(null=True, blank=True)


class Price(models.Model):
    PREFIX_NONE = "NONE"
    PREFIX_FROM = "FROM"
    PREFIX_UP_TO = "UP_TO"
    PREFIX_AVERAGE = "AVERAGE"
    POSTFIX_NONE = "NONE"
    POSTFIX_HOUR = "HOUR"
    POSTFIX_DAY = "DAY"
    POSTFIX_WEEK = "WEEK"
    POSTFIX_MONTH = "MONTH"
    POSTFIX_YEAR = "YEAR"

    POSTFIX_CHOICES = [
        (POSTFIX_NONE, "None"),
        (POSTFIX_HOUR, "Hour"),
        (POSTFIX_DAY, "Day"),
        (POSTFIX_WEEK, "Week"),
        (POSTFIX_MONTH, "Month"),
        (POSTFIX_YEAR, "Year"),
    ]

    PREFIX_CHOICES = [
        (PREFIX_NONE, "None"),
        (PREFIX_FROM, "From"),
        (PREFIX_AVERAGE, "Average"),
    ]

    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default=CURRENCY_USD
    )
    prefix = models.CharField(max_length=7, choices=PREFIX_CHOICES, default=PREFIX_FROM)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    postfix = models.CharField(
        max_length=5, choices=POSTFIX_CHOICES, default=POSTFIX_MONTH
    )
    caption = models.TextField(null=True, blank=True)


class Content(models.Model):
    pass


class Column(models.Model):
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, related_name="columns"
    )
    title = models.CharField(max_length=255)
    caption = models.TextField(null=True, blank=True)
    price = models.OneToOneField(Price, on_delete=models.SET_NULL, null=True)
    button = models.OneToOneField(Button, on_delete=models.SET_NULL, null=True)
    picture = models.ImageField(upload_to="widget", null=True, blank=True)
    featured_column = models.BooleanField(default=False)
    ribbon_text = models.CharField(max_length=100, null=True, blank=True)
    skin_color = models.CharField(max_length=100, default="#000")


class Features(models.Model):
    ICON_NONE = "N"
    ICON_CHECK = "CH"
    ICON_CROSS = "CR"
    ICON_MINUS = "M"

    ICON_CHOICES = [
        (ICON_NONE, "None"),
        (ICON_CHECK, "Check"),
        (ICON_CROSS, "Cross"),
        (ICON_MINUS, "Minus"),
    ]

    column = models.ForeignKey(
        Column, on_delete=models.CASCADE, related_name="features"
    )
    text = models.TextField()
    icon = models.CharField(max_length=2, default=ICON_NONE, choices=ICON_CHOICES)
    hint = models.TextField(null=True, blank=True)


class Layout(models.Model):
    LAYOUT_GRID = "G"
    LAYOUT_COLUMNS = "C"
    LAYOUT_TABLE = "T"

    LAYOUT_CHOICES = [
        (LAYOUT_GRID, "Grid"),
        (LAYOUT_COLUMNS, "Columns"),
        (LAYOUT_TABLE, "Table"),
    ]

    layout_type = models.CharField(
        max_length=1, choices=LAYOUT_CHOICES, default=LAYOUT_GRID
    )
    picture = models.BooleanField(default=True)
    title = models.BooleanField(default=True)
    features = models.BooleanField(default=True)
    price = models.BooleanField(default=True)
    button = models.BooleanField(default=True)


class TitleAppearance(models.Model):
    color = models.CharField(max_length=100, default="#000")
    caption_color = models.CharField(max_length=100, default="#000")
    font = models.PositiveSmallIntegerField(default=24)


class FeatureAppearance(models.Model):
    color = models.CharField(max_length=100, default="#000")
    font = models.PositiveSmallIntegerField(default=13)


class PriceAppearance(models.Model):
    color = models.CharField(max_length=100, default="#000")
    caption_color = models.CharField(max_length=100, default="#000")
    font = models.PositiveSmallIntegerField(default=24)


class ButtonAppearance(models.Model):
    TYPE_OUTLINE = "O"
    TYPE_FILLED = "F"
    SIZE_SMALL = "S"
    SIZE_MEDIUM = "M"
    SIZE_LARGE = "L"

    SIZE_CHOICE = [
        (SIZE_SMALL, "Small"),
        (SIZE_MEDIUM, "Medium"),
        (SIZE_LARGE, "Large"),
    ]
    TYPE_CHOICE = [(TYPE_OUTLINE, "Outline"), (TYPE_FILLED, "Filled")]

    type = models.CharField(max_length=1, choices=TYPE_CHOICE, default=TYPE_FILLED)
    size = models.CharField(max_length=1, choices=SIZE_CHOICE, default=SIZE_SMALL)
    button_color = models.CharField(max_length=100, default="#000")
    label_color = models.CharField(max_length=100, default="#fff")


class Appearance(models.Model):
    title = models.OneToOneField(TitleAppearance, on_delete=models.SET_NULL, null=True)
    feature = models.OneToOneField(
        FeatureAppearance, on_delete=models.SET_NULL, null=True
    )
    price = models.OneToOneField(PriceAppearance, on_delete=models.SET_NULL, null=True)
    button = models.OneToOneField(
        ButtonAppearance, on_delete=models.SET_NULL, null=True
    )


class Container(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    title = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="widget"
    )
    content = models.OneToOneField(Content, on_delete=models.SET_NULL, null=True)
    layout = models.OneToOneField(Layout, on_delete=models.SET_NULL, null=True)
    appearance = models.OneToOneField(
        Appearance, on_delete=models.SET_NULL, null=True, related_name="container"
    )


# Appointment Widget
