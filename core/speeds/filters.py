from django.utils.datastructures import MultiValueDict
from django_filters import rest_framework as filters, widgets
from django.contrib import admin

from rest_framework.exceptions import APIException

from .models import Speed, SpeedFeedback, SpeedBookmark
from .validators import tags_validator
from core.users.validators import username_validator


class CustomQueryArrayWidget(widgets.QueryArrayWidget):
    def value_from_datadict(self, data, files, name) -> list:
        """
        Allows the passing of tags in query parameters using either
        of the following formats:
        - .../?tags=one,seven
        - .../?tags=one&tags=seven
        """

        # source code: leave it as is just in case;
        # it appears that it won't ever run as the `data` should be always a QueryDict
        if not isinstance(data, MultiValueDict):
            data = data.copy()
            for key, value in data.items():
                # treat value as csv string: ?foo=1,2
                if isinstance(value, str):
                    data[key] = [
                        x.strip() for x in value.rstrip(",").split(",") if x
                    ]
            data = MultiValueDict(data)

        values_list = data.getlist(name, data.getlist("%s[]" % name)) or []

        # add the following `if` statement
        if len(values_list) == 1:
            if isinstance(values_list[0], str) and len(values_list[0]) > 0:
                ret = values_list[0].lower().split(",")
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
        method="tags_filter",
        label="Speed tags, comma separated (example: `tag1,tag2,tag3`):",
    )
    user = filters.CharFilter(
        method="user_filter",
        label="Username of the user:",
    )

    class Meta:
        model = Speed
        fields = ["is_public", "speed_type", "user", "tags"]

    def tags_filter(self, queryset, name: str, value: list[str]):
        tags_validator(value, max_length=4)
        return queryset.filter(tags__contains=value)

    def user_filter(self, queryset, name, value):
        try:
            username_validator(value)
        except Exception as e:
            raise APIException(str(e))
        return queryset.filter(user__username=value)


class SpeedFeedbackFilter(filters.FilterSet):
    speed = filters.UUIDFilter()

    class Meta:
        model = SpeedFeedback
        fields = ["speed"]


class SpeedBookmarkFilter(filters.FilterSet):
    speed = filters.UUIDFilter()

    class Meta:
        model = SpeedBookmark
        fields = ["speed"]


class ReportsCountFilter(admin.SimpleListFilter):
    title = "Reports Count"
    parameter_name = "reports_count"

    def lookups(self, request, model_admin):
        return [
            ("10", "reports count >= 10"),
            ("4", "reports count >= 4"),
            ("1", "reports count >= 1"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "1":
            return queryset.filter(reports_count__gte=1)
        elif value == "4":
            return queryset.filter(reports_count__gte=4)
        elif value == "10":
            return queryset.filter(reports_count__gte=10)

        return queryset
