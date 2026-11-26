
from django.contrib.auth.forms import UserCreationForm

from .models import User


class WarriWorksAdminUserCreationForm(UserCreationForm):
    """
    Creates staff administrator accounts without granting superuser access.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "username")

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = False

        if commit:
            user.save()

        return user
