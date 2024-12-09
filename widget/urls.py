from django.urls import path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from . import views

router = DefaultRouter()
router.register("widget", views.WidgetViewSet, basename="Widget")

prefill_form = NestedDefaultRouter(router, "widget", lookup="widget")
prefill_form.register("form", views.PreFillFormViewSet, basename="Prefill-Form")

urlpatterns = [
    path("<uuid:uuid>", views.WidgetCodeView.as_view()),
    path(
        "widget/<uuid:uuid>/download-data",
        views.DownloadSubmittedDataView.as_view(),
    ),
]

urlpatterns += router.urls + prefill_form.urls
