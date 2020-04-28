from django import forms

from .functions import (get_secured_resource_model, save_secured_resource,
                        validate_secured_resource)


class SecuredResourceForm(forms.ModelForm):

    class Meta:
        model = get_secured_resource_model()
        fields = model.fields()

    def secured_resource_form(self, save=True):
        secured_resource = super(SecuredResourceForm, self)
        if save:
            return secured_resource.save(commit=False)
        return secured_resource.clean()

    def clean(self):
        # get the cleaned data from default clean, returns cleaned_data
        cleaned_data = SecuredResourceForm.secured_resource_form(
            self, save=False)

        validate_secured_resource(cleaned_data)
        return cleaned_data

    def save(self, user=None):
        secured_resource = self.secured_resource_form(self)
        return save_secured_resource(secured_resource)


class PasswordForm(forms.ModelForm):
    class Meta:
        model = get_secured_resource_model()
        fields = model.field_password()

    def save(self, user=None):
        return self.secured_resource_form(self)
