from django.utils.decorators import method_decorator
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from swipe.models import HouseImage, House, HouseNews, DeveloperHouse, Announcement
from swipe.permissions import IsDeveloper
from swipe.serializers import HouseImagesSerializer, HouseListSerializer, HouseNewsSerializer, HouseSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['house']))
class APIHouseViewSet(ModelViewSet):
    '''API for houses'''
    queryset = House.objects.all()
    permission_classes = IsAuthenticated, IsDeveloper | IsAdminUser

    def get_queryset(self):
        qs = self.queryset
        if (self.request.user.user_developer is not None 
            and self.request.user.is_superuser == False
            and self.request.user.is_staff == False):
            qs = House.objects.filter(pk__in=[
                dv.house.pk for dv in DeveloperHouse.objects.filter(
                    developer=self.request.user.user_developer)
            ])
        elif (self.request.user.user_developer is None
            and self.request.user.is_superuser == False
            and self.request.user.is_staff == False):
            qs = House.objects.filter(pk__in={
                an.flat.house.pk for an in Announcement.objects.all() if an.flat is not None
            })
        return qs

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsDeveloper|IsAdminUser]
        if self.action == 'list': 
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list': 
            return HouseListSerializer
        return HouseSerializer
    
    @action(methods=['get'], detail=True, url_path='get-photos', url_name='get_photos')
    @swagger_auto_schema(
        operation_description="API for getting house photos",
        tags=['house'])
    def get_photos(self, request, *args, **kwargs):
        house = get_object_or_404(House, pk=kwargs.get('pk'))
        serializer = HouseImagesSerializer(house.images.all(), many=True)
        return Response(data=serializer.data)


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['house_news']))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['house_news']))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['house_news']))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['house_news']))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['house_news']))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['house_news']))
class APIHouseNewsViewSet(ModelViewSet):
    '''API for houses'''
    queryset = HouseNews.objects.all()
    serializer_class = HouseNewsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['house']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsDeveloper|IsAdminUser]
        if self.action == 'list' and 'house' in self.request.GET: 
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]