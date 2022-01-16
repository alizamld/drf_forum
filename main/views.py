from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# from main.filters import PostFilter
from main.models import *
from main.permissions import IsAuthor
from main.serializers import *
#
#
# class PermissionMixin:
#
#     def get_permissions(self):
#         if self.action in ['update', 'partial_update', 'delete', 'destroy']:
#             permissions= [IsAuthor, ]
#         elif self.action == 'favorite':
#             permissions = [IsAuthenticated]
#         else:
#             permissions = []
#         return [permission() for permission in permissions]
#
#
# class PostViewSet(PermissionMixin,ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#
#     @action(methods=['GET'], detail=False)
#     def search(self, request):
#         q = request.query_params.get('q')
#         queryset = self.get_queryset().filter(
#             Q(name__icontains=q)|
#             Q(description__icontains=q)|
#             Q(country__icontains=q)
#         )
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['get'])
#     def favorites(self, request):
#         queryset = Favorite.objects.all()
#         queryset = queryset.filter(user=request.user)
#         serializer = FavoriteSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
#     def favorite(self, request, pk=None):
#         hotel = self.get_object()
#         obj, created = Favorite.objects.get_or_create(user=request.user, hotel=hotel, )
#         if not created:
#             obj.favorite = not obj.favorite
#             obj.save()
#         favorites = 'added to favorites' if obj.favorite else 'removed from favorites'
#
#         return Response(f'Successfully {favorites}', status=status.HTTP_200_OK)
#
#     def get_serializer_context(self):
#         return {'request': self.request, 'action': self.action}
#


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'category__name']
    # filterset_class = PostFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return []
        elif self.action == 'comments':
            if self.request.method == 'POST':
                return [IsAuthenticated()]
            return []
        return [IsAuthor()]

    # elif self.action in ['partial_update', 'update', 'destroy', 'delete']:
    #     return [IsAuthor()]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        images = data.pop('images', [])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        for image in images:
            PostImage.objects.create(post=post, image=image)
        return Response(serializer.data, status=201)

    # чтобы привязать к какому-то пути (api/v1/products/pk/reviews/) (по дефолту по названию метода -> путь)
    # отзывы получаем через детали (определенный продукт, после нажатия на продукт видим отзывы), поэтому True
    @action(['GET', 'POST'], detail=True)
    def comments(self, request, pk=None):
        # получаем продукт по pk через get_object
        post = self.get_object()
        if request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        # если метод пост, то из запроса получаем данные
        data = request.data
        # в context передаем request чтобы достать юзера
        serializer = CommentSerializer(data=data, context={'request': request, 'post': post})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        queryset = Favorite.objects.all()
        queryset = queryset.filter(user=request.user)
        serializer = FavoriteSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        post = self.get_object()
        obj, created = Favorite.objects.get_or_create(user=request.user, post=post, )
        if not created:
            obj.favorite = not obj.favorite
            obj.save()
        favorites = 'added to favorites' if obj.favorite else 'removed from favorites'
        return Response(f'Successfully {favorites}', status=status.HTTP_200_OK)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # filterset_class = CommentFilter

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        return [IsAdminUser()]


class UpdateDeleteComment(UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthor]

    def get_serializer_context(self):
        return {'request': self.request}

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class LikesViewSet(ModelViewSet):
    queryset = Likes.objects.all()
    serializer_class = LikesSerializer
    permission_classes = [IsAuthenticated, ]
