from django.urls import path

from .views  import *

urlpatterns = [
    path('messages/<int:sender>/<int:receiver>/', message_list),
    path('messages/', message_list),
    path('users/', user_list),
]
