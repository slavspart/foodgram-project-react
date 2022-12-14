from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import CreateDestroyViewset
from .models import (Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from .pagination import LimitPagination
from .permissions import UpdateRestriction
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """"Вьюсет тэгов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # фронтенд устроен так, что он не передает токен при запросе
    # тэгов и ингредиентов


class RecipeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для GET, PATCH, DELETE запросов рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        UpdateRestriction
        )

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class FavoriteViewSet(CreateDestroyViewset,):
    """Вьюсет для объектов Favorite"""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = request.user.favorite.filter(recipe=kwargs.get('id'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
        # переопределяем метод, для переопределения instance


class ShoppingCartViewSet(CreateDestroyViewset,):
    """Вьюсет для объектов ShoppingCart"""
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def destroy(self, request, *args, **kwargs):
        instance = request.user.shopping_cart.filter(recipe=kwargs.get('id'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_shop(request):
    """Вью-функция для получения списка продуктов"""
    ing_dict = {}
    for ingredient in RecipeIngredient.objects.filter(
        recipe__in=Recipe.objects.filter(
            selected__in=request.user.shopping_cart.all())):
        # перебираем ингредиенты из объектов shopping_cart
        if ((f'{ingredient.ingredient.name}'
             f'({ingredient.ingredient.measurement_unit}) -')
                not in ing_dict):
            # если ингредиента нет в словаре, создаем запись
            ing_dict[f'{ingredient.ingredient.name}'
                     f'({ingredient.ingredient.measurement_unit}) -'] = (
                    ingredient.amount)
        else:
            ing_dict[f'{ingredient.ingredient.name}'
                     f'({ingredient.ingredient.measurement_unit}) -'] += (
                        ingredient.amount)
            # если ингредиент есть, то добавляем количество
    cart_text = ''
    for item in ing_dict:
        cart_text += f'{item} {ing_dict[item]}' + '''
'''
    # меняем словарь на строку
    return HttpResponse(cart_text, content_type="text/plain")
    # возвращаем httpresponse, а не drf Response,
    # потому что он не работает с переносом текста
