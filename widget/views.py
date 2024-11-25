from pprint import pprint
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import WidgetSerializer
from .models import WidgetData, WidgetFile


class WidgetCodeView(APIView):
    def get(self, request, uuid):
        queryset = WidgetData.objects.get(id=uuid)
        serializer = WidgetSerializer(queryset)
        return Response(serializer.data)

    def post(self, request, uuid):
        try:
            widget = WidgetData.objects.get(id=uuid)
            widget_fields = widget.widget_fields

            field_values = []
            errors = {}

            for field in widget_fields:
                field_id = field["id"]
                field_type = field["type"]
                is_required = field["required"]
                field_label = field.get("label")
                value = None

                if field_type == "text":
                    value = request.data.get(field_id, "").strip()

                elif field_type == "file":
                    uploaded_files = request.FILES.getlist(field_id)

                    if is_required and not uploaded_files:
                        errors[field_label] = f"{field_label} is required."
                    else:
                        if uploaded_files:
                            widget_file = WidgetFile.objects.create(
                                widget=widget, file=uploaded_files[0]
                            )
                            value = widget_file.file.url

                field_values.append({"id": field_id, "value": value})

                if is_required and not value:
                    errors[field_label] = f"{field_label} is required."

            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            pprint(field_values)

            return Response(
                {"message": widget.success_msg, "field_values": field_values},
                status=status.HTTP_200_OK,
            )

        except WidgetData.DoesNotExist:
            return Response(
                {"error": "Widget not found."}, status=status.HTTP_404_NOT_FOUND
            )


class WidgetViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return WidgetData.objects.filter(user=user.id)

    serializer_class = WidgetSerializer

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}
