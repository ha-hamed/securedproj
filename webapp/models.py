from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

STATUS = (
    (1, 'active'),
    (2, 'expired')
)
TYPES = (
    (1, 'link'),
    (2, 'file')
)


class UserStatistics(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='user_stat')
    last_user_agent = models.CharField(max_length=200,)

    class Meta:
        db_table = "user_statistics"


class SecuredResource(models.Model):
    res_type = models.IntegerField("Resource Type", choices=TYPES, default=1)
    url = models.URLField("Resource URL", max_length=200,
                          blank=True, default='')
    res_file = models.FileField(
        "Resource File", upload_to='', max_length=100, blank=True, default='')
    uid = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    status = models.IntegerField(choices=STATUS, default=1)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "secured_resource"

    def __str__(self):
        formatted_string = f"id: {self.id}, type: {self.get_string(TYPES)}, \
            status: {self.get_string(STATUS)}, date: {self.date}"
        if self.res_type == 1:
            return f"url: {self.url}, {formatted_string}"
        return f"file: {self.res_file}, {formatted_string}"

    def model(self):
        return self.SecuredResource

    @staticmethod
    def fields():
        return ('res_type', 'url', 'res_file')

    @staticmethod
    def field_password():
        return ('password',)

    def get_string(self, tuple):
        return tuple[self.res_type-1][1]


class SecuredResourceStatistics(models.Model):
    resource = models.OneToOneField(
        SecuredResource, on_delete=models.CASCADE, primary_key=True)
    date = models.DateField(auto_now_add=True)
    visited = models.IntegerField(default=0)

    class Meta:
        db_table = "secured_resource_statistics"

    def __str__(self):
        return f"{str(self.resource.id)}, type: {SecuredResource.get_string(self.resource, TYPES)}, \
            date: {self.date}, visited: {self.visited}"


@receiver(post_save, sender=User)
def create_user_stat(sender, instance, created, **kwargs):
    if created:
        UserStatistics.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_stat(sender, instance, **kwargs):
    instance.user_stat.save()
