from django.contrib import admin


# Register your models here.
from iHubSite.models import Users


class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'no', 'identity', 'name', 'gender', 'major', 'avatar', 'mail', 'weChat_id', 'phone', 'reg_time', 'credit')


admin.site.register(Users, UsersAdmin)
