from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тэга"""
    name = models.CharField(max_length=100,)
    color = models.CharField(max_length=7,)
    slug = models.SlugField(unique=True,)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(max_length=200, db_index=True)
    measurement_unit = models.CharField(max_length=50,)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов"""
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    author = models.ForeignKey(
        User, related_name='recipes', on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Промежуточная модель тэгов в рецепте"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    # поменять on_delete

    class Meta:
        unique_together = ['recipe', 'tag']

    def __str__(self):
        return f'{self.recipe} in {self.tag}'


class RecipeIngredient(models.Model):
    """Промежуточная модель ингредиентов в рецепте"""
    recipe = models.ForeignKey(
        Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingrec')
    amount = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['recipe', 'ingredient']
        # нельзя созавать повторные объекты с одними и теми же значениями

    def __str__(self):
        return f'{self.recipe} in {self.ingredient}'


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite')

    class Meta:
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f'{self.user} favorited {self.recipe}'


class ShoppingCart(models.Model):
    """Модель покупок"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='selected')

    class Meta:
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f'{self.user} added {self.recipe} to cart'
