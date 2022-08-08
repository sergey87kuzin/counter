from django import forms
from crum import get_current_user
from datetime import datetime as dt

from .models import Stock
from .vars import graphics, months, years
# from .vars import stocks


def get_stocks():
    stock_list = Stock.objects.filter(user=get_current_user())
    stocks = ((stock.name, stock.pseudo_name) for stock in stock_list)
    return stocks


class MonthForm(forms.Form):
    year = forms.ChoiceField(choices=years,
                             initial=dt.now().year)
    month = forms.ChoiceField(choices=months,
                              initial=dt.now().month)


class InputForm(forms.Form):
    photo = forms.IntegerField(max_value=50, min_value=0, label='Фото')
    video = forms.IntegerField(max_value=50, min_value=0, label='Видео')


class GraphicForm(forms.Form):
    stocks = get_stocks()
    # stocks = ((stock.name, stock.pseudo_name) for stock in stock_list)
    year = forms.ChoiceField(choices=years, label='Год')
    month = forms.ChoiceField(choices=months, label='Месяц')
    graphic = forms.ChoiceField(choices=graphics, label='График')
    stock = forms.ChoiceField(choices=stocks, label='Сток')


class StockForm(forms.Form):
    stocks = get_stocks()
    # stocks = ((stock.name, stock.pseudo_name) for stock in stock_list)
    date = forms.DateField(input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],
                           label='Дата',
                           localize=True)
    photo = forms.IntegerField(max_value=50,
                               min_value=0,
                               label='Фото',
                               initial=0,
                               required=False)
    video = forms.IntegerField(max_value=50,
                               min_value=0,
                               label='Видео',
                               initial=0,
                               required=False)
    income = forms.FloatField(max_value=9999,
                              label='Доход',
                              initial=0,
                              required=False)
    stock = forms.ChoiceField(choices=stocks, label='Сток')


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['name', 'pseudo_name']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        pseudo_name = cleaned_data.get('pseudo_name')
        msg_empty = 'Заполните оба поля'
        msg_name_exists = 'Сток уже существует'
        msg_pseudo_exists = 'Псевдоним уже существует'
        if not name:
            self.add_error('name', msg_empty)
        else:
            name_exists = Stock.objects.filter(name=name)
            if name_exists:
                self.add_error('name', msg_name_exists)
        if not pseudo_name:
            self.add_error('pseudo_name', msg_empty)
        else:
            pseudo_exists = Stock.objects.filter(pseudo_name=pseudo_name)
            if pseudo_exists:
                self.add_error('pseudo_name', msg_pseudo_exists)
