from django.core.validators import EMPTY_VALUES
import django_filters as filters

from swipe.models import Flat, Announcement


class EmptyStringFilter(filters.BooleanFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        exclude = self.exclude ^ (value is False)
        method = qs.exclude if exclude else qs.filter

        return method(**{self.field_name: None})


class AnnouncementFilter(filters.FilterSet):
    flat__isempty = EmptyStringFilter(field_name='flat')

    class Meta:
        model = Announcement
        fields = []