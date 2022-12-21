from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class CreateDestroyViewset(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    def perform_create(self, serializer):
        recipe = self.kwargs.get('id')
        user = self.request.user
        serializer.save(recipe_id=recipe, user=user)

    def destroy(self, request, *args, **kwargs):
        instance = request.user.favorite.filter(recipe=kwargs.get('id'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
