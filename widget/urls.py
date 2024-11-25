from django.urls import path
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()
router.register("widget", views.WidgetViewSet, basename="Widget")

urlpatterns = [
    path("<uuid:uuid>", views.WidgetCodeView.as_view()),
] + router.urls
