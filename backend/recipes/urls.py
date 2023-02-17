from django.urls import path, include
from rest_framework import routers
from api.views import TagViewset, IngredientsViewset, RecipesViewset


app_name = 'recipes'
router = routers.DefaultRouter()
router.register('tags', TagViewset, basename='tag')
router.register('ingredients', IngredientsViewset,)
router.register('recipes', RecipesViewset,)

urlpatterns = [
    path('', include(router.urls)),
]
