from django_filters import rest_framework as filters

from .models import Speed


class SpeedFilter(filters.FilterSet):

    class Meta:
        model = Speed
        fields = [
            'is_public', 
            'speed_type', 
            'user__username',
            ]