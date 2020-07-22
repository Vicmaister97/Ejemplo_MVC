from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst


class UserLoginForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Username/password is not valid"),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(UserLoginForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        userfield = UserModel.USERNAME_FIELD
        self.username_field = UserModel._meta.get_field(userfield)
        if self.fields['username'].label is None:
            verb_name = self.username_field.verbose_name
            self.fields['username'].label = capfirst(verb_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class SignupForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'pass_mismatch': _("Password and Repeat password are not the same"),
        'pw_length': _("Password is too short.\
                        Password must at least 6 characters\
                        and must not be too common.")
    }
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above,\
                                             for verification."))

    class Meta:
        model = User
        fields = ("username",)

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError(
                self.error_messages['pass_mismatch'],
                code='pass_mismatch',
            )
        if len(password2) < 7:
            raise forms.ValidationError(
                self.error_messages['pw_length'],
                code='pw_length',
            )
        return password2

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class MoveForm(forms.Form):
    error_messages = {
        'origen_problem': _("Origin square is not valid."),
        'target_problem': _("Target square is not valid.")
    }

    origin = forms.IntegerField()
    target = forms.IntegerField()

    def clean(self):
        origin = self.cleaned_data.get('origin')
        target = self.cleaned_data.get('target')
        if (origin > 63) or (origin < 0):
            raise forms.ValidationError(
                self.error_messages['origen_problem'],
                code='origen_problem',
            )
        if (target > 63) or (target < 0):
            raise forms.ValidationError(
                self.error_messages['target_problem'],
                code='target_problem',
            )
        return self.cleaned_data
