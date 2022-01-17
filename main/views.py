from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from main.models import *
from main.permissions import IsAuthor
from main.serializers import *


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()

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

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        images = data.pop('images', [])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        for image in images:
            PostImage.objects.create(post=post, image=image)
        return Response(serializer.data, status=201)

    def get_queryset(self):
        queryset = super().get_queryset()
        days_count = int(self.request.query_params.get('days', 0))
        if days_count > 0:
            start_date = timezone.now() - timedelta(days=days_count)
            queryset = queryset.filter(created_at__gte=start_date)
        return queryset

    @action(detail=False, methods=['GET'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(user=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        # request_params = request.GET (возвращает словарь, в ктр хранится искомое слово
        q = request.query_params.get('q')
        print(q)
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
