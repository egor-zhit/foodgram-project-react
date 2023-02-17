from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class IngredientsModel(models.Model):
    """Модель Ингредиенты."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True
        )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta():
        ordering = ['-name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}({self.measurement_unit})'


class TagModel(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    color = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='Цветовой HEX-код'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Идентификатор'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class RecipesModel(models.Model):
    """Модель рецепты."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
        )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        TagModel,
        related_name='recipes',
        verbose_name='рецепт',
        )
    image = models.ImageField(
        'картинка',
        upload_to='recipes/'
    )
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            limit_value=1,
            message='Введеное вами число больше единицы'
            )
            ]
        )

    class Meta():
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipeModel(models.Model):
    """Модель для связки рецепта и ингредиента."""
    ingredient = models.ForeignKey(IngredientsModel,
                                   on_delete=models.CASCADE,
                                   related_name='recipes',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(RecipesModel,
                               on_delete=models.CASCADE,
                               related_name='ingredients',
                               verbose_name='Рецепт'
                               )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta():
        ordering = ['-id']
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'

    def __str__(self):
        return f"Ингредиент: {self.ingredient}, Рецепт: {self.recipe}"


class ShoppingCardModel(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь',
        )
    recipes = models.ForeignKey(
        RecipesModel,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='рецепт',
    )

    class Meta():
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        models.UniqueConstraint(
            fields=['user', 'recipes'],
            name='unique_shopping_user_recipes'
        )

    def __str__(self):
        return f'список покупок пользователя {self.user}'


class FavoriteModel(models.Model):
    """Модель избраное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        RecipesModel,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='рецепт',
    )

    class Meta():
        ordering = ['-id']
        verbose_name = 'Избраное'
        verbose_name_plural = 'Избраное'
        models.UniqueConstraint(
            fields=['user', 'recipes'],
            name='unique_favorites_user_recipes'
        )

    def __str__(self):
        return f'избранное пользователя {self.user}'
