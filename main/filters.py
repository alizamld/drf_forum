from django_filters import rest_framework as filters

from main.models import Comment


# class PostFilter(filters.FilterSet):
#     rating_from = filters.NumberFilter(field_name='rating', lookup_expr='gte')
#     rating_to = filters.NumberFilter(field_name='rating', lookup_expr='lte')
#
#     class Meta:
#         model = Comment
#         fields = ['post']


# class PostFilter(filters.FilterSet):
#     price_from = filters.NumberFilter(field_name='price', lookup_expr='gte')
#     price_to = filters.NumberFilter(field_name='price', lookup_expr='lte')
#
#     class Meta:
#         model = Post
#         fields = ['category']
