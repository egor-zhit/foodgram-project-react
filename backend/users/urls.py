from django.urls import path, include
from rest_framework import routers

from api.views import ()

app_name = 'users'
router = routers.DefaultRouter()
router.register('users', )

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
