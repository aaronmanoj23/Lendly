from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "body"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "body": forms.Textarea(attrs={"rows": 4}),
        }
