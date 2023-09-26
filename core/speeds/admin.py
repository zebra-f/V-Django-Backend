from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .models import Speed, SpeedFeedback, SpeedBookmark, SpeedReport
from .queries import SpeedQueries
from .filters import ReportsCountFilter


class SpeedAdmin(admin.ModelAdmin):
    list_per_page = 20
    readonly_fields = [
        'id',
        'user', 
        'downvotes', 
        'upvotes', 
        'score',
        'created_at',
    ]
    list_display = [
        'id',
        'user',
        'downvotes',
        'upvotes',
        'score',
        'updated_at',
        'reports_count'
    ]
    search_fields = [
        'user__username',
    ]
    list_filter = [
        'created_at',
        ReportsCountFilter,
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return SpeedQueries.get_admin_site_query()
    
    def reports_count(self, obj):
        return obj.reports_count


class SpeedFeedbackAdmin(admin.ModelAdmin):
    list_per_page = 20
    readonly_fields = [
        'id', 
        'user',
        'speed',
        'created_at',
    ]
    list_display = [
        'id',
        'user',
        'speed',
    ]

    def has_add_permission(self, request, obj=None):
        return False


class SpeedBookmarkAdmin(admin.ModelAdmin):
    list_per_page = 20
    readonly_fields = [
        'id', 
        'user',
        'speed',
        'created_at',
    ]
    list_display = [
        'id',
        'user',
        'speed',
    ]

    def has_add_permission(self, request, obj=None):
        return False
    

class SpeedReportAdmin(admin.ModelAdmin):
    list_per_page = 20
    readonly_fields = [
        'id', 
        'user',
        'speed',
        'created_at',
    ]
    list_display = [
        'id',
        'user',
        'speed',
    ]

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Speed, SpeedAdmin)
admin.site.register(SpeedFeedback, SpeedFeedbackAdmin)
admin.site.register(SpeedBookmark, SpeedBookmarkAdmin)
admin.site.register(SpeedReport, SpeedReportAdmin)