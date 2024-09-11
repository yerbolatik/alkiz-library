from django import forms
from reviews.models import Review, Rating


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
