from django import forms

from .models import Stock
from .vars import graphics, months, years

stock_list = Stock.objects.all()
stocks = ((stock.name, stock.pseudo_name) for stock in stock_list)


class MonthForm(forms.Form):
    year = forms.ChoiceField(choices=years)
    month = forms.ChoiceField(choices=months)


class InputForm(forms.Form):
    photo = forms.IntegerField(max_value=50, min_value=0, label='Photo')
    video = forms.IntegerField(max_value=50, min_value=0, label='Video')


class GraphicForm(forms.Form):
    stocks = ((stock.name, stock.pseudo_name) for stock in stock_list)
    year = forms.ChoiceField(choices=years, label='Год')
    month = forms.ChoiceField(choices=months, label='Месяц')
    graphic = forms.ChoiceField(choices=graphics, label='График')
    stock = forms.ChoiceField(choices=stocks, label='Сток')


class StockForm(forms.Form):
    stocks = ((stock.name, stock.pseudo_name) for stock in stock_list)
    date = forms.DateField(input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],
                           label='Дата',
                           localize=True)
    photo = forms.IntegerField(max_value=50,
                               min_value=0,
                               label='Фото',
                               initial=0,)
    video = forms.IntegerField(max_value=50,
                               min_value=0,
                               label='Видео',
                               initial=0,)
    income = forms.FloatField(max_value=9999,
                              label='Доход',
                              initial=0,)
    stock = forms.ChoiceField(choices=stocks, label='Сток')


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['name', 'pseudo_name']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        pseudo_name = cleaned_data.get('pseudo_name')
        msg_empty = 'Заполните оба поле'
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
