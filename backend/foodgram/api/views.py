from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .pagination import LimitPagination
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('-id')
        tags = self.request.query_params.getlist('tags')
        # передаем из query список значений tags, чтобы потом отфильтровать
        # по вхождению в список
        if tags != []:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct().order_by('-id')
            # distinct, чтобы убрать повторения, если больше одно тэга
        return queryset

    def update(self, request, *args, **kwargs):
        if self.action == 'update':
            raise exceptions.MethodNotAllowed(request.method)
            # запрещаем put метод
        return super().update(request, *args, **kwargs)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CreateRecipeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Вьюсет для создания рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для объектов Favorite"""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

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

    def destroy(self, request, *args, **kwargs):
        instance = request.user.favorite.filter(recipe=kwargs.get('id'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """Вьюсет для объектов ShoppingCart"""
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

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

    def destroy(self, request, *args, **kwargs):
        instance = request.user.shopping_cart.filter(recipe=kwargs.get('id'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_shop(request):
    """Вью-функция для получения списка продуктов"""
    dict = {}
    for shopping_cart in request.user.shopping_cart.all():
        # перебираем объекты списка покупок у данного юзера
        for ingredient in shopping_cart.recipe.recipe_ingredients.all():
            # перебираем ингредиенты из объектов shopping_cart
            if ((f'{ingredient.ingredient.name}'
                    f'({ingredient.ingredient.measurement_unit}) -')
                    not in dict):
                # если ингредиента нет в словаре, создаем запись
                dict[f'{ingredient.ingredient.name}'
                     f'({ingredient.ingredient.measurement_unit}) -'] = (
                        ingredient.amount)
            else:
                dict[f'{ingredient.ingredient.name}'
                     f'({ingredient.ingredient.measurement_unit}) -'] += (
                        ingredient.amount)
            # если ингредиент есть, то добавляем количество
    cart_text = ''
    for item in dict:
        cart_text += f'{item} {dict[item]}' + '''
'''
    # меняем словарь на строку
    return HttpResponse(cart_text, content_type="text/plain")
    # возвращаем httpresponse, а не drf Response,
    # потому что он не работает с переносом текста
