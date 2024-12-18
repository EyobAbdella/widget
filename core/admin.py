from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(GoogleSheetToken)
admin.site.register(OAuthSession)
admin.site.register(User)

