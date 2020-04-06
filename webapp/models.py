from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

STATUS = (
    ('1','Active'),
    ('2','Expired'),
)
TYPES = (
    ('1','Link'),
    ('2','File'),
)

class UserStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='userstat')
    LastUserAgent = models.CharField(max_length=200,)

class SecuredResource(models.Model):
    Type = models.CharField(max_length=2, choices=TYPES, default='1')
    URL = models.URLField(max_length=200, blank=True)
    File = models.FileField(upload_to='', max_length=100, blank=True)
    UID =  models.CharField(max_length=100)
    Password =  models.CharField(max_length=100)
    Status = models.CharField(max_length=2, choices=STATUS, default='1')
    DateTime = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id) + ' - Type:' + str(self.Type) + ' - Status:' + str(self.Status) + ' - ' + str(self.DateTime)

class SecuredResourceStatistics(models.Model):
    resource = models.OneToOneField(SecuredResource, on_delete=models.CASCADE, primary_key=True, related_name='resstat')
    Date = models.DateField(auto_now_add=True)
    Visited = models.IntegerField(default=0)
    def __str__(self):
        return str(self.resource.id) + ' - ' + 'Type:' + str(self.resource.Type) + ' - ' + 'Date:' + str(self.Date) + ' - ' + "Visited:" + str(self.Visited)


@receiver(post_save, sender=User)
def create_user_stat(sender, instance, created, **kwargs):
    if created:
        us = UserStatistics.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_stat(sender, instance, **kwargs):
    instance.userstat.save()
