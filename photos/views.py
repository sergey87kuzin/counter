import calendar
import datetime
import logging
from datetime import datetime as dt

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (GraphicForm, InputForm, MonthForm, StockCreateForm,
                    StockForm)
from .models import Day, Month, Stock, StockCount
from .vars import header_names
from .vars import months_list as months
from .vars import total_header

currentMonth = datetime.datetime.now().month - 1
currentYear = datetime.datetime.now().year
logger = logging.getLogger('django')


@login_required
def index(request):
    header_form = MonthForm(request.POST or None)
    logger.warning(f'Home page { dt.now() }')
    if 'header_button' in request.POST:
        return go_to_month(request, header_form)
    return render(request, 'index.html', {'month': months[currentMonth],
                                          'month_number': currentMonth,
                                          'year': currentYear,
                                          'header_form': header_form})


@login_required
def month(request, year, month):
    curr_month = get_month(user=request.user, year=year, month=month)
    days = get_days(curr_month)
    header_form = MonthForm(request.POST or None)
    if 'header_button' in request.POST:
        return go_to_month(request, header_form)
    logger.warning(f'Month { month } of { year }, days={ days }. { dt.now() }')
    return render(request, 'month.html', {'year': year,
                                          'month': months[month - 1],
                                          'header_form': header_form,
                                          'header_names': header_names,
                                          'month_obj': curr_month,
                                          'days': days})


@login_required
def input_value(request, year, month, date):
    form = InputForm(request.POST or None)
    header_form = MonthForm(request.POST or None)
    if 'header_button' in request.POST:
        return go_to_month(request, header_form)
    if form.is_valid():
        photo = form.cleaned_data['photo']
        video = form.cleaned_data['video']
        month_obj = get_month(user=request.user, year=year, month=month)
        get_days(month=month_obj)
        day = get_object_or_404(Day, month=month_obj, date=date)
        day.photo = photo
        day.video = video
        day.save()
        logger.warning(f'Input downloads: date = { date }.{ month }.{ year }'
                       f', counts: photo = { photo }, video = { video },'
                       f' income = { income }. { dt.now() }')
        return redirect('months', year=year, month=month)
    return render(request, 'income.html', {'form': form,
                                           'header_form': header_form,
                                           'year': currentYear,
                                           'month': months[currentMonth]})


@login_required
def income(request):
    form = StockForm(request.POST or None)
    form.fields['stock'].choices = get_stock_list(request)
    header_form = MonthForm(request.POST or None)
    if 'header_button' in request.POST:
        return go_to_month(request, header_form)
    if form.is_valid():
        choosen_day = form.cleaned_data['date']
        year = choosen_day.year
        month = choosen_day.month
        date = choosen_day.day
        photo = form.cleaned_data['photo']
        video = form.cleaned_data['video']
        income = form.cleaned_data['income']
        stock = Stock.objects.get(user=request.user,
                                  name=form.cleaned_data['stock'])
        month_obj = get_month(user=request.user, year=year, month=month)
        get_days(month=month_obj)
        day = Day.objects.filter(date=date, month=month_obj).last()
        count = StockCount.objects.filter(day=day,
                                          stock=stock)
        if not count:
            count = StockCount.objects.create(photo=photo,
                                              video=video,
                                              day=day,
                                              stock=stock,
                                              income=income)
            count.save()
        else:
            count[0].video += video
            count[0].photo += photo
            count[0].income += income
            count[0].save()
        logger.warning(f'changing income: { choosen_day }, video = { video }'
                       f', photo = { photo }, income = { income }.'
                       f'{ dt.now() }')
        return redirect('index')
    return render(request, 'income.html', {'form': form,
                                           'header_form': header_form,
                                           'year': currentYear,
                                           'month': months[currentMonth]})


@login_required
def create_stock(request):
    form = StockCreateForm(request.POST or None)
    header_form = MonthForm(request.POST or None)
    if 'header_button' in request.POST:
        return go_to_month(request, header_form)
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        logger.warning(f'stock created: name = { form.cleaned_data["name"] }'
                       f', pseudo_name = { form.cleaned_data["pseudo_name"] }')
        return redirect('index')
    return render(request, 'income.html', {'form': form,
                                           'header_form': header_form,
                                           'year': currentYear,
                                           'month': months[currentMonth]})


