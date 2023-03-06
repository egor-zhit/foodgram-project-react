from django.contrib import admin

from .models import (FavoriteModel, IngredientRecipeModel, IngredientsModel,
                     RecipesModel, ShoppingCardModel, TagModel)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class IngredientRecipeAdmin(admin.StackedInline):
    model = IngredientRecipeModel
    extra = 3


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text', 'cooking_time', 'favorites')
    list_filter = ('author', 'name', 'tags')
    inlines = [IngredientRecipeAdmin]

    def favorites(self, obj):
        return obj.favorites.count()


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes')
    search_fields = ('user', 'recipes',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipes', 'user')
    list_filter = ('user',)


admin.site.register(TagModel, TagAdmin)
admin.site.register(IngredientsModel, IngredientAdmin)
admin.site.register(RecipesModel, RecipeAdmin)
admin.site.register(ShoppingCardModel, ShoppingCartAdmin)
admin.site.register(FavoriteModel, FavoriteAdmin)
