from django.db import models
from django.conf import settings
from uuid import uuid4
from django.core.exceptions import ValidationError


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
