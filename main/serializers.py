from django.db.models import Avg
from rest_framework import serializers
from .models import *


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('image', )

    def _get_image_url(self, obj):
        if obj.image:
            url = obj.image.url
            return url
        return ''

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = self._get_image_url(instance)
        return representation


class PostListSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'images']


class PostSerializer(serializers.ModelSerializer):
    # images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        # fields = '__all__'
        exclude = ('user', )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        images_data = request.FILES
        validated_data['user'] = user
        post = Post.objects.create(**validated_data)
        for image in images_data.getlist('images'):
            PostImage.objects.create(image=image, post=post)
        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        images_data = request.FILES
        instance.images.all().delete()
        for image in images_data.getlist('images'):
            PostImage.objects.create(image=image, post=instance)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = PostImageSerializer(instance.images.all(), many=True).data
        # representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        representation['likes'] = instance.likes.all().count()
        # representation['rating'] = instance.rating.aggregate(Avg('rating')).get("rating_avg")
        return representation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('user', 'post')

    def create(self, validated_data):
        # мы можем отправлять from view to serializer через context
        # request отправляет юзер, его мы получаем в request.user
        request = self.context.get('request')
        user = request.user
        post = self.context.get('post')
        # чтобы ошибки не было, мы должны взять пользователя, так как в fields мы его не заполняли
        validated_data['user'] = user
        validated_data['post'] = post
        return super().create(validated_data)


class LikesSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Likes
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        post = validated_data.get('post')
        like = Likes.objects.get_or_create(author=author, post=post)[0]
        like.likes = True if like.likes is False else False
        like.save()
        return like


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.email
        representation['post'] = instance.post.title
        return representation

