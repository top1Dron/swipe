import logging

from django.utils.decorators import method_decorator
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from swipe.filters import FlatFilter

from swipe.models import ClientHouseFavourites, Flat, HouseImage, House, HouseNews, DeveloperHouse, Announcement
from swipe.permissions import IsDeveloper
from swipe.serializers import FlatSerializer, HouseFavouritesCreateSerializer, HouseImagesSerializer, HouseListSerializer, HouseNewsSerializer, HouseSerializer


logger = logging.getLogger(__name__)


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['house']))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['house']))
class APIHouseViewSet(ModelViewSet):
    '''API for houses'''
    queryset = House.objects.all().order_by('id')
    permission_classes = IsAuthenticated, IsDeveloper | IsAdminUser
    filterset_class = None

    def get_queryset(self):
        qs = self.queryset
        if (self.request.user.user_developer is not None 
            and self.request.user.is_superuser == False
            and self.request.user.is_staff == False):
            qs = House.objects.filter(pk__in=[
                dv.house.pk for dv in DeveloperHouse.objects.filter(
                    developer=self.request.user.user_developer)
            ]).order_by('id')
        elif (self.request.user.user_developer is None
            and self.request.user.is_superuser == False
            and self.request.user.is_staff == False):
            qs = House.objects.filter(pk__in={
                an.flat.house.pk for an in Announcement.objects.all() if an.flat is not None
            }).order_by('id')
        return qs

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsDeveloper|IsAdminUser]
        if self.action in ['list', 'retrieve', 'get_client_favourites', 'add_to_client_favourites', 'remove_from_client_favourites']: 
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.action in ['list', 'get_client_favourites']: 
            return HouseListSerializer
        elif self.action in ('add_to_client_favourites'):
            return HouseFavouritesCreateSerializer
        elif self.action == 'add_photo':
            return HouseImagesSerializer
        return HouseSerializer
    
    @action(methods=['get'], detail=True, url_path='get-photos', url_name='get_photos')
    @swagger_auto_schema(
        operation_description="API for getting house photos",
        tags=['house'])
    def get_photos(self, request, *args, **kwargs):
        house = get_object_or_404(House, pk=kwargs.get('pk'))
        serializer = HouseImagesSerializer(house.images.all(), many=True)
        return Response(data=serializer.data)

    @action(methods=['post'], detail=True, url_path='add-photo', url_name='add_photo')
    @swagger_auto_schema(
        operation_description="API for add house photo",
        tags=['house'])
    def add_photo(self, request, *args, **kwargs):
        house = get_object_or_404(HouseImage, pk=kwargs.get('pk'))
        serializer = HouseImagesSerializer(data=request.FILES)
        if serializer.is_valid():
            serializer.save(house=house)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='get-client-favourites', url_name='get_client_favourites')
    @swagger_auto_schema(
        operation_description="API for getting house list of client favourites",
        tags=['house'])
    def get_client_favourites(self, request):
        client_house_favourites = House.objects.filter(
            pk__in=[cf.house.pk for cf in ClientHouseFavourites.objects.filter(
                client=request.user.client
            )]
        )
        serializer = self.get_serializer_class()(client_house_favourites, many=True, context={'request': request})
        return Response(data=serializer.data)

    @action(methods=['post'], detail=True, url_path='add-to-client-favourites', url_name='add_to_client_favourites')
    @swagger_auto_schema(
        operation_description="API for add house to client favourites",
        tags=['house'])
    def add_to_client_favourites(self, request, *args, **kwargs):
        cf = ClientHouseFavourites.objects.create(
            client=request.user.client, 
            house=House.objects.get(pk=kwargs.get('pk')))
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True, url_path='remove-from-client-favourites', url_name='remove_from_client_favourites')
    @swagger_auto_schema(
        operation_description="API for delete house from client favourites",
        tags=['house'])
    def remove_from_client_favourites(self, request, *args, **kwargs):
        house = House.objects.get(
                pk=kwargs.get('pk'))
        try:
            ClientHouseFavourites.objects.get(
                client=request.user.client, 
                house=house).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(data={'announcement': 'Этот ЖК не находится в списке избранных'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['delete'], detail=True, url_path='remove-photo', url_name='remove_photo')
    @swagger_auto_schema(
        operation_description="API for remove house photo. id - a unique integer value identifying this photo.",
        tags=['house'])
    def remove_photo(self, request, *args, **kwargs):
        house_image = get_object_or_404(HouseImage, pk=kwargs.get('pk'))
        house_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 


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