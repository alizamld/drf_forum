from django.urls import path
from .views import *
#
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
# )

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('activate/', ActivationView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('change_password/', ChangePassword.as_view()),
    path('forgot_password/', ForgotPassword.as_view()),
    path('forgot_password_complete/', ForgotPasswordCompleteView.as_view()),
]
