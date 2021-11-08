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
    price__gt = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lt = filters.NumberFilter(field_name='price', lookup_expr='lte')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    total_area__gt = filters.NumberFilter(field_name='total_area', lookup_expr='gte')
    total_area__lt = filters.NumberFilter(field_name='total_area', lookup_expr='lte')

    class Meta:
        model = Announcement
        fields = ['calculation_options', 'state', 'rooms', 'appointment', 'flat__house__status']


class FlatFilter(filters.FilterSet):
    square_meter_price__gt = filters.NumberFilter(field_name='square_meter_price', lookup_expr='gte')
    square_meter_price__lt = filters.NumberFilter(field_name='square_meter_price', lookup_expr='lte')

    class Meta:
        model = Flat
        fields = ['house__id', 'status']