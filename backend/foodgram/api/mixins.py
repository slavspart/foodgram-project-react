from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class CreateDestroyViewset(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        recipe = self.kwargs.get('id')
        user = self.request.user
        serializer.save(recipe_id=recipe, user=user)
        # переопределяем метод, чтобы передать в модель
        # юзера и рецепт
