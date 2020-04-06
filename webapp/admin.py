from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models

class StatInline(admin.StackedInline):
    model = models.UserStatistics
    can_delete = False
    verbose_name_plural = 'Statistics'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = ( StatInline, )

class SecuredResourceStatisticsAdmin(admin.ModelAdmin):
    readonly_fields = ('Date',)

admin.site.register(models.SecuredResourceStatistics,SecuredResourceStatisticsAdmin)

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(models.SecuredResource)
admin.site.register(models.UserStatistics)
