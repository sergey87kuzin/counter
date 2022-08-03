from django.contrib import admin

from .models import Day, Month, Stock, StockCount


class MonthAdmin(admin.ModelAdmin):
    list_display = ('year_list', 'month_list')
    search_fields = ('year_list',)
    list_filter = ('year_list',)
    empty_value_display = '-пусто-'


class DayAdmin(admin.ModelAdmin):
    list_display = ('month', 'date', 'photo', 'video')


class StockAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'pseudo_name',)


class StockCountAdmin(admin.ModelAdmin):
    list_display = ('stock', 'day', 'photo', 'video', 'income')


admin.site.register(Month, MonthAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(StockCount, StockCountAdmin)
