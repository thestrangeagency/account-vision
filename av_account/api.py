from rest_framework import viewsets, permissions

from av_account.models import AvUser, Address
from av_account.serializers import UserSerializer, AddressSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = AvUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = AvUser
    http_method_names = ['get', 'patch', 'head']

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    model = Address
    http_method_names = ['get', 'patch', 'post', 'head']

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
