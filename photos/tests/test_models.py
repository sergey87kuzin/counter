from django.test import TestCase
from photos.models import (Day, Month, Stock, User,)


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Anon')
        cls.month = Month.objects.create(
            user=cls.user, month_list=7, year_list=2022
        )
        cls.day = Day.objects.create(
            date=15, month=cls.month, photo=3, video=5
        )
        cls.stock = Stock.objects.create(
            user=cls.user, name='qwe', pseudo_name='qwe'
        )
        cls.stock.day.set([cls.day, ])

    def test_month_verbose_names(self):
        """verbose_name в полях Month совпадает с ожидаемым."""
        month = self.month
        field_verboses = {
            'user': 'Пользователь',
            'month_list': 'месяц',
            'year_list': 'год',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):

                self.assertEqual(
                    month._meta.get_field(value).verbose_name, expected)

    def test_day_verbose_names(self):
        """verbose_name в полях Day совпадает с ожидаемым."""
        day = self.day
        field_verboses = {
            'date': 'День месяца',
            'month': 'Месяц',
            'photo': 'Фото',
            'video': 'Видео',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):

                self.assertEqual(
                    day._meta.get_field(value).verbose_name, expected)

    def test_stock_verbose_names(self):
        """verbose_name в полях Stock совпадает с ожидаемым."""
        stock = self.stock
        field_verboses = {
            'user': 'Пользователь',
            'name': 'Сток',
            'pseudo_name': 'Псевдоним',
            'day': 'Дата',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):

                self.assertEqual(
                    stock._meta.get_field(value).verbose_name, expected)
