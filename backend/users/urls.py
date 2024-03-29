from api.views import CastomUserViewset, SubscribeViewSet
from django.urls import include, path
from rest_framework import routers

app_name = 'users'
router = routers.DefaultRouter()
router.register('users', CastomUserViewset, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:pk>/subscribe/', SubscribeViewSet.as_view())
]
