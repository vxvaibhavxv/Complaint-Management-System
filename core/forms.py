from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User = get_user_model()

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput)
    password_2 = forms.CharField(label = "Confirm Password", widget = forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "firstName", "lastName", "isAdmin", "isManager", "active", "isSuperuser", "slug"]

    def clean(self):
        cleanedData = super().clean()
        password = cleanedData.get("password")
        password_2 = cleanedData.get("password_2")

        if password is None:
            self.add_error("password", "Password is empty")

        if password_2 is None:
            self.add_error("password_2", "Confirm password is empty")

        if password is not None and password != password_2:
            self.add_error("password_2", "Passwords don't match")

        return cleanedData

    def save(self, commit = True):
        user = super().save(commit = False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user

class UserEditForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    slug = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "password", "firstName", "lastName", "isAdmin", "isManager", "active", "isSuperuser", "slug"]
    def clean_password(self):
        return self.initial["password"]