from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    pass


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited')
    list_filter = ('name', 'tags')
    readonly_fields = ('favorited',)

    def favorited(self, instance):
        return instance.favorite.all().count()


@admin.register(Ingredient)
class IndgredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class RecipeTagAdmin(RecipeTag):
    pass


class RecipeIngredientAdmin(RecipeIngredient):
    pass


class FavoriteAdmin(Favorite):
    pass


class ShoppingCartAdmin(ShoppingCart):
    pass


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
