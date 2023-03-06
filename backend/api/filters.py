from django.contrib.auth import get_user_model
from django_filters import filters
from django_filters.rest_framework import FilterSet
from recipes.models import RecipesModel, TagModel
from rest_framework.filters import SearchFilter

User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтер для рецептов."""

    is_favorited = filters.BooleanFilter(field_name='is_favorited')
    author = filters.ModelChoiceField(queryset=User.objects.all())
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug", queryset=TagModel.objects.all(),
        to_field_name="slug"
    )

    class Meta:
        model = RecipesModel
        fields = ["tags", "author", "is_favorited", "is_in_shopping_cart"]


class IngredientSearchFilter(SearchFilter):
    """Фильтр для ингредиента."""

    search_param = "name"
