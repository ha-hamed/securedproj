from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from . import models


class StatInline(admin.StackedInline):
    model = models.UserStatistics
    can_delete = False
    verbose_name_plural = "statistics"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (StatInline, )


class SecuredResourceStatisticsAdmin(admin.ModelAdmin):
    readonly_fields = ("date",)


admin.site.register(models.SecuredResourceStatistics,
                    SecuredResourceStatisticsAdmin)

# model registration
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(models.SecuredResource)
admin.site.register(models.UserStatistics)
