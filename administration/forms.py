from typing import Any
from django import forms

from administration.models import AffiliateRegisterInstance
from ecommerce.models.administration import (
    AdministrativeProfile,
    AdministrativeUser,
    NonAdministrativeUsers,
)
from ecommerce.models.affiliate import Affiliate
from ecommerce.models.modality import Modality
from ecommerce.models.quotation import Quotation
from ecommerce.utils.consts import CommissionEnum
from payment.models import WithDrawRequest


class BackofficeLoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Usuário")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")


class AffiliateForm(forms.ModelForm):
    quotations = forms.ModelMultipleChoiceField(
        label="Cotações",
        queryset=Quotation.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Confirmação de senha"
    )

    def __init__(self, *args, **kwargs):
        user: AdministrativeUser = kwargs.pop("user")
        super(AffiliateForm, self).__init__(*args, **kwargs)
        possible_parents = user.get_possible_parents_to_user(
            NonAdministrativeUsers.AFFILIATE
        )
        if user.profile != AdministrativeProfile.ADMIN:
            self.fields["quotations"].widget = forms.HiddenInput()
        self.fields["user_above"].widget = forms.Select(attrs={"class": "form-control"})
        self.fields["user_above"].label = "Gerente"
        self.fields["commission"].widget = forms.Select(attrs={"class": "form-control"})
        self.fields["commission"].label = "Comissão"
        self.fields["commission"].choices = CommissionEnum.choices
        if possible_parents.count() == 1:
            self.fields["user_above"].initial = possible_parents.first()
            self.fields["user_above"].widget = forms.HiddenInput()
        self.fields["user_above"].queryset = user.get_possible_parents_to_user(
            NonAdministrativeUsers.AFFILIATE
        )
        self.fields["password"].widget = forms.PasswordInput()
        self.fields["user_above"].initial = user

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password != password2:
            self.add_error("password2", "As senhas não conferem")
        return cleaned_data

    class Meta:
        model = Affiliate
        fields = [
            "username",
            "name",
            "phone",
            "email",
            "cpf",
            "quotations",
            "commission",
            "user_above",
            "password",
            "password2",
        ]


class AffiliateEditForm(forms.ModelForm):
    quotations = forms.ModelMultipleChoiceField(
        label="Cotações",
        queryset=Quotation.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Confirmação de senha", required=False
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        user: AdministrativeUser = kwargs.pop("user")
        super(AffiliateEditForm, self).__init__(*args, **kwargs)
        possible_parents = user.get_possible_parents_to_user(
            NonAdministrativeUsers.AFFILIATE
        )
        if user.profile != AdministrativeProfile.ADMIN:
            self.fields["quotations"].widget = forms.HiddenInput()
        if possible_parents.count() == 1:
            self.fields["user_above"].initial = possible_parents.first()
            self.fields["user_above"].widget = forms.HiddenInput()
        self.fields["user_above"].queryset = user.get_possible_parents_to_user(
            NonAdministrativeUsers.AFFILIATE
        )
        self.fields["password"].widget = forms.PasswordInput()
        self.fields["password"].required = False
        self.fields["quotations"].initial = instance.quotations.all()

    class Meta:
        model = Affiliate
        fields = [
            "username",
            "name",
            "phone",
            "email",
            "cpf",
            "quotations",
            "commission",
            "user_above",
            "password",
            "password2",
        ]


class ChangePasswordForm(forms.Form):
    MIN_LENGTH = 8
    current_password = forms.CharField(widget=forms.PasswordInput, label="Senha atual")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Confirmação de senha"
    )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password != password2:
            self.add_error("password2", "As senhas não conferem")
        if len(password) < self.MIN_LENGTH:
            self.add_error(
                "password", f"A senha deve ter no mínimo {self.MIN_LENGTH} caracteres"
            )
        return cleaned_data


