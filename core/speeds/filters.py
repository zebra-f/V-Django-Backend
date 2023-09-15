from django.utils.datastructures import MultiValueDict
from django_filters import rest_framework as filters, widgets

from .models import Speed
from .validators import tags_validator


class CustomQueryArrayWidget(widgets.QueryArrayWidget):

    def value_from_datadict(self, data, files, name):
        # source code: leave it as is just in case; 
        # it appears that it won't ever run as the `data` should be always a QueryDict
        if not isinstance(data, MultiValueDict):
            data = data.copy()
            for key, value in data.items():
                # treat value as csv string: ?foo=1,2
                if isinstance(value, str):
                    data[key] = [x.strip() for x in value.rstrip(",").split(",") if x]
            data = MultiValueDict(data)

        values_list = data.getlist(name, data.getlist("%s[]" % name)) or []

        # add the following `if` statement
        if len(values_list) == 1:
            if isinstance(values_list[0], str):
                ret = values_list[0].lower().split(',')
            else:
                ret = []
        # replace the `if len(values_list) > 0` with the following line
        elif len(values_list) > 1:
            # add `.lower()` method to the following line
            # add `and isinstance(x, str)` to the following line
            ret = [x.lower() for x in values_list if x and isinstance(x, str)]  
        else:
            ret = []
        return list(set(ret))


class SpeedFilter(filters.FilterSet):
    tags = filters.Filter(
        widget=CustomQueryArrayWidget,
        method='tags_filter',
        label='Speed tags, comma separated (example: `tag1,tag2,tag3`):'
    )

    class Meta:
        model = Speed
        fields = [
            'is_public', 
            'speed_type', 
            'user__username',
            'tags'
            ]
        
    def tags_filter(self, queryset, name: str, value: list):
        tags_validator(value, max_length=4)
        return queryset.filter(tags__contains=value)