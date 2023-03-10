from django.contrib.auth import get_user_model
from django_filters import filters
from django_filters.rest_framework import FilterSet
from recipes.models import RecipesModel, TagModel
from rest_framework.filters import SearchFilter

User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтер для рецептов."""

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    author = filters.ModelChoiceField(queryset=User.objects.all())
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug", queryset=TagModel.objects.all(),
        to_field_name="slug"
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == 1:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset

    class Meta:
        model = RecipesModel
        fields = ["tags", "author"]


class IngredientSearchFilter(SearchFilter):
    """Фильтр для ингредиента."""

    search_param = "name"
