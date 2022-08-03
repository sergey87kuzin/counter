import calendar
import datetime as dt

from django.db import models
from django.contrib.auth import get_user_model

from .vars import months_list as months


User = get_user_model()


class Month(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='month')
    month_list = models.IntegerField(verbose_name='месяц',
                                     blank=False,
                                     null=False)
    year_list = models.IntegerField(verbose_name='год',
                                    blank=False,
                                    null=False)

    def __str__(self):
        return f'{months[self.month_list - 1]} {self.year_list}'


class Day(models.Model):
    date = models.IntegerField(verbose_name='День месяца',
                               blank=True,
                               null=True)
    month = models.ForeignKey(Month,
                              on_delete=models.CASCADE,
                              verbose_name='Месяц',
                              related_name='month')
    photo = models.IntegerField(verbose_name='Фото', blank=True, null=True)
    video = models.IntegerField(verbose_name='Видео', blank=True, null=True)

    def __str__(self):
        return (f'{self.date} {months[self.month.month_list - 1]}'
                f'{self.month.year_list}')


def get_today():
    year = dt.datetime.today().year
    month = dt.datetime.today().month
    curr_month = Month.objects.filter(year_list=year,
                                      month_list=month)
    if not curr_month:
        curr_month = Month.objects.create(month_list=month,
                                          year_list=year)
    month_days = Day.objects.filter(month=curr_month)
    if not month_days:
        dates = calendar.monthcalendar(year=year,
                                       month=month)
        days = [Day(date=date, month=month, photo=0, video=0)
                for week in dates for date in week]
        month_days = Day.objects.bulk_create(days)
    today = Day.objects.filter(date=dt.datetime.today().date, month=curr_month)
    return today


class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='stock')
    name = models.CharField(verbose_name='Сток',
                            max_length=32)
    pseudo_name = models.CharField(verbose_name='Псевдоним',
                                   max_length=32,
                                   default='Новый сток')
    day = models.ManyToManyField('Day',
                                 related_name='stock_day',
                                 through='StockCount',
                                 verbose_name='Дата',
                                 blank=True)

    def __str__(self):
        return self.pseudo_name


class StockCount(models.Model):
    stock = models.ForeignKey('Stock',
                              on_delete=models.CASCADE,
                              related_name='stock',
                              verbose_name='Сток')
    day = models.ForeignKey('Day',
                            on_delete=models.CASCADE,
                            related_name='stock_count_day',
                            verbose_name='Дата')
    photo = models.PositiveIntegerField(verbose_name='Фото',
                                        blank=True,
                                        null=True)
    video = models.PositiveIntegerField(verbose_name='Видео',
                                        blank=True,
                                        null=True)
    income = models.FloatField(verbose_name='Доход',
                               blank=True,
                               null=True)
