from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import api_view

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
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class FavoriteViewSet(CreateDestroyViewset,):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingCartViewSet(CreateDestroyViewset,):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


@api_view(['GET'])
def get_shop(request):
    ings = {}
    for ingredient in Ingredient.objects.filter(
        ingrec__in=RecipeIngredient.objects.filter(
            recipe__in=Recipe.objects.filter(
                selected__in=request.user.shopping_cart.all()))).annotate(
                    amount=Sum('ingrec__amount')):
        ings[ingredient] = f'{ingredient.amount} {ingredient.measurement_unit}'
    cart_text = ''
    for item in ings:
        cart_text += f'''{item} - {ings[item]}
'''
#
    return HttpResponse(cart_text, content_type="text/plain")
