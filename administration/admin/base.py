from typing import TYPE_CHECKING
from django import forms
from django.contrib import admin

if TYPE_CHECKING:
    from ecommerce.models import AdministrativeUser


class AdminstrationAdminFormBase(forms.ModelForm):
    current_user: "AdministrativeUser"


class AdministrationAdminBase(admin.ModelAdmin):
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
