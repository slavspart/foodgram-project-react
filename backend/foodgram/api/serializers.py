from rest_framework import serializers


from .fields import Base64ImageField
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)
from users.serializers import UserSerializer

class TagSerializer (serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer (serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer (serializers.ModelSerializer):
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeSerializer (serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(read_only=False,)
    ingredients = RecipeIngredientSerializer(
        read_only=False, many=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
            )

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.favorite.filter(
                user=self.context.get('request').user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.selected.filter(
                user=self.context.get('request').user).exists()
        return False


class RecipeIngredientCreateSerializer (serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        required=False
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(source='ingredient.name', required=False)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='tag', queryset=Tag.objects.all())
    name = serializers.CharField(source='tag.name', required=False)
    color = serializers.CharField(source='tag.color', required=False)
    slug = serializers.CharField(source='tag.slug', required=False)

    class Meta:
        model = RecipeTag
        fields = ('id', 'name', 'color', 'slug')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(
        many=True, source='recipe_ingredients')
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
        )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'cooking_time',
                  'tags', 'image', 'name', 'text')

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления дожно превышать 0')
        return value

    def validate_ingredients(self, value):
        list_of_ids = []
        for ingredient in value:
            if ingredient.get('ingredient') not in list_of_ids:
                list_of_ids.append(ingredient.get('ingredient'))
            else:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальны')
        return value

    def create_recipe_ingredients(self, instance, ingredients):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
                ) for ingredient, amount in ingredients.items()])

    def create_recipe_tags(self, instance, tags):
        RecipeTag.objects.bulk_create(
            [RecipeTag(recipe=instance, tag=tag) for tag in tags])

    def create(self, validated_data):
        validated_data['author_id'] = self.context.get('request').user.id
        ingredients = {
            ingredient.get(
                'ingredient'): ingredient.get(
                    'amount') for ingredient in validated_data.pop(
                        'recipe_ingredients')}
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        self.create_recipe_ingredients(instance, ingredients)
        self.create_recipe_tags(instance, tags)
        return instance

    def update(self, instance, validated_data):
        instance.recipe_ingredients.all().delete()
        request_ingredients = {
            ingredient.get('ingredient'): ingredient.get('amount')
            for ingredient in validated_data.pop('recipe_ingredients')}
        self.create_recipe_ingredients(instance, request_ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields['tags'] = RecipeTagSerializer(
            many=True, source='recipe_tags')
        return super().to_representation(instance)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного"""
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='recipe')
    name = serializers.CharField(required=False, source='recipe.name')
    image = Base64ImageField(required=False, source='recipe.image')
    cooking_time = serializers.IntegerField(
        required=False, source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор покупок"""
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='recipe')
    name = serializers.CharField(required=False, source='recipe.name')
    image = Base64ImageField(required=False, source='recipe.image')
    cooking_time = serializers.IntegerField(
        required=False, source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time',)
