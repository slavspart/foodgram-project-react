from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import Subscription, User
from .pagination import LimitPagination
from .serializers import (SubscriptionSerializer, UserRegistrSerializer,
                          UserSerializer)


class CustomUserViewsSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrSerializer
        return super().get_serializer_class()


class SubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SubscriptionSerializer
    pagination_class = LimitPagination

    def get_queryset(self):
        queryset = Subscription.objects.all()
        if self.action == 'list':
            queryset = Subscription.objects.filter(follower=self.request.user)
        return queryset

    def perform_create(self, serializer):
        author = self.kwargs.get('id')
        follower = self.request.user
        serializer.save(author=author, follower=follower)

    def destroy(self, request, *args, **kwargs):
        instance = request.user.follower.filter(author=kwargs.get('id'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
