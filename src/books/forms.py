from django import forms
from .models import Book, Author, Language, Category


AVAILABLE_CHOICES = [
    ('all', 'Все'),
    ('available', 'Доступные'),
    ('not_available', 'Не доступные'),
]


class BookFilterForm(forms.Form):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(), required=False, label="Автор")
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, label="Категория")
    language = forms.ModelChoiceField(
        queryset=Language.objects.all(), required=False, label="Язык")
    available = forms.ChoiceField(
        choices=AVAILABLE_CHOICES,
        required=False,
        label="Доступно"
    )
