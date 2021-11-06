from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from users.serializers import ClientSerializer, DeveloperSerializer, NotarySerializer
from users.models import User, Developer, Notary, Client

class APIClientUpdate(generics.UpdateAPIView):
    serializer_class = ClientSerializer
    queryset = User.objects.all()


class APIDeveloperViewSet(viewsets.ModelViewSet):
    '''API for developers'''
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer


class APINotaryViewSet(viewsets.ModelViewSet):
    '''API for notaries'''
    queryset = Notary.objects.all()
    serializer_class = NotarySerializer


class APIClientViewSet(viewsets.ModelViewSet):
    '''API for clients'''
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = IsAuthenticated, 

    def get_permissions(self):
        permission_classes = IsAuthenticated,
        if self.action == 'list' or 'destroy':
            permission_classes += (IsAdminUser,)
        return [p() for p in permission_classes]


# class APIAgentViewSet()