from django import forms

from .models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "bio", "phone", "avatar", "campus"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