@login_required
def graphic(request):
    form = GraphicForm(request.POST or None)
    form.fields['stock'].choices = get_stock_list(request)
    header_form = MonthForm(request.POST or None)
    if 'header_button' in request.POST:
        return go_to_month(request, header_form)
    if form.is_valid():
        chosen_month = int(form.cleaned_data['month'])
        chosen_year = form.cleaned_data['year']
        graphic = form.cleaned_data['graphic']
        stock_name = form.cleaned_data['stock']
        stock = get_object_or_404(Stock,
                                  user=request.user,
                                  name=stock_name)
        month = get_month(user=request.user,
                          year=chosen_year,
                          month=chosen_month)
        if graphic == 'daily':
            result = month_graphic(month=month, stock=stock)
        elif graphic == 'monthly':
            result = year_graphic(year=chosen_year, stock=stock)
        elif graphic == 'diagram':
            result = month_diagram(request=request, month=month)
        context = {'form': form,
                   'header_form': header_form,
                   'year': currentYear,
                   'month': months[currentMonth],
                   'result': result}
        return render(request, 'graphic.html', context)
    return render(request, 'income.html', {'form': form,
                                           'header_form': header_form,
                                           'year': currentYear,
                                           'month': months[currentMonth]})


@login_required
def total(request):
    form = MonthForm(request.POST or None)
    header_form = MonthForm(request.POST or None)
    if 'header_button' in request.POST:
        return go_to_month(request, header_form)
    stocks_table = []
    labels = []
    photoes_count = []
    video_count = []
    incomes = []
    if form.is_valid():
        month = get_month(user=request.user,
                          year=form.cleaned_data['year'],
                          month=form.cleaned_data['month'])
        days = get_days(month=month)
        stock_list = Stock.objects.filter(user=request.user)
        for stock in stock_list:
            counts = get_counts(days=days, stock=stock)
            append_incomes(video_count, photoes_count, incomes, counts)
            stock_line = [stock.pseudo_name,
                          photoes_count[-1],
                          video_count[-1],
                          incomes[-1]]
            labels.append(stock.pseudo_name)
            stocks_table.append(stock_line)
        return render(request, 'total.html',
                      {'header_form': header_form,
                       'year': currentYear,
                       'month': months[currentMonth],
                       'stocks': stocks_table,
                       'header_cells': total_header,
                       'labels': labels,
                       'photo': photoes_count,
                       'video': video_count})
    return render(request, 'income.html', {'form': form,
                                           'header_form': header_form,
                                           'year': currentYear,
                                           'month': months[currentMonth]})


def get_month(user, year, month):
    curr_month = Month.objects.filter(user=user,
                                      month_list=month,
                                      year_list=year).last()
    if not curr_month:
        curr_month = Month.objects.create(user=user,
                                          month_list=month,
                                          year_list=year)
    return curr_month


def get_days(month):
    curr_days = Day.objects.filter(month=month)
    if not curr_days:
        curr_days = []
        dates = calendar.monthcalendar(year=int(month.year_list),
                                       month=int(month.month_list))
        days = [Day(date=date, month=month, photo=0, video=0)
                for week in dates for date in week]
        with transaction.atomic():
            for day in days:
                day.save()
                curr_days.append(day)
    return curr_days


def get_counts(days, stock):
    month_counts = StockCount.objects.filter(stock=stock, day__in=days)
    if not month_counts:
        counts = [StockCount(stock=stock, day=day, photo=0, video=0, income=0)
                  for day in days]
        month_counts = StockCount.objects.bulk_create(counts)
    return month_counts


def month_graphic(month, stock):
    days = get_days(month=month)
    counts = get_counts(days=days, stock=stock)
    photoes = [count.photo for count in counts]
    videos = [count.video for count in counts]
    incomes = [count.income for count in counts]
    dates = [count.day.date for count in counts]
    result = {'photoes': photoes,
              'videos': videos,
              'incomes': incomes,
              'labels': dates}
    return result


def year_graphic(year, stock):
    photoes = []
    videos = []
    incomes = []
    for month_num in range(12):
        month = get_month(user=stock.user, year=year, month=month_num + 1)
        days = get_days(month=month)
        counts = get_counts(days=days, stock=stock)
        append_incomes(videos, photoes, incomes, counts)
    labels = [months[month] for month in range(12)]
    result = {'photoes': photoes,
              'videos': videos,
              'incomes': incomes,
              'labels': labels}
    return result


def month_diagram(request, month):
    stocks = Stock.objects.filter(user=request.user)
    labels = []
    videos = []
    photoes = []
    incomes = []
    for stock in stocks:
        days = get_days(month=month)
        counts = get_counts(days=days, stock=stock)
        append_incomes(videos, photoes, incomes, counts)
        labels.append(stock.pseudo_name)
    result = {'photoes': photoes,
              'videos': videos,
              'incomes': incomes,
              'labels': labels}
    return result


def go_to_month(request, header_form):
    if header_form.is_valid():
        logger.warning('redirect to month')
        return redirect('months',
                        int(header_form.cleaned_data['year']),
                        int(header_form.cleaned_data['month']))


def get_stock_list(request):
    stock_list = Stock.objects.filter(user=request.user)
    stocks = ((stock.name, stock.pseudo_name) for stock in stock_list)
    return stocks


def append_incomes(videos, photoes, incomes, counts):
    photoes.append(sum([int(count.photo) for count in counts]))
    videos.append(sum([int(count.video) for count in counts]))
    incomes.append(sum([float(count.income) for count in counts]))
