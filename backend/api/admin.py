from django.contrib import admin

from recipes.models import TagModel, IngredientsModel, RecipesModel, IngredientRecipeModel
from users.models import User

admin.site.register(TagModel)
admin.site.register(IngredientsModel)
admin.site.register(RecipesModel)
admin.site.register(IngredientRecipeModel)
admin.site.register(User)