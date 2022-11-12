from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import Subscription, User
from .pagination import LimitPagination
from .serializers import (SubscriptionSerializer, UserRegistrSerializer,
                          UserSerializer)


class CustomUserViewsSet(UserViewSet):
    """Вьюсет для юзеров"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagination

    def retrieve(self, request, *args, **kwargs):
        # переписываем метод, чтобы отображать True,
        # если есть подписка на этого автора
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if request.user.follower.filter(author=kwargs.get('id')).exists():
            # запросили queryset через related_name
            data = serializer.data
            data['is_surbscribed'] = True
            serializer = UserSerializer(instance=instance, data=data)
            serializer.is_valid()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = UserRegistrSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
            )


class SubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет подписок"""
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
