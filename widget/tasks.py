from celery import shared_task
from widget.models import AppointmentWidget
from django.core.mail import send_mail
from widget.utils import write_sheet, create_sheet
from django.apps import apps


@shared_task
def handle_google_sheet_integration(widget_id, model_name, values, sheet_header):
    try:
        model = apps.get_model(model_name)
        widget = model.objects.get(id=widget_id)
        sheet_id = widget.integration_google_sheets_id
        if sheet_id:
            write_sheet(
                widget.user,
                sheet_id,
                [values],
            )
        else:
            sheet_id = create_sheet(widget.user, widget.name)
            write_sheet(
                widget.user,
                sheet_id,
                [
                    sheet_header,
                    values,
                ],
            )
            widget.integration_google_sheets_id = sheet_id
            widget.save()

    except model.DoesNotExist:
        pass


@shared_task
def send_email_notifications(subject, body, sender, recipients_list):
    send_mail(
        subject,
        body,
        sender,
        recipients_list,
        fail_silently=False,
    )
