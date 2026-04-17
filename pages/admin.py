from django.contrib import admin
from .models import HistoricSite


@admin.register(HistoricSite)
class HistoricSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'state', 'is_verified')
    list_filter = ('category', 'state', 'is_verified')
    search_fields = ('name', 'summary', 'city', 'state', 'source_name')
