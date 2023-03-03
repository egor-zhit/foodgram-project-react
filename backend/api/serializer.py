from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
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

class CustomCreateUserSerializers(UserCreateSerializer):
    """Сериализатор для создания пользователей."""
    password = serializers.CharField(
        style={'input_type': 'password'},
        label='Пароль',
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'password',
        )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializers(UserSerializer):
    """Сериализатор для получения пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, author_id):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            user=user, author=author_id.id
            ).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

class SubscriberRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = RecipesModel
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriberUserSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = RecipesModel.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return SubscriberRecipeSerializers(queryset, many=True).data

    def get_recipes_count(self, obj):
        return RecipesModel.objects.filter(author=obj.author).count()

    class Meta:
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

    class Meta:
        model = IngredientsModel
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientResipeSerializer(serializers.ModelSerializer):
    """Сериализер для получения количества ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipeModel
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ResipeSerializer(serializers.ModelSerializer):
    """Сериализер для рецептов."""
    tags = TagSerialiser(read_only=True, many=True)
    author = CustomUserSerializers(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientResipeSerializer(read_only=True, many=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True, default=False)

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(IngredientsModel, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({
                    'tags': 'Теги должны быть уникальными!'
                })
            tags_list.append(tag)
        return 

    @staticmethod
    def ingredient_recipe_create(ingredients_set, recipe):
        ingredients_list = []
        for ingredient_get in ingredients_set:
            ingredient=IngredientsModel.objects.get(id=ingredient_get.get('id'))
            amount = ingredient_get['amount']
            ingredients_list.append(
                IngredientRecipeModel(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            )
        IngredientRecipeModel.objects.bulk_create(ingredients_list)

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
        tags = self.initial_data.get('tags')
        ingredients_set = self.initial_data.get('ingredients')
        instance.tags.clear()
        IngredientRecipeModel.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)
        self.ingredient_recipe_create(ingredients_set, instance)
        return super().update(instance, validated_data)

    class Meta:
        model = RecipesModel
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализер для избраного."""
    id = serializers.ReadOnlyField(source='recipes.id')
    name = serializers.ReadOnlyField(source='recipes.name')
    image = serializers.ImageField(source='recipes.image')
    cooking_time = serializers.ReadOnlyField(source='recipes.cooking_time')

    class Meta:
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