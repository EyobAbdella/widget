from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status

from widget.tasks import handle_google_sheet_integration, send_email_notifications
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AppointmentDataSerializer,
    AppointmentWidgetSerializer,
    FormTemplateSerializer,
    ImageUploadSerializer,
    PricingWidgetV2Serializer,
    WidgetSerializer,
    ContainerSerializer,
    CreateContainerSerializer,
)
from .models import (
    AppointmentWidget,
    FormTemplate,
    ImageUpload,
    PricingWidgetV2,
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
            email_receiver = next(
                (i for i in field_values if i.get("type") == "email"), None
            )
            user_data = "\n".join(
                [f"{item['label']}: {item['value']}" for item in field_values]
            )
            if widget.user.is_oauth:
                handle_google_sheet_integration.delay(
                    widget_id=widget.id,
                    model_name="widget.WidgetData",
                    values=[item["value"] for item in field_values],
                    sheet_header=[item["label"].lower() for item in field_values],
                )
            user_data = "\n".join(
                [f"{item['label']}: {item['value']}" for item in field_values]
            )
            if email_receiver and widget.email_notification.auto_responder_email:
                send_email_notifications.delay(
                    subject=widget.email_notification.response_subject,
                    body=widget.email_notification.response_message,
                    sender=widget.user,
                    recipients_list=[email_receiver.get("value")],
                )
            if widget.is_email_notification:
                send_email_notifications.delay(
                    subject=widget.email_notification.subject,
                    body=f"{widget.email_notification.message}\n{user_data}",
                    sender=widget.email_notification.sender_name,
                    recipients_list=widget.email_notification.email,
                )

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


class ImageUploadViewSet(ModelViewSet):
    http_method_names = ["post"]
    serializer_class = ImageUploadSerializer
    queryset = ImageUpload.objects.all()


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


# class SubmittedDataView(viewsets.ModelViewSet):
#     http_method_names = ["get"]
#     serializer_class = SubmittedDataSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         widget_id = self.kwargs["widget_pk"]
#         return SubmittedData.objects.filter(widget__id=widget_id)

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()

#         total_submissions = queryset.count()

#         serializer = self.get_serializer(queryset, many=True)

#         return Response(
#             {"total_submissions": total_submissions, "submissions": serializer.data}
#         )


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


# Appointment Widget


class AppointmentWidgetViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentWidgetSerializer

    def get_queryset(self):
        return AppointmentWidget.objects.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        return {"request": self.request}


class AppointmentViewSet(APIView):
    def get(self, request, uuid):
        try:
            queryset = AppointmentWidget.objects.get(id=uuid)
        except AppointmentWidget.DoesNotExist:
            return Response(
                {"error": "widget doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AppointmentWidgetSerializer(queryset, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, uuid):
        try:
            queryset = AppointmentWidget.objects.get(id=uuid)
            serializers = AppointmentDataSerializer(data=request.data)
            serializers.is_valid(raise_exception=True)

            response_data = {"message": "Appointment booked successfully!"}
            response = Response(response_data, status=status.HTTP_201_CREATED)

            if queryset.user.is_oauth:
                handle_google_sheet_integration.delay(
                    widget_id=queryset.id,
                    model_name="widget.AppointmentWidget",
                    values=list(serializers.data.values()),
                    sheet_header=["Name", "Email", "Date Time", "Note"],
                )

            if queryset.owner_notification and queryset.owner_email:
                send_email_notifications.delay(
                    subject="New Appointment Booked",
                    body=f"Hi {queryset.owner_email},\n\nA new appointment has been booked.",
                    sender=queryset.owner_email,
                    recipients_list=[queryset.owner_email],
                )
            if queryset.client_notification and serializers.data.get("email"):
                send_email_notifications.delay(
                    subject=f"Appointment Confirmation – {queryset.business_name}",
                    body=f"Hi {serializers.data.get('name')},\n\nYour appointment for {queryset.service.name} is confirmed!",
                    sender=queryset.user.email,
                    recipients_list=[serializers.data.get("email")],
                )

            return response
        except AppointmentWidget.DoesNotExist:
            return Response(
                {"error": "Appointment Widget not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


# Version 2 Pricing Widget


class PricingWidgetViewSetV2(ModelViewSet):
    serializer_class = PricingWidgetV2Serializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        widget_id = self.kwargs.get("pk")
        if self.request.user.is_authenticated:
            return PricingWidgetV2.objects.filter(user_id=self.request.user.id)
        return PricingWidgetV2.objects.filter(widget_id=widget_id)

    def get_serializer_context(self):
        return {"request": self.request}
