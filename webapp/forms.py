from . import models
from django import forms

import secrets
import string
import datetime

class SecuredResourceForm(forms.ModelForm):
    class Meta:
        model = models.SecuredResource
        fields = ('Type','URL', 'File')

    def save(self, user=None):
        SecuredResource = super(SecuredResourceForm, self).save(commit=False)

        res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(50)) # Generate Cryptographically Secure Random String
        p = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(10)) # Generate Cryptographically Secure Random String

        if(SecuredResource.Type == "1"):
            SecuredResource.File = ""
        else:
            SecuredResource.URL= ""

        SecuredResource.UID = res
        SecuredResource.Password = p
        SecuredResource.save()

        # Create SecuredResourceStatistics Object for newly saved resource if it is not already created for a given date.
        if(models.SecuredResourceStatistics.objects.filter(Date=datetime.date.today(), resource=SecuredResource).count() > 0 ):
            pass
        else:
            rs = models.SecuredResourceStatistics(Date=datetime.date.today(), resource=SecuredResource)
            rs.save()
        return SecuredResource

class PasswordForm(forms.ModelForm):
    class Meta:
        model = models.SecuredResource
        fields = ('Password',)

    def save(self, user=None):
        SR = super(SecuredResourceForm, self).save(commit=False)
        return SR
