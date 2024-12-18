from django.contrib import admin
from .models import *


admin.site.register(EmailNotification)
admin.site.register(AdminBrandInfo)
admin.site.register(UserBrandInfo)
admin.site.register(WidgetData)
admin.site.register(WidgetFile)
admin.site.register(SubmittedData)
admin.site.register(PreFill)
admin.site.register(SubmitButton)
admin.site.register(FormTemplate)


