from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

from .models import Campus


class EduOnlyAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        email = super().clean_email(email)
        if not email.lower().endswith(".edu"):
            raise ValidationError("Signup requires a .edu email address.")
        return email

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        domain = user.email.split("@")[-1].lower()
        campus = Campus.objects.filter(email_domain__iexact=domain).first()
        if campus:
            user.campus = campus
        if commit:
            user.save()
        return user
