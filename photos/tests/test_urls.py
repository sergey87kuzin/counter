from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from photos.models import Day, Month, Stock

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NeAnon')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.year = 2022
        cls.month_no = 7
        cls.date = 15
        cls.month = Month.objects.create(
            user=cls.user, month_list=cls.month_no, year_list=cls.year
        )
        cls.day = Day.objects.create(
            date=cls.date, month=cls.month, photo=3, video=5
        )
        cls.stock = Stock.objects.create(
            user=cls.user, name='qwe', pseudo_name='qwe'
        )
        cls.stock.day.set([cls.day, ])

    def setUp(self):
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        """Доступ к страницам неавторизованного пользователя"""
        url_names = {
            '/': HTTPStatus.FOUND,
            f'/{ self.year }/{ self.month_no }/': HTTPStatus.FOUND,
            f'/{ self.year }/{ self.month_no }/{ self.date }/':
            HTTPStatus.FOUND,
            '/income/': HTTPStatus.FOUND,
            '/create_stock/': HTTPStatus.FOUND,
            '/graphic/': HTTPStatus.FOUND,
            '/total/': HTTPStatus.FOUND,
        }

        for url_name, page_code in url_names.items():
            with self.subTest():
                response = self.guest_client.get(url_name)

                self.assertEqual(
                    response.status_code, page_code, msg=url_name
                )

    def test_authorized_url_exists_at_desired_location(self):
        """Страницы доступны авторизованному пользователю."""
        url_names = {
            '/': HTTPStatus.OK,
            f'/{ self.year }/{ self.month_no }/': HTTPStatus.OK,
            f'/{ self.year }/{ self.month_no }/{ self.date }/': HTTPStatus.OK,
            '/income/': HTTPStatus.OK,
            '/create_stock/': HTTPStatus.OK,
            '/graphic/': HTTPStatus.OK,
            '/total/': HTTPStatus.OK,
        }

        for url_name, page_code in url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url_name)

                self.assertEqual(
                    response.status_code, page_code, msg=url_name
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            f'/{ self.year }/{ self.month_no }/': 'month.html',
            f'/{ self.year }/{ self.month_no }/{ self.date }/': 'income.html',
            '/income/': 'income.html',
            '/create_stock/': 'income.html',
            '/graphic/': 'income.html',
            '/total/': 'income.html'
        }

        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)

                self.assertTemplateUsed(
                    response, template, msg_prefix=reverse_name
                )
