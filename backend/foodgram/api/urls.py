from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet, get_shop)

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', get_shop),
    path('recipes/<id>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'})
    ),
    path('recipes/<id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    path('', include(router.urls)),
]
