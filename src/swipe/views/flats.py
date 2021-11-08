import logging
from django.utils.decorators import method_decorator
from django_filters.rest_framework.backends import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from swipe.filters import FlatFilter

from swipe.models import (Flat, House, DeveloperHouse)
from swipe.permissions import IsDeveloper
from swipe.serializers import FlatSerializer


logger = logging.getLogger(__name__)


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['flat']))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['flat']))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['flat']))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['flat']))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['flat']))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['flat']))
class APIFlatViewSet(ModelViewSet):
    '''API for flats'''
    serializer_class = FlatSerializer
    queryset = Flat.objects.all().order_by('id')
    filterset_fields = ['flat']
    filterset_class = FlatFilter

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action != 'create': 
            permission_classes = [IsAuthenticated, IsDeveloper|IsAdminUser]
        return [p() for p in permission_classes]

    def get_queryset(self):
        qs = self.queryset
        if self.action != 'create' and self.request.user.user_developer is not None:
            qs = Flat.objects.filter(
                house__in=House.objects.filter(
                    pk__in=[dh.house.pk for dh in DeveloperHouse.objects.filter(
                        developer=self.request.user.user_developer
                    )]))
        return qs



