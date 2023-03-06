from api.views import IngredientsViewset, RecipesViewset, TagViewset
from django.urls import include, path
from rest_framework import routers

app_name = 'recipes'
router = routers.DefaultRouter()
router.register('tags', TagViewset, basename='tag')
router.register('ingredients', IngredientsViewset)
router.register('recipes', RecipesViewset, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
