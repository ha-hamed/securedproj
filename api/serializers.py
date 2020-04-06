from rest_framework import serializers
from webapp import models

class SecuredResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SecuredResource
        fields = ('Type', 'URL', 'File')

class GetSecuredResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SecuredResource
        fields = ('Type', 'URL', 'File', 'UID', 'Password')

class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
