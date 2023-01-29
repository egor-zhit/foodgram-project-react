from django.urls import path, include
from rest_framework import routers
from api.views import TagViewset

from api.views import ()

app_name = 'recipes'
router = routers.DefaultRouter()
router.register('recipes', )
router.register('tags', TagViewset, basename='tag')
router.register('ingredients', )

urlpatterns = [
    path('', include(router.urls)),
]
