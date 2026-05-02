from django import forms

from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "category",
            "condition",
            "price_per_day",
            "deposit",
            "campus",
            "location_note",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
