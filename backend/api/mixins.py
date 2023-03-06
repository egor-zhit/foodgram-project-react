from django.utils.translation import gettext as _
from recipes.models import RecipesModel
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


class CustomRecipeModelViewSet(viewsets.ModelViewSet):

    def add_obj(self, serializers, model, user, pk):
        recipe = get_object_or_404(RecipesModel, id=pk)
        if model.objects.filter(user=user, recipes=recipe).exists():
            return Response({'errors':
                            _(f'{recipe} уже добавлен в {model}')},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipes=recipe)
        queryset = model.objects.get(user=user, recipes=recipe)
        serializer = serializers(queryset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_obj(self, model, pk, user):
        recipe = get_object_or_404(RecipesModel, id=pk)
        if not model.objects.filter(user=user, recipes=recipe).exists():
            return Response({'errors': _(f'{recipe} не добавлен в {model}')},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.get(user=user, recipes=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
