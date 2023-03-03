from django.urls import path, include
from rest_framework import routers

from api.views import CastomUserViewset, SubscribeViewSet

app_name = 'users'
router = routers.DefaultRouter()
router.register('users',  CastomUserViewset, basename='users')


urlpatterns = [
   path('', include(router.urls)),
   path('', include('djoser.urls')),
   path('auth/', include('djoser.urls.authtoken')),
   path('users/<int:pk>/subscribe/', SubscribeViewSet.as_view())
]
