from datetime import datetime as dt

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from photos.models import Day, Month, Stock, StockCount, User
from photos.vars import months_list as months
from photos.views import get_days


class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Anon')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.month_no = 8
        cls.year = 2022
        cls.photo = 3
        cls.video = 5
        cls.income = 10
        cls.month = Month.objects.create(user=cls.user,
                                         year_list=cls.year,
                                         month_list=cls.month_no)
        cls.next_month = Month.objects.create(
            user=cls.user, year_list=cls.year, month_list=cls.month_no + 1)
        cls.days = get_days(cls.month)
        get_days(cls.next_month)
        cls.stock = Stock.objects.create(
            user=cls.user, name='Pond5', pseudo_name='Pond5'
        )
        cls.date = 15
        cls.day = Day.objects.get(date=cls.date, month=cls.month)
        StockCount.objects.create(
            photo=cls.photo, video=cls.video, day=cls.day,
            stock=cls.stock, income=cls.income
        )
        cls.next_day = Day.objects.get(date=cls.date, month=cls.next_month)
        StockCount.objects.create(
            photo=cls.photo, video=cls.video, day=cls.next_day,
            stock=cls.stock, income=cls.income
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('index'): 'index.html',
            reverse('months', kwargs={'year': self.year,
                                      'month': self.month_no}): 'month.html',
            reverse('income'): 'income.html',
            reverse('input', kwargs={'year': self.year,
                                     'month': self.month_no,
                                     'date': self.date}): 'income.html',
            reverse('create_stock'): 'income.html',
            reverse('graphic'): 'income.html',
            reverse('total'): 'income.html'
        }

        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)

                self.assertTemplateUsed(response, template)

    def test_page_show_correct_form_fields(self):
        """Шаблон сформирован с правильным набором полей в формах."""
        rev_names = {reverse('input', kwargs={'year': self.year,
                                              'month': self.month_no,
                                              'date': self.date}):
                     {'photo': forms.fields.IntegerField,
                      'video': forms.fields.IntegerField},
                     reverse('income'):
                     {'date': forms.fields.DateField,
                      'photo': forms.fields.IntegerField,
                      'video': forms.fields.IntegerField,
                      'income': forms.fields.FloatField,
                      'stock': forms.fields.ChoiceField},
                     reverse('create_stock'):
                     {'name': forms.fields.CharField,
                      'pseudo_name': forms.fields.CharField},
                     reverse('graphic'):
                     {'year': forms.fields.ChoiceField,
                      'month': forms.fields.ChoiceField,
                      'graphic': forms.fields.ChoiceField,
                      'stock': forms.fields.ChoiceField},
                     reverse('total'):
                     {'year': forms.fields.ChoiceField,
                      'month': forms.fields.ChoiceField}}

        for rev_name, fields in rev_names.items():
            with self.subTest():
                response = self.authorized_client.get(rev_name)
                for value, expected in fields.items():
                    with self.subTest(value=value):
                        model_field = response.context['form'].fields[value]
                        self.check_header(response)
                        self.assertIsInstance(model_field, expected)

    def test_home_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        resp = self.authorized_client.get(reverse('index'))
        month_no = resp.context['month_number']

        self.assertEqual(month_no, dt.now().month - 1)

    def test_month_page_show_correct_context(self):
        """Шаблон month сформирован с правильным контекстом."""
        resp = self.authorized_client.get(
            reverse('months', kwargs={'year': self.year,
                                      'month': self.month_no})
        )
        month_obj = resp.context['month_obj']
        days = list(resp.context['days'])

        self.assertEqual(month_obj, self.month)
        self.assertListEqual(days, self.days)

    def test_post_request_to_graphic_page(self):
        graphics = {'daily': (0, self.date),
                    'monthly': (self.month_no, months[self.month_no]),
                    'diagram': (0, self.stock.pseudo_name)}
        data1_form = {'year': self.year, 'month': self.month_no}
        for graphic, index in graphics.items():
            with self.subTest():
                data2_form = {'year': self.year,
                              'month': self.month_no,
                              'graphic': graphic,
                              'stock': self.stock.name}
                data = {**data1_form, **data2_form}
                response = self.authorized_client.post(
                    reverse('graphic'), data=data, follow=True
                )
                form = response.context['form']
                self.assertTrue(form.is_valid())
                result = response.context['result']
                self.assertEqual(result['photoes'][index[0]], self.photo)
                self.assertEqual(result['videos'][index[0]], self.video)
                self.assertEqual(result['incomes'][index[0]], self.income)
                self.assertEqual(result['labels'][index[0]], index[1])

    def test_post_request_to_total_page(self):
        data_form = {'year': self.year, 'month': self.month_no}
        data = {**data_form, **data_form}
        response = self.authorized_client.post(
            reverse('total'), data=data, follow=True
        )
        self.assertEqual(
            response.context['stocks'][0][0], self.stock.pseudo_name
        )
        self.assertEqual(
            response.context['stocks'][0][1], self.photo
        )
        self.assertEqual(
            response.context['stocks'][0][2], self.video
        )
        self.assertEqual(
            response.context['stocks'][0][3], self.income
        )
        self.assertEqual(
            response.context['labels'][0], self.stock.pseudo_name
        )
        self.assertEqual(
            response.context['photo'][0], self.photo
        )
        self.assertEqual(
            response.context['video'][0], self.video
        )

    def check_header(self, response):
        month_name = response.context['month']
        year = response.context['year']
        self.assertIsInstance(
            response.context['header_form'].fields['month'],
            forms.fields.ChoiceField
        )
        self.assertIsInstance(
            response.context['header_form'].fields['year'],
            forms.fields.ChoiceField
        )
        self.assertEqual(month_name, months[self.month_no])
        self.assertEqual(year, dt.now().year)
