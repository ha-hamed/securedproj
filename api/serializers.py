from rest_framework import serializers
from webapp.functions import (get_secured_resource_model,
                              validate_secured_resource)


class SecuredResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_secured_resource_model()
        fields = model.fields()

    def validate(self, data):
        validate_secured_resource(data, True)
        return data


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_secured_resource_model()
        fields = model.field_password()
