from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:year>/<int:month>/', views.month, name='months'),
    path('<int:year>/<int:month>/<int:date>/',
         views.input_value,
         name='input'),
    path('income/', views.income, name='income'),
    path('create_stock/', views.create_stock, name='create_stock'),
    path('graphic/', views.graphic, name='graphic'),
    path('total/', views.total, name='total')
]
