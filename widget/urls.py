from django.urls import path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from . import views

router = DefaultRouter()
router.register("form", views.WidgetViewSet, basename="FormWidget")
router.register("pricing", views.ContainerViewSet, basename="PricingWidget")
router.register("template", views.FormTemplateViewSet)
router.register(
    "appointment", views.AppointmentWidgetViewSet, basename="AppointmentWidget"
)
widget_data = NestedDefaultRouter(router, "form", lookup="widget")
widget_data.register("data", views.SubmittedDataView, basename="Submitted Data")

urlpatterns = [
    path("<uuid:uuid>", views.WidgetCodeView.as_view()),
    path("booking/<uuid:uuid>", views.AppointmentViewSet.as_view()),
    path("script/<uuid:uuid>.js", views.ServeScriptView.as_view()),
    path("pr/<uuid:uuid>", views.PricingWidgetViewSet.as_view()),
    path(
        "<uuid:uuid>/download-data",
        views.DownloadSubmittedDataView.as_view(),
    ),
]

urlpatterns += router.urls + widget_data.urls
