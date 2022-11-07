from .models import Favorite, Ingredient, Recipe, RecipeTag, ShoppingCart, Tag, RecipeIngredient
from users.serializers import UserSerializer

import base64 
# Модуль с функциями кодирования и декодирования base64
from django.core.files.base import ContentFile
# Модуль для создания файла из base64
from rest_framework import serializers



class TagSerializer (serializers.ModelSerializer):
    """Сериализатор тегов"""
    class Meta:
        model=Tag
        fields = '__all__'


class IngredientSerializer (serializers.ModelSerializer):
    """Сериализатор ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer (serializers.ModelSerializer):
    """Сериализатор для получения ингредиентов для рецепта"""
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    id = serializers.PrimaryKeyRelatedField(source='ingredient', queryset = Ingredient.objects.all())
    # здесь имеется в виду id ингредиента
    name = serializers.CharField(source = 'ingredient.name')
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')

   

class Base64ImageField(serializers.ImageField):
    """Поле для управления картинками"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            # декодируем
            ext = format.split('/')[-1]  
            # делим строку на части
            # и извлечкаем расширение файла.
            data = ContentFile(base64.b64decode(imgstr), name='recipe.' + ext)
            # Сохраняем в файл
        return super().to_internal_value(data)
    def to_representation(self, value):
        return value.url


class RecipeSerializer (serializers.ModelSerializer):
    """Сериализатор для получения рецептов"""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author=UserSerializer(read_only=False,)
    ingredients = RecipeIngredientSerializer(
        read_only=False, many=True, 
        source='recipe_ingredients'
        )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
    
    def get_is_favorited(self,obj):
        if self.context.get('request').user.is_authenticated:
            return obj.favorite.filter(user=self.context.get('request').user).exists()
        # значение равно существуют ли объекты связанной модели с request.user
        return False
        
    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated:
            return obj.selected.filter(user=self.context.get('request').user).exists()
        return False


class RecipeIngredientCreateSerializer (serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', 
        queryset = Ingredient.objects.all()
        )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        required=False
        )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', 
        queryset = Ingredient.objects.all()
        )
    # здесь имеется в виду id ингредиента
    name = serializers.CharField(source = 'ingredient.name', required=False)
    # required=False, чтобы можно было передавать не все поля при создании объекта
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')
    
    
class RecipeTagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов в рецепте"""
    id = serializers.PrimaryKeyRelatedField(source='tag', queryset=Tag.objects.all())
    name = serializers.CharField(source='tag.name', required=False)
    color = serializers.CharField(source='tag.color', required=False)
    slug = serializers.CharField(source='tag.slug', required=False)
    class Meta:
        model=RecipeTag
        fields = ('id', 'name', 'color', 'slug')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    ingredients = RecipeIngredientCreateSerializer(many=True,source='recipe_ingredients')
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    class Meta:
        model = Recipe
        fields = ('ingredients', 'cooking_time', 'tags', 'image', 'name', 'text')

    def validate_cooking_time(self,value):
        if value < 1:
            raise serializers.ValidationError('Cooking time must be more than 0')
        return value
        
    def create(self, validated_data):
        validated_data['author_id']= self.context.get('request').user.id
        ingredients = validated_data.pop('recipe_ingredients')
        tags=self.initial_data.get('tags')
        # удаляем из validated_data ингредиенты, т.к. нельзя прямо оттуда
        # передать значение в рецепт
        instance=Recipe.objects.create(**validated_data)
        # создаем рецепт без ингредиентов
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient.get('ingredient'), 
                recipe=instance, amount=ingredient.get('amount'))
        for tag in tags:
            RecipeTag.objects.create(
                tag_id=tag,
                recipe=instance,
            )
        # в цикле создаем промежуточный объект с созданным рецептом
        # и нужными ингредиентами
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        initial_ingredient_ids = list(
            instance.recipe_ingredients.all().values_list('ingredient_id', flat=True))
        # cоздаем список ингредиентов которые уже есть в рецепте
        # flat=True отвечает за то, что передаются только id ингредиентов
        request_ingredient_ids = [dict['id'] for dict in
        self.initial_data['ingredients'] if 'id' in dict]
        # создаем список переданных в запросе ингредиентов
        for ingredient in initial_ingredient_ids:
            if ingredient not in request_ingredient_ids:
                RecipeIngredient.objects.filter(ingredient_id=ingredient, recipe=instance).delete()
        # проверяем, если среди имеющихся нет тех, которые были запрошены
        # удаляем лишние
        ingredients = validated_data.pop('recipe_ingredients')
        for ingredient in ingredients:
            if RecipeIngredient.objects.filter(
                ingredient=ingredient.get('ingredient'),recipe = instance).exists():
                RecipeIngredient.objects.filter(
                    ingredient=ingredient.get('ingredient')).update(amount=ingredient.get('amount'))
            # проверяем если такой ингредиент существует, то обновляем количество
            else:    
                RecipeIngredient.objects.create(
                ingredient=ingredient.get('ingredient'),
                recipe=instance,
                amount=ingredient.get('amount')
                )
            # если ингредиент отсутствует создаем новый объект промежуточной модели

        if 'tags' in self.initial_data:
            initial_tags = list(instance.recipe_tags.all().values_list('tag',flat=True))
            request_tags=self.initial_data.get('tags')
            for tag in initial_tags:
                if tag not in request_tags:
                    RecipeTag.objects.filter(recipe=instance, tag=tag).delete()
            for tag in request_tags:
                    RecipeTag.objects.get_or_create(recipe=instance, tag_id=tag)
        instance.save()
        return instance

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного"""
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='recipe')
    # read_only = True, т.к. данные id берется не из payload 
    # (иначе будет требовать заполнения полей в момент валидации для unique_together)
    name = serializers.CharField(required=False, source='recipe.name')
    image = Base64ImageField(required=False, source='recipe.image')
    cooking_time = serializers.IntegerField(required=False, source='recipe.cooking_time')
    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time',)
    

class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор покупок"""
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='recipe')
    name = serializers.CharField(required=False, source='recipe.name')
    image = Base64ImageField(required=False, source='recipe.image')
    cooking_time = serializers.IntegerField(required=False, source='recipe.cooking_time')
    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time',)
    

