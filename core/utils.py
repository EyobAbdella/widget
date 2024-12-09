from .models import GoogleSheetToken


def store_tokens(user, access_token, refresh_token):
    token, created = GoogleSheetToken.objects.update_or_create(
        user=user,
    )
    token.set_access_token(access_token)
    if refresh_token:
        token.set_refresh_token(refresh_token)
    token.save()
