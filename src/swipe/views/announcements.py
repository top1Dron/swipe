from django.utils.decorators import method_decorator
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from swipe.filters import AnnouncementFilter
from swipe.models import Announcement, ClientAnnouncementFavourites, Promotion
from swipe.serializers import AnnoncementFavouritesCreateSerializer, AnnouncementAdminSerializer, AnnouncementImagesSerializer, AnnouncementListSerializer, AnnouncementRetrieveSerializer, AnnouncementToTheTopSerializer, PromotionSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['announcement']))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['announcement']))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['announcement']))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['announcement']))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['announcement']))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['announcement']))
class APIAnnouncementViewSet(ModelViewSet):
    '''API for announcement'''
    queryset = Announcement.objects.all().order_by('-publication_date')
    permission_classes = IsAuthenticated,
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flat__house__status', 'flat']
    filterset_class = AnnouncementFilter

    def get_queryset(self):
        qs = self.queryset
        if (self.action in ('update', 'partial_update', 'destroy')
            and not self.request.user.is_superuser
            and not self.request.user.is_staff):
            qs = Announcement.objects.filter(advertiser=self.request.user.client)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return AnnouncementListSerializer
        elif self.action in ('add_to_client_favourites', 'remove_from_client_favourites'):
            return AnnoncementFavouritesCreateSerializer
        elif self.action == 'to_the_top':
            return AnnouncementToTheTopSerializer
        else:
            if (not self.request.user.is_superuser
                and not self.request.user.is_staff):
                return AnnouncementRetrieveSerializer
            else:
                return AnnouncementAdminSerializer

    @action(methods=['get'], detail=True, url_path='get-photos', url_name='get_photos')
    @swagger_auto_schema(
        operation_description="API for getting announcement photos",
        tags=['announcement'])
    def get_photos(self, request, *args, **kwargs):
        announcement = get_object_or_404(Announcement, pk=kwargs.get('pk'))
        serializer = AnnouncementImagesSerializer(announcement.images.all(), many=True)
        return Response(data=serializer.data)
    
    @action(methods=['get'], detail=False, url_path='get-client-favourites', url_name='get_client_favourites')
    @swagger_auto_schema(
        operation_description="API for getting announcement list of client favourites",
        tags=['announcement'])
    def get_client_favourites(self, request):
        client_announcement_favourites = Announcement.objects.filter(
            pk__in=[cf.announcement.pk for cf in ClientAnnouncementFavourites.objects.filter(
                client=request.user.client
            )]
        )
        serializer = self.get_serializer_class()(client_announcement_favourites, many=True)
        return Response(data=serializer.data)

    @action(methods=['post'], detail=True, url_path='add-to-client-favourites', url_name='add_to_client_favourites')
    @swagger_auto_schema(
        operation_description="API for add announcement to client favourites",
        tags=['announcement'])
    def add_to_client_favourites(self, request, *args, **kwargs):
        cf = ClientAnnouncementFavourites.objects.create(
            client=request.user.client, 
            announcement=Announcement.objects.get(pk=kwargs.get('pk')))
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True, url_path='remove-from-client-favourites', url_name='remove_from_client_favourites')
    @swagger_auto_schema(
        operation_description="API for delete announcement from client favourites",
        tags=['announcement'])
    def remove_from_client_favourites(self, request, *args, **kwargs):
        announcement = Announcement.objects.get(
                pk=kwargs.get('pk'))
        try:
            ClientAnnouncementFavourites.objects.get(
                client=request.user.client, 
                announcement=announcement).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(data={'announcement': 'Это объявление не находится в списке избранных'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['patch'], detail=True, url_path='to-the-top', url_name='to_the_top')
    @swagger_auto_schema(
        operation_description="API for raising an announcement to the top of the list",
        tags=['announcement'])
    def to_the_top(self, request, *args, **kwargs):
        announcement = get_object_or_404(Announcement, pk=kwargs.get('pk'))
        if (announcement.advertiser != request.user.client
            and not self.request.user.is_superuser
            and not self.request.user.is_staff):
            return Response({'non_field_errors': 'Только создатель объявления может выполнить это действие'}, 
                status=status.HTTP_403_FORBIDDEN)
        serializer = AnnouncementToTheTopSerializer(announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['promotion']))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['promotion']))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['promotion']))
class PromotionAPIView(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """API for announcements' promotions"""
    queryset = Promotion.objects.all()
    permission_classes = IsAuthenticated,
    view_tags = ['promotion']
    serializer_class = PromotionSerializer
    lookup_field = 'announcement_id'