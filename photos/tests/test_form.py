# import inspect

from http import HTTPStatus
from datetime import datetime as dt

from django.test import Client, TestCase
from django.urls import reverse
# from django.forms import Form
from photos.models import Month, Day, Stock, StockCount, User
from photos.forms import (
    GraphicForm, InputForm, MonthForm, StockCreateForm, StockForm
)
# from photos.views import logger


class MonthFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        cls.year = 2022
        cls.month = 7
        cls.date = 15

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_go_to_month(self):
        """ Валидная форма пересылает на необходимую страницу """
        form_data = {
            'year': self.year,
            'month': self.month,
            'header_button': True
        }
        form = MonthForm(data=form_data)
        self.assertTrue(form.is_valid())

        urls = {'index': {},
                'months': {'year': self.year, 'month': self.month},
                'income': {},
                'create_stock': {},
                'graphic': {},
                'total': {},
                'input': {'year': self.year,
                          'month': self.month,
                          'date': self.date}}

        for key, value in urls.items():
            with self.subTest(value=value):
                response = self.authorized_client.post(
                    reverse(key, kwargs=value),
                    data=form_data,
                    follow=True,
                )

                self.assertRedirects(
                    response, reverse('months', kwargs={'year': self.year,
                                                        'month': self.month}),
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_initial(self):
        form_data = {'header_button': True}
        form = MonthForm(data=form_data)
        self.assertEqual(form.fields['year'].initial, dt.now().year)
        self.assertEqual(form.fields['month'].initial, dt.now().month)


class InputFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        cls.year = 2022
        cls.month = 7
        cls.date = 15
        cls.photo = 12
        cls.video = 15
        cls.month_obj = Month.objects.create(user=cls.user,
                                             month_list=cls.month,
                                             year_list=cls.year)
        cls.month_obj.save()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_changing_loads(self):
        """ Проверяем, вносит ли форма значения в объект Day """
        test_date = {'year': self.year, 'month': self.month, 'date': self.date}
        form1_data = {'year': self.year, 'month': self.month}
        form2_data = {'photo': self.photo, 'video': self.video}
        response = self.authorized_client.post(
                    reverse('input', kwargs=test_date),
                    data={**form1_data, **form2_data},
                    follow=True,
                )
        self.assertRedirects(
            response, reverse('months', kwargs={'year': self.year,
                                                'month': self.month}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Day.objects.filter(date=self.date,
                               month=self.month_obj,
                               photo=self.photo,
                               video=self.video).exists()
        )

    def test_labels(self):
        form = InputForm()
        self.assertEqual(form.fields['photo'].label, 'Фото')
        self.assertEqual(form.fields['video'].label, 'Видео')


class GraphicFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        cls.form = GraphicForm()
        cls.year = 2022
        cls.month = 7
        cls.date = 15

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_labels(self):
        """ проверка подписей фронтенда """
        labels = {'year': 'Год',
                  'month': 'Месяц',
                  'graphic': 'График',
                  'stock': 'Сток'}
        for key, value in labels.items():
            with self.subTest(value=value):
                self.assertEqual(self.form.fields[key].label, value)


class StockFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        cls.stock = Stock.objects.create(user=cls.user,
                                         name='Shutter',
                                         pseudo_name='Шаттер')
        cls.form = StockForm()
        cls.year = 2022
        cls.month = 7
        cls.date = 15
        cls.photo = 10
        cls.video = 10
        cls.income = 10

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_labels(self):
        """ проверка подписей фронтенда """
        labels = {'date': 'Дата',
                  'photo': 'Фото',
                  'video': 'Видео',
                  'income': 'Доход',
                  'stock': 'Сток'}
        for key, value in labels.items():
            with self.subTest(value=value):
                self.assertEqual(self.form.fields[key].label, value)

    def test_initial(self):
        """ проверка начальных значений """
        initials = {'photo': 0,
                    'video': 0,
                    'income': 0}
        for key, value in initials.items():
            with self.subTest(value=value):
                self.assertEqual(self.form.fields[key].initial, value)

    def test_create_count(self):
        """ создание и изменение данных о продажах """
        form1_data = {'year': self.year, 'month': self.month}
        form2_data = {'date': '2022-07-07',
                      'photo': self.photo,
                      'video': self.video,
                      'income': self.income,
                      'stock': self.stock.name}
        response = self.authorized_client.post(
                    reverse('income'),
                    data={**form1_data, **form2_data},
                    follow=True,
                )
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(StockCount.objects.filter(
            photo=self.photo,
            video=self.video,
            day__date=7,
            stock=self.stock,
            income=self.income
        ).exists())
        response = self.authorized_client.post(
                    reverse('income'),
                    data={**form1_data, **form2_data},
                    follow=True,
                )
        self.assertTrue(StockCount.objects.filter(
            photo=self.photo * 2,
            video=self.video * 2,
            day__date=7,
            stock=self.stock,
            income=self.income * 2
        ).exists())
        self.assertTrue(StockCount.objects.count() == 1)


class StockCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        cls.form = StockCreateForm()
        cls.year = 2022
        cls.month = 7
        cls.date = 15

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_stock(self):
        form1_data = {'year': dt.now().year, 'month': dt.now().month}
        form2_data = {'name': 'Shutter', 'pseudo_name': 'Шаттер'}
        response = self.authorized_client.post(
                    reverse('create_stock'),
                    data={**form1_data, **form2_data},
                    follow=True,
                )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(Stock.objects.filter(
            user=self.user, name='Shutter', pseudo_name='Шаттер'
        ).exists())

    def test_labels(self):
        labels = {'name': 'Сток',
                  'pseudo_name': 'Псевдоним'}
        for key, value in labels.items():
            with self.subTest(value=value):
                self.assertEqual(self.form.fields[key].label, value)

    def test_errors(self):
        form1_data = {'year': dt.now().year, 'month': dt.now().month}
        form2_data = {'name': 'Shutter', 'pseudo_name': 'Шаттер'}
        response = self.authorized_client.post(
                        reverse('create_stock'),
                        data={**form1_data, **form2_data},
                        follow=True,
                    )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = StockCreateForm(data=form2_data)
        self.assertEqual(
            form.errors['name'], ['Сток уже существует']
        )
        self.assertEqual(
            form.errors['pseudo_name'], ['Псевдоним уже существует']
        )
        form = StockCreateForm(data={})
        self.assertEqual(
            form.errors['name'],
                       ['This field is required.', 'Заполните оба поля']
        )
        self.assertEqual(
            form.errors['pseudo_name'],
                       ['This field is required.', 'Заполните оба поля']
        )

    # def test_get_class_params(self):
    #     logger.warning(
    #         inspect.getmembers(Form, lambda a: not(inspect.isroutine(a)))
    #     )