class AdministrativeUserCreateForm(forms.ModelForm):
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Confirmação de senha"
    )

    def __init__(self, *args, **kwargs):
        user: AdministrativeUser = kwargs.pop("user")
        new_user_profile = kwargs.pop("new_user_profile")
        super(AdministrativeUserCreateForm, self).__init__(*args, **kwargs)
        possible_parents = user.get_possible_parents_to_user(new_user_profile)
        possible_parents_choices = [
            (parent.id, str(parent.username)) for parent in possible_parents
        ]
        self.fields["parent"].widget = forms.Select(attrs={"class": "form-control"})
        self.fields["parent"].choices = possible_parents_choices
        self.fields["parent"].label = "Supervisor"
        if len(possible_parents_choices) == 1:
            self.fields["parent"].initial = possible_parents_choices[0]
        self.fields["password"].widget = forms.PasswordInput()
        self.fields["profile"].initial = new_user_profile
        self.fields["profile"].widget = forms.HiddenInput()

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password != password2:
            self.add_error("password2", "As senhas não conferem")
        return cleaned_data

    class Meta:
        model = AdministrativeUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
            "parent",
            "password",
            "password2",
        ]


class AdministrativeUserEditForm(forms.ModelForm):
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Confirmação de senha", required=False
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        user: AdministrativeUser = kwargs.pop("user")
        super(AdministrativeUserEditForm, self).__init__(*args, **kwargs)
        possible_parents = user.get_possible_parents_to_user(instance.profile)
        self.fields["parent"].widget = forms.Select(attrs={"class": "form-control"})
        self.fields["parent"].choices = [
            (parent.id, str(parent.username)) for parent in possible_parents
        ]
        if user.profile != AdministrativeProfile.ADMIN:
            self.fields["percent"].disabled = True
            self.fields["percent"].widget = forms.HiddenInput()
        if possible_parents.count() == 1:
            self.fields["parent"].initial = (
                possible_parents.first().id,
                str(possible_parents.first().username),
            )
            self.fields["parent"].widget = forms.HiddenInput()
        self.fields["password"].widget = forms.PasswordInput()
        self.fields["password"].required = False

    class Meta:
        model = AdministrativeUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "parent",
            "password",
            "password2",
            "percent",
        ]


class WithDrawRequestForm(forms.ModelForm):
    class Meta:
        model = WithDrawRequest
        fields = [
            "status",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class ModalityForm(forms.ModelForm):

    class Meta:
        model = Modality
        fields = [
            "max_len_input_guess",
            "min_len_input_guess",
            "max_quantity_guess",
            "max_guess_value",
            "max_bet_value",
            "min_bet_value",
            "is_active",
        ]


class NewAffiliateLinkForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user: AdministrativeUser = kwargs.pop("user")
        super(NewAffiliateLinkForm, self).__init__(*args, **kwargs)
        self.fields["manager"].widget = forms.Select(attrs={"class": "form-control"})
        self.fields["manager"].queryset = user.get_possible_parents_to_user(
            NonAdministrativeUsers.AFFILIATE
        )
        if user.profile == AdministrativeProfile.MANAGER:
            self.fields["manager"].disable = True
            self.fields["manager"].initial = user
            self.fields["manager"].widget = forms.HiddenInput()

    class Meta:
        model = AffiliateRegisterInstance
        fields = [
            "manager",
            "max_registrations",
        ]


class RegisterAffiliateForm(forms.ModelForm):
    name = forms.CharField()
    phone = forms.CharField()
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, label="Confirmação de senha"
    )

    def __init__(self, *args, **kwargs):
        register_intance = kwargs.pop("register_instance")
        super(RegisterAffiliateForm, self).__init__(*args, **kwargs)
        self.fields["password"].widget = forms.PasswordInput()
        self.fields["user_above"].initial = register_intance.manager
        self.fields["user_above"].widget = forms.HiddenInput()

    def validate(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("confirm_password")
        if password != password2:
            self.add_error("confirm_password", "As senhas não conferem")
        return cleaned_data

    class Meta:
        model = Affiliate
        fields = [
            "username",
            "name",
            "email",
            "cpf",
            "password",
            "confirm_password",
            "phone",
            "user_above",
        ]
