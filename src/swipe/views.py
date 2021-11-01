import logging
from django.utils.decorators import method_decorator

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from swipe.filters import AnnouncementFilter
from swipe.models import Flat, House, Announcement, DeveloperHouse, ClientAnnouncementFavourites, HouseNews
from swipe.permissions import IsDeveloper
from swipe.serializers import AnnoncementFavouritesSerializer, HouseSerializer, HouseNewsSerializer, AnnouncementSerializer, FlatSerializer


logger = logging.getLogger(__name__)


class APIHouseViewSet(ModelViewSet):
    '''API for houses'''
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = IsAuthenticated, IsDeveloper | IsAdminUser


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


class APIAnnouncementViewSet(ModelViewSet):
    '''API for announcement'''
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = IsAuthenticated,
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flat__house__status', 'flat']
    filterset_class = AnnouncementFilter


class APIFlatViewSet(ModelViewSet):
    '''API for flats'''
    serializer_class = FlatSerializer
    queryset = Flat.objects.all()

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
    # http_method_names = ['get', 'put', 'patch', 'delete', 'head', ]
    # permission_classes = IsAuthenticated, 


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="API for getting list of client announcement favourites",
    tags=['announcement favourites']
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="API for add announcement to client favourites",
    tags=['announcement favourites']
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_description="API for delete announcement from client favourites",
    tags=['announcement favourites']
))
class APIAnnouncementFavouritesViewSet(ModelViewSet):
    '''API for announcement favourites'''
    queryset = ClientAnnouncementFavourites.objects.all()
    serializer_class = AnnoncementFavouritesSerializer
    permission_classes = IsAuthenticated,
    http_method_names = ['get', 'post', 'delete' ]

    def get_queryset(self):
        return ClientAnnouncementFavourites.objects.filter(
            client=self.request.user.user_client)