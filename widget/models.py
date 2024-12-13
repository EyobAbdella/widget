from django.db import models
from django.conf import settings
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class EmailNotification(models.Model):
    sender_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
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
    logo = models.ImageField(upload_to="user/brand_logo")
    name = models.CharField(max_length=255)
    redirect_url = models.URLField(null=True, blank=True)


class WidgetData(models.Model):
    SUCCESS_MESSAGE = "MSG"
    REDIRECT_TO_URL = "REDIRECT_URL"
    HIDE_FORM = "HIDE_FORM"
    POST_SUBMIT_ACTION = [
        (SUCCESS_MESSAGE, "msg"),
        (REDIRECT_TO_URL, "redirect_url"),
        (HIDE_FORM, "hide_form"),
    ]

    id = models.UUIDField(default=uuid4, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="widgets"
    )
    html = models.TextField()
    widget_fields = models.JSONField(default=list)
    sheet_id = models.CharField(max_length=255, blank=True, null=True)
    post_submit_action = models.CharField(max_length=20, choices=POST_SUBMIT_ACTION)
    success_msg = models.TextField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    spam_protection = models.BooleanField(default=False)
    email_notification = models.OneToOneField(
        EmailNotification, on_delete=models.CASCADE, null=True, blank=True
    )
    is_email_notification = models.BooleanField(default=False)
    user_brand_info = models.OneToOneField(UserBrandInfo, on_delete=models.CASCADE)


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
