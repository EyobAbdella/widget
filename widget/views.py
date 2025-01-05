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
    PreFill,
    SubmittedData,
    WidgetData,
    WidgetFile,
    Container,
)
import csv
import requests


class WidgetCodeView(APIView):
    def get(self, request, uuid):
        queryset = WidgetData.objects.get(id=uuid)
        serializer = WidgetSerializer(
            queryset, context={"include_email_notification": False, "request": request}
        )

        return Response(serializer.data)

    def post(self, request, uuid):
        try:
            widget = WidgetData.objects.get(id=uuid)
            recaptcha_token = request.data.get("recaptchaToken")
            if widget.spam_protection and not recaptcha_token:
                return Response(
                    {"error": "Missing reCAPTCHA token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if widget.spam_protection:
                secret_key = settings.RECAPTCHA_SECRET_KEY
                url = "https://www.google.com/recaptcha/api/siteverify"
                response = requests.post(
                    url, data={"secret": secret_key, "response": recaptcha_token}
                )
                result = response.json()

            if not widget.spam_protection or result.get("success"):
                widget_fields = widget.widget_fields
                field_values = []
                errors = {}

                for field in widget_fields:
                    field_id = field["id"]
                    field_type = field["type"]
                    is_required = field["required"]
                    field_label = field.get("label")
                    value = None

                    if field_type == "file":
                        uploaded_files = request.FILES.getlist(field_id)

                        if is_required and not uploaded_files:
                            errors[field_label] = f"{field_label} is required."
                        else:
                            if uploaded_files:
                                widget_file = WidgetFile.objects.create(
                                    widget=widget, file=uploaded_files[0]
                                )
                                value = request.build_absolute_uri(widget_file.file.url)
                    elif field_type:
                        value = request.data.get(field_id, "").strip()

                    field_values.append(
                        {"label": field_label, "type": field_type, "value": value}
                    )

                    if is_required and not value:
                        errors[field_label] = f"{field_label} is required."

                if errors:
                    return Response(
                        {"errors": errors}, status=status.HTTP_400_BAD_REQUEST
                    )
                email_receiver = next(
                    (i for i in field_values if i.get("type") == "email"), None
                )
                if widget.sheet_id:
                    write_sheet(
                        widget.user,
                        widget.sheet_id,
                        [[item["value"] for item in field_values]],
                    )
                if not widget.sheet_id:
                    sheet_id = create_sheet(widget.user)

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

                user_data = [
                    f"{i.get('label')}: {i.get('value')}" for i in field_values
                ]
                if email_receiver:
                    send_mail(
                        "",
                        "Thank you for submitting the form.",
                        widget.user,
                        [email_receiver.get("value")],
                        fail_silently=False,
                    )
                if widget.is_email_notification:
                    send_mail(
                        widget.email_notification.subject,  # subject
                        f"{widget.email_notification.message} \n{user_data}",  # message
                        widget.email_notification.sender_name,  # sender name
                        widget.email_notification.email,
                        fail_silently=False,
                    )
                data = {item["label"]: item["value"] for item in field_values}
                SubmittedData.objects.create(widget_id=uuid, data=data)
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
            else:
                return Response(
                    {"success": False, "error": "Invalid reCAPTCHA token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except WidgetData.DoesNotExist:
            return Response(
                {"error": "Widget not found."}, status=status.HTTP_404_NOT_FOUND
            )


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


# class PreFillFormViewSet(viewsets.ViewSet):
#     def create(self, request, *args, **kwargs):
#         widget_id = self.kwargs.get("widget_pk")
#         if not widget_id:
#             return Response({"error": "Widget ID is missing in URL."}, status=400)

#         query_params = request.query_params

#         try:
#             widget = WidgetData.objects.get(id=widget_id)
#             widget_fields = widget.widget_fields

#             prefills = PreFill.objects.filter(widget_id=widget_id)
#             prefill_map = {pre.parameter_name: pre.field_id for pre in prefills}

#             field_map = {field["id"]: field for field in widget_fields}

#             data = []

#             submittedValues = {}
#             for key, value in query_params.items():
#                 field_id = prefill_map.get(key)
#                 if field_id:
#                     matching_field = field_map.get(field_id)

#                     if matching_field:
#                         submittedValues[matching_field["label"]] = value
#                         data.append(
#                             {
#                                 matching_field["label"]: value,
#                             }
#                         )
#             if widget.sheet_id:
#                 write_sheet(
#                     widget.user,
#                     widget.sheet_id,
#                     [[list(d.values())[0] for d in data]],
#                 )
#             if not widget.sheet_id:
#                 sheet_id = create_sheet(widget.user)
#                 write_sheet(
#                     widget.user,
#                     sheet_id,
#                     [
#                         [list(d.keys())[0] for d in data],
#                         [list(d.values())[0] for d in data],
#                     ],
#                 )
#                 widget.sheet_id = sheet_id
#                 widget.save()
#                 if widget.is_email_notification:
#                     send_mail(
#                         widget.email_notification.subject,  # subject
#                         f"{widget.email_notification.message} \n{data}",  # message
#                         widget.email_notification.sender_name,  # sender name
#                         widget.email_notification.email,
#                         fail_silently=False,
#                     )
#             SubmittedData.objects.create(widget_id=widget_id, data=submittedValues)

#         except WidgetData.DoesNotExist:
#             return Response({"error": "Widget not found."}, status=404)

#         return Response("", status=200)


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
