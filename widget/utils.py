from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from core.models import GoogleSheetToken


def store_tokens(user, access_token, refresh_token):
    token, created = GoogleSheetToken.objects.update_or_create(user=user)
    token.set_access_token(access_token)
    token.set_refresh_token(refresh_token)
    token.save()


def get_credentials(user):
    try:
        token = GoogleSheetToken.objects.get(user=user)
    except GoogleSheetToken.DoesNotExist:
        return None

    credentials = Credentials(
        token=token.get_access_token(),
        refresh_token=token.get_refresh_token(),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        store_tokens(user, credentials.token, token.get_refresh_token())

    return credentials


def write_sheet(user, sheet_id, values):
    credentials = get_credentials(user)
    if not credentials:
        return None

    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    body = {"values": values}

    result = (
        sheet.values()
        .append(
            spreadsheetId=sheet_id,
            range="Sheet1",
            valueInputOption="RAW",
            body=body,
            insertDataOption="INSERT_ROWS",
        )
        .execute()
    )

    return result


def create_sheet(user):
    credentials = get_credentials(user)
    if not credentials:
        return None

    service = build("sheets", "v4", credentials=credentials)

    spreadsheet = {"properties": {"title": "Widget-Form-Data"}}

    result = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId,properties")
        .execute()
    )

    spreadsheet_id = result.get("spreadsheetId")
    spreadsheet_title = result.get("properties", {}).get("title")

    return spreadsheet_id
