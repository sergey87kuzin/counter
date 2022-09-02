from django import forms

from .models import Stock


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Заполните поле',
            params={'value': value},
        )


def validate_stock(value):
    name_exists = Stock.objects.filter(name=value)
    pseudo_exists = Stock.objects.filter(pseudo_name=value)
    if name_exists or pseudo_exists:
        raise forms.ValidationError(
            'Сток уже существует',
            params={'value': value})
