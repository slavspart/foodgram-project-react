from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')
    tags = filters.CharFilter(method='tag_filter')

    class Meta:
        fields = ['is_favorited', 'is_in_shopping_cart', 'author']
        model = Recipe

    def is_favorited_filter(self, queryset, name, value):
        if value == 1:
            return queryset.filter(favorite__user=self.request.user)
        elif value == 0:
            return queryset.exclude(favorite__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value == 1:
            return queryset.filter(selected__user=self.request.user)
        elif value == 0:
            return queryset.exclude(selected__user=self.request.user)
        return queryset

    def tag_filter(self, queryset, name, value):
        queryset = queryset.order_by('-id')
        tags = []
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct().order_by('-id')
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name', ]
