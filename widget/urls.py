from django.urls import path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from . import views

router = DefaultRouter()
router.register("form", views.WidgetViewSet, basename="Widget")
router.register("pricing", views.ContainerViewSet, basename="PricingWidget")
router.register("template", views.FormTemplateViewSet)

prefill_form = NestedDefaultRouter(router, "form", lookup="widget")
prefill_form.register("prefill", views.PreFillFormViewSet, basename="Prefill-Form")

widget_data = NestedDefaultRouter(router, "form", lookup="widget")
widget_data.register("data", views.SubmittedDataView, basename="Submitted Data")

urlpatterns = [
    path("<uuid:uuid>", views.WidgetCodeView.as_view()),
    path("script/<uuid:uuid>.js", views.ServeScriptView.as_view()),
    path("pr/<uuid:uuid>", views.PricingWidgetViewSet.as_view()),
    path(
        "<uuid:uuid>/download-data",
        views.DownloadSubmittedDataView.as_view(),
    ),
]

urlpatterns += router.urls + prefill_form.urls + widget_data.urls
