from rest_framework import serializers
from recipes.models import (
    TagModel, IngredientsModel,
    IngredientRecipeModel, RecipesModel,
    FavoriteModel, ShoppingCardModel
)
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from users.models import User, Subscriptions
from drf_extra_fields.fields import Base64ImageField


class CustomCreateUserSerializers(serializers.ModelSerializer):
    """Сериализатор для создания пользователей."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta():
        model = User
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super(CustomCreateUserSerializers, self).create(validated_data)


class CustomUserSerializers(serializers.ModelSerializer):
    """Сериализатор для получения пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, author_id):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=user, author=author_id.id
            ).exists()

    class Meta():
        model = User
        fields = '__all__'


class SubscriberRecipeSerializers(serializers.ModelSerializer):
    class Meta():
        model = RecipesModel
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriberUserSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=user, author=obj.author
            ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = RecipesModel.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return SubscriberRecipeSerializers(queryset, many=True).data

    def get_recipes_count(self, obj):
        return RecipesModel.objects.filter(author=obj.author).count()

    class Meta():
        model = Subscriptions
        fields = '__all__'


class TagSerialiser(serializers.ModelSerializer):
    """Сериалайзер для Тега."""
    class Meta:
        model = TagModel
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientsSerealizer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов."""

    class Meta():
        model = IngredientsModel
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientResipeSerializer(serializers.ModelSerializer):
    """Сериализер для получения количества ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta():
        model = IngredientRecipeModel
        fields = '__all__'


class ResipeSerializer(serializers.ModelSerializer):
    """Сериализер для рецептов."""
    tags = TagSerialiser(read_only=True, many=True)
    author = CustomUserSerializers(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientResipeSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCardModel.objects.filter(
            user=user, recipe=obj.id
            ).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = {}
        if ingredients:
            for ingredient in ingredients:
                if ingredient.get('id') in ingredients_list:
                    raise ValidationError(
                        'Ингредиент может быть добавлен только один раз')
                if int(ingredient.get('amount')) <= 0:
                    raise ValidationError(
                        'Добавьте количество для ингредиента больше 0'
                    )
                ingredients_list[ingredient.get('id')] = (
                    ingredients_list.get('amount')
                )
            return data
        else:
            raise ValidationError('Добавьте ингредиент в рецепт')

    def ingredient_recipe_create(self, ingredients_set, recipe):
        for ingredient_get in ingredients_set:
            ingredient = IngredientsModel.objects.get(
                id=ingredient_get.get('id')
            )
            IngredientRecipeModel.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=ingredient_get.get('amount')
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        recipe = RecipesModel.objects.create(
            image=image,
            author=self.context['request'].user,
            **validated_data
        )
        tags = self.initial_data.get('tags')
        recipe.tags.set(tags)
        ingredients_set = self.initial_data.get('ingredients')
        self.ingredient_recipe_create(ingredients_set, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        instance.save()
        IngredientRecipeModel.objects.filter(recipe=instance).delete()
        ingredients_set = self.initial_data.get('ingredients')
        self.ingredient_recipe_create(ingredients_set, instance)
        return instance

    class Meta():
        model = RecipesModel
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализер для избраного."""
    id = serializers.ReadOnlyField(source='recipes.id')
    name = serializers.ReadOnlyField(source='recipes.name')
    image = serializers.ImageField(source='recipes.image')
    cooking_time = serializers.ReadOnlyField(source='recipes.cooking_time')

    class Meta():
        model = FavoriteModel
        fields = '__all__'


class ShoppingCardSerializers(serializers.ModelSerializer):
    """Сериализер для корзины."""
    id = serializers.ReadOnlyField(source='recipes.id')
    name = serializers.ReadOnlyField(source='recipes.name')
    image = serializers.ImageField(source='recipes.image')
    cooking_time = serializers.ReadOnlyField(source='recipes.cooking_time')

    class Meta:
        model = ShoppingCardModel
        fields = '__all__'