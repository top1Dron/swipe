from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from users.serializers import ClientSerializer, DeveloperSerializer, NotarySerializer
from users.models import User, Developer, Notary, Client

class APIClientUpdate(generics.UpdateAPIView):
    serializer_class = ClientSerializer
    queryset = User.objects.all().order_by('id')


class APIDeveloperViewSet(viewsets.ModelViewSet):
    '''API for developers'''
    queryset = Developer.objects.all().order_by('id')
    serializer_class = DeveloperSerializer


class APINotaryViewSet(viewsets.ModelViewSet):
    '''API for notaries'''
    queryset = Notary.objects.all().order_by('id')
    serializer_class = NotarySerializer
    
    def get_permissions(self):
        return [IsAuthenticated()] if self.action == 'list' else [IsAdminUser()]


class APIClientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    '''API for clients'''
    queryset = Client.objects.all().order_by('id')
    serializer_class = ClientSerializer
    permission_classes = IsAuthenticated, 

    def get_permissions(self):
        permission_classes = IsAuthenticated,
        if self.action in ['list', 'blacklist']:
            permission_classes += (IsAdminUser,)
        return [p() for p in permission_classes]

    @action(methods=['patch'], detail=True, url_path='blacklist', url_name='blacklist')
    @swagger_auto_schema(
        operation_description="API for adding user to blacklist or removing him from it",
        tags=['users'])
    def blacklist(self, request, *args, **kwargs):
        client = generics.get_object_or_404(Client, pk=kwargs.get('pk'))
        user = client.user
        user.is_active = False if user.is_active else True
        user.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=False, url_path='update-profile', url_name='update_profile')
    @swagger_auto_schema(
        operation_description="API for update user client profile",
        tags=['users'])
    def update_profile(self, request, *args, **kwargs):
        client = request.user.client
        serializer = ClientSerializer(client, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='me', url_name='me')
    @swagger_auto_schema(
        operation_description="API for get user client profile",
        tags=['users'])
    def me(self, request, *args, **kwargs):
        client = request.user.client
        serializer = ClientSerializer(client, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# class APIAgentViewSet()