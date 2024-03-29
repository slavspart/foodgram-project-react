from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='имя')
    color = models.CharField(max_length=7, verbose_name='цвет')
    slug = models.SlugField(unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name='имя')
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='единица измерения',
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='тэги'
        )
    author = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='автор'
        )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='ингредиенты')
    name = models.CharField(max_length=200, verbose_name='имя')
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='фото',
        )
    text = models.TextField(verbose_name='текст',)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='рецепт',
        )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='тэг',
        related_name='tags_rec'
        )

    class Meta:
        verbose_name = 'Тэг для рецепта'
        verbose_name_plural = 'Тэги для рецептов'
        constraints = [models.UniqueConstraint(
            fields=['tag', 'recipe'],
            name='unique_tag_in_recipe',
            )]

    def __str__(self):
        return f'{self.recipe} in {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingrec',
        verbose_name='ингредиент',
        )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_ingredient_in_recipe'
            )]

    def __str__(self):
        return f'''{self.ingredient_id} {self.amount}
        in {self.recipe} - {self.recipe_id}'''


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='пользователь',
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='рецепт'
        )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite'
            )]

    def __str__(self):
        return f'{self.user} favorited {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='пользователь',
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='selected',
        verbose_name='рецепт',
        )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart')]

    def __str__(self):
        return f'{self.user} added {self.recipe} id {self.id} to cart'
