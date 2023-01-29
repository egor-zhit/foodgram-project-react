from django.shortcuts import render
from rest_framework import viewsets
from .serializer import TagSerialiser
from rest_framework.permissions import AllowAny


class CastomUserViewset(viewsets.ModelViewSet):
    pass


class TagViewset(viewsets.ModelViewSet):
    """ Получение Тегов """
    serializer_class = TagSerialiser
    permission_classes = (AllowAny,)
