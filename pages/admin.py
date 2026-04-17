from django.contrib import admin
from .models import HistoricSite, ImportRun, SourceFeed, UserVisit


@admin.register(HistoricSite)
class HistoricSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'state', 'source_feed', 'is_verified')
    list_filter = ('category', 'state', 'source_feed', 'is_verified')
    search_fields = ('name', 'summary', 'city', 'state', 'source_name', 'source_id')


@admin.register(SourceFeed)
class SourceFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'jurisdiction_level', 'jurisdiction_name', 'source_type', 'is_active')
    list_filter = ('jurisdiction_level', 'source_type', 'is_active')
    search_fields = ('name', 'slug', 'jurisdiction_name')


@admin.register(ImportRun)
class ImportRunAdmin(admin.ModelAdmin):
    list_display = (
        'source_feed',
        'status',
        'imported_count',
        'created_count',
        'updated_count',
        'failed_count',
        'started_at',
        'finished_at',
    )
    list_filter = ('status', 'source_feed')
    search_fields = ('source_feed__name', 'notes', 'error_log')


@admin.register(UserVisit)
class UserVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'historic_site', 'visited_at')
    list_filter = ('user', 'historic_site__state', 'historic_site__category')
    search_fields = ('user__username', 'historic_site__name')
