from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .permissions import IsAdminOrReadOnly
from .utils import create_sheet, write_sheet
from .serializers import (
    FormTemplateSerializer,
    SubmittedDataSerializer,
    WidgetSerializer,
    # Pricing widget serializers
    ContainerSerializer,
    CreateContainerSerializer,
)
from .models import (
    FormTemplate,
    SubmittedData,
    WidgetData,
    WidgetFile,
    Container,
)
import csv
import requests


class WidgetCodeView(APIView):
    def get(self, request, uuid):
        try:
            widget = WidgetData.objects.get(id=uuid)
            serializer = WidgetSerializer(
                widget,
                context={"include_email_notification": False, "request": request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except WidgetData.DoesNotExist:
            return Response(
                {"error": "Widget not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, uuid):
        try:
            widget = WidgetData.objects.get(id=uuid)
            if widget.spam_protection:
                recaptcha_token = request.data.get("recaptchaToken")
                if not recaptcha_token:
                    return self._error_response("Missing reCAPTCHA token")
                if not self._validate_recaptcha(recaptcha_token):
                    return self._error_response("Invalid reCAPTCHA token")

            field_values, errors = self._process_fields(request, widget)
            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            self._handle_sheet_integration(widget, field_values)

            self._send_email_notifications(widget, field_values)

            self._save_submitted_data(uuid, field_values)

            return self._handle_post_submit_action(widget, field_values)

        except WidgetData.DoesNotExist:
            return Response(
                {"error": "Widget not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def _error_response(self, message):
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    def _validate_recaptcha(self, recaptcha_token):
        url = "https://www.google.com/recaptcha/api/siteverify"
        response = requests.post(
            url,
            data={"secret": settings.RECAPTCHA_SECRET_KEY, "response": recaptcha_token},
        )
        result = response.json()
        return result.get("success", False)

    def _process_fields(self, request, widget):
        field_values = []
        errors = {}

        for field in widget.widget_fields:
            field_id = field["id"]
            field_type = field["type"]
            is_required = field["required"]
            field_label = field.get("label")
            value = None

            if field_type == "file":
                uploaded_files = request.FILES.getlist(field_id)
                if is_required and not uploaded_files:
                    errors[field_label] = f"{field_label} is required."
                elif uploaded_files:
                    widget_file = WidgetFile.objects.create(
                        widget=widget, file=uploaded_files[0]
                    )
                    value = request.build_absolute_uri(widget_file.file.url)

            else:
                value = request.data.get(field_id, "").strip()
                if field_type == "consent" and is_required and value != "true":
                    errors[field_label] = f"{field_label} is required."
                elif is_required and not value:
                    errors[field_label] = f"{field_label} is required."
                elif field_type != "consent":
                    field_values.append(
                        {"label": field_label, "type": field_type, "value": value}
                    )

        return field_values, errors

    def _handle_sheet_integration(self, widget, field_values):
        if widget.sheet_id:
            write_sheet(
                widget.user,
                widget.sheet_id,
                [[item["value"] for item in field_values]],
            )
        else:
            sheet_id = create_sheet(widget.user, widget.name)
            write_sheet(
                widget.user,
                sheet_id,
                [
                    [item["label"].lower() for item in field_values],
                    [item["value"] for item in field_values],
                ],
            )
            widget.sheet_id = sheet_id
            widget.save()

    def _send_email_notifications(self, widget, field_values):
        email_receiver = next(
            (i for i in field_values if i.get("type") == "email"), None
        )
        user_data = "\n".join(
            [f"{item['label']}: {item['value']}" for item in field_values]
        )

        if email_receiver and widget.email_notification.auto_responder_email:
            send_mail(
                widget.email_notification.response_subject,
                widget.email_notification.response_message,
                widget.user,
                [email_receiver.get("value")],
                fail_silently=False,
            )

        if widget.is_email_notification:
            send_mail(
                widget.email_notification.subject,
                f"{widget.email_notification.message}\n{user_data}",
                widget.email_notification.sender_name,
                widget.email_notification.email,
                fail_silently=False,
            )

    def _save_submitted_data(self, uuid, field_values):
        data = {item["label"]: item["value"] for item in field_values}
        SubmittedData.objects.create(widget_id=uuid, data=data)

    def _handle_post_submit_action(self, widget, field_values):
        if widget.post_submit_action == WidgetData.SUCCESS_MESSAGE:
            return Response(
                {"action": "success_msg", "value": widget.success_msg},
                status=status.HTTP_200_OK,
            )
        elif widget.post_submit_action == WidgetData.REDIRECT_TO_URL:
            return Response(
                {"action": "redirect_url", "value": widget.redirect_url},
                status=status.HTTP_200_OK,
            )
        elif widget.post_submit_action == WidgetData.HIDE_FORM:
            return Response({"action": "hide_form"}, status=status.HTTP_200_OK)


class WidgetViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WidgetSerializer

    def get_queryset(self):
        widget_type = self.request.query_params.get("widget_type")
        if widget_type:
            return WidgetData.objects.filter(
                user=self.request.user, widget_type__iexact=widget_type
            )
        return WidgetData.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {"user_id": self.request.user.id, "request": self.request}


class DownloadSubmittedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        submitted_data = SubmittedData.objects.filter(
            widget_id=uuid, widget__user=request.user
        )

        if not submitted_data.exists():
            return Response({"error": "No data found."}, status=404)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="widget_{uuid}_data.csv"'
        )

        writer = csv.writer(response)

        keys = set()
        for entry in submitted_data:
            keys.update(entry.data.keys())

        keys = sorted(keys)
        writer.writerow(keys)

        for entry in submitted_data:
            writer.writerow([entry.data.get(key, "") for key in keys])

        return response


class SubmittedDataView(viewsets.ModelViewSet):
    http_method_names = ["get"]
    serializer_class = SubmittedDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        widget_id = self.kwargs["widget_pk"]
        return SubmittedData.objects.filter(widget__id=widget_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        total_submissions = queryset.count()

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {"total_submissions": total_submissions, "submissions": serializer.data}
        )


class FormTemplateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = FormTemplate.objects.all()
    serializer_class = FormTemplateSerializer


class ServeScriptView(APIView):
    def get(self, request, uuid):
        widget = get_object_or_404(WidgetData, id=uuid)
        return HttpResponse(widget.script, content_type="application/javascript")


# Pricing Widget


class ContainerViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return Container.objects.filter(user_id=user_id)

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateContainerSerializer
        return ContainerSerializer

    def get_serializer_context(self):
        return {"user_id": self.request.user.id, "request": self.request}


class PricingWidgetViewSet(APIView):
    def get(self, request, uuid):
        queryset = Container.objects.get(id=uuid)
        serializer = ContainerSerializer(
            queryset, context={"request": self.request, "view_layout": False}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
