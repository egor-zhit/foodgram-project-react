import io

from django.db.models import Sum
from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions, status, views
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import (
    TagModel, RecipesModel, 
    IngredientsModel, IngredientRecipeModel, 
    ShoppingCardModel, FavoriteModel
)
from users.models import User, Subscriptions

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import LimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializer import (
    TagSerialiser, IngredientsSerealizer,
    ResipeSerializer,
    SubscriberUserSerializers, SubscriberRecipeSerializers,
    FavoriteSerializer, ShoppingCardSerializers
)


class CastomUserViewset(UserViewSet):
    pagination_class = LimitPagination

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = Subscriptions.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriberRecipeSerializers(
            page, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(views.APIView):
    pagination_class = LimitPagination
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'errors': 'Подписаться на себя невозможно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscriptions.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Подписаться дважды невозможнj'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.create(user=user, author=author)
        queryset = Subscriptions.objects.get(user=request.user, author=author)
        serializer = SubscriberUserSerializers(
            queryset, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if not Subscriptions.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Отписка не возможна'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user.is_authenticated:
            return Response(
                {'errors': 'Пожалуйста войдите в личный кабинет'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if Subscriptions.objects.filter(user=user, author=author).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Обьект не найден'},
            status=status.HTTP_404_NOT_FOUND
        )


class TagViewset(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """ Получение Тегов """
    queryset = TagModel.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (permissions.AllowAny,)


class IngredientsViewset(TagViewset):
    """Получение ингредиентов."""
    queryset = IngredientsModel.objects.all()
    serializer_class = IngredientsSerealizer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('name',)


class RecipesViewset(viewsets.ModelViewSet):
    """Получение, обновление, удаление и создания рецептов."""
    permission_classes = (IsAdminOrReadOnly, IsAuthorOrReadOnly,)
    serializer_class = ResipeSerializer
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        favorited = FavoriteModel.objects.filter(
            user=user,
            recipes=OuterRef('id'),
        )
        shopping_cart = ShoppingCardModel.objects.filter(
            user=user, 
            recipes=OuterRef('id'),
        )
        if user.is_anonymous:
            return False
        queryset = RecipesModel.objects.annotate(
            is_favorited=Exists(favorited),
            is_in_shopping_cart=Exists(shopping_cart)
        )
        return queryset

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'errors': 'Пожалуйста войдите в личный кабинет'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if request.method == 'POST':
            return self.add_obj(
                model=FavoriteModel, pk=pk,
                serializers=FavoriteSerializer,
                user=user
            )
        if request.method == 'DELETE':
            return self.del_obj(
                model=FavoriteModel, pk=pk, user=user
            )
        return None

    @action(
        detail='True', methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'errors': 'Пожалуйста войдите в личный кабинет'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if request.method == 'POST':
            return self.add_obj(
                model=ShoppingCardModel, pk=pk,
                serializer=ShoppingCardSerializers,
                user=user
            )
        if request.method == 'DELETE':
            return Response(
                model=ShoppingCardModel, pk=pk, user=user
            )
        return None
    
    @action(
        detail=False, permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        dow_resipe = RecipesModel.objects.filter(shopping_cart__user=user)
        if not dow_resipe:
            return Response(
                {'errors': 'Список рецептов пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = IngredientRecipeModel.objects.filter(
            recipe__shopping_carts__user=user).values(
                'ingredient__name',
                'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(amount=Sum('amount')
        )
        buffer = io.BytesIO()
        canvas = Canvas(buffer)
        pdfmetrics.registerFont(
            TTFont('Country', 'Country.ttf', 'UTF-8'))
        canvas.setFont('Country', size=36)
        canvas.drawString(70, 800, 'Продуктовый помощник')
        canvas.drawString(70, 760, 'список покупок:')
        canvas.setFont('Country', size=18)
        canvas.drawString(70, 700, 'Ингредиенты:')
        canvas.setFont('Country', size=16)
        canvas.drawString(70, 670, 'Название:')
        canvas.drawString(220, 670, 'Количество:')
        canvas.drawString(350, 670, 'Единица измерения:')
        height = 630
        for ingredient in ingredients:
            canvas.drawString(70, height, f"{ingredient['ingredient__name']}")
            canvas.drawString(250, height,
                              f"{ingredient['amount']}")
            canvas.drawString(380, height,
                              f"{ingredient['ingredient__measurement_unit']}")
            height -= 25
        canvas.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename='Shoppinglist.pdf')