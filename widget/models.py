from django.db import models
from django.conf import settings
from uuid import uuid4


class WidgetData(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="widgets"
    )
    html = models.TextField()
    success_msg = models.TextField()
    widget_fields = models.JSONField(default=list)


class WidgetFile(models.Model):
    widget = models.ForeignKey(WidgetData, on_delete=models.CASCADE)
    file = models.FileField(upload_to="widget/files")
