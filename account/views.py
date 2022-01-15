from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from account.serializers import *


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Successfully signed up.', status=status.HTTP_201_CREATED)


class ActivationView(APIView):
    def post(self, request):
        data = request.data
        serializer = ActivationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.activate()
        return Response('You have successfully activated your account')


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        # Token.objects.filter(user=user).delete() <- can also delete this way
        # auth_token через related name удалили
        user.auth_token.delete()
        return Response('You have successfully logged out.')


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = ChangePasswordSerializer(data=data,
                                              context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.set_new_pass()
        return Response('You have updated your password')


class ForgotPassword(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.send_code()
        return Response('Code was sent to your email.')


class ForgotPasswordCompleteView(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordCompleteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.set_new_pass()
        return Response('You have reset your password.')
