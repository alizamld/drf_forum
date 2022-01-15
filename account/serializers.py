from django.contrib.auth import get_user_model, authenticate
from django.utils.crypto import get_random_string
from rest_framework import serializers
from .models import MyUser
from .tasks import send_activation_code, send_activation_code_forgot_pass

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'password_confirm')

    def validate(self, validated_data):
        password = validated_data.get('password')
        password_confirm = validated_data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match!')
        return validated_data

    def create(self, validated_data):
        """ this func is calling when self.save() is called"""
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = MyUser.objects.create_user(email=email, password=password)
        send_activation_code.delay(email=user.email, activation_code=str(user.activation_code))
        return user


class ActivationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6, required=True)

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            return serializers.ValidationError('Пользователь не найден')
        return code

    def activate(self):
        code = self.validated_data.get('code')
        user = User.objects.get(activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        label='Password',
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                message = 'Unable to log in'
                raise serializers.ValidationError(message, code='authorization')
        else:
            message = 'Must include "email" and "password".'
            raise serializers.ValidationError(message, code='authorization')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=6)
    new_pass = serializers.CharField(min_length=6)
    new_pass_confirm = serializers.CharField(min_length=6)

    def validate_old_password(self, old_password):
        # request получаем из контекста
        user = self.context.get('request').user
        if not user.check_password(old_password):
            raise serializers.ValidationError('Укажите верный текущий пароль')
        return old_password

    def validate(self, validated_data):
        new_pass = validated_data.get('new_pass')
        new_pass_confirm = validated_data.get('new_pass_confirm')
        if new_pass != new_pass_confirm:
            raise serializers.ValidationError('Неверный пароль или его подтверждение')
        return validated_data

    def set_new_pass(self):
        new_pass = self.validated_data.get('new_pass')
        user = self.context.get('request').user
        user.set_password(new_pass)
        user.save()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, email):
        email = email['email']
        if not User.objects.filter(email=email):
            raise serializers.ValidationError('No email found.')
        return email

    def send_code(self):
        email = self.validated_data
        user = User.objects.get(email=email)
        user.create_activation_code()
        # print(code)
        send_activation_code_forgot_pass(email=user.email, activation_code=str(user.activation_code))


class ForgotPasswordCompleteSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)
    new_pass = serializers.CharField(min_length=6)
    new_pass_confirm = serializers.CharField(min_length=6)

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('User is not found')
        return code

    def validate(self, validated_data):
        new_pass = validated_data.get('new_pass')
        new_pass_confirm = validated_data.get('new_pass_confirm')
        if new_pass != new_pass_confirm:
            raise serializers.ValidationError('Incorrect password or confirmation')
        return validated_data

    def set_new_pass(self):
        code = self.validated_data.get('code')
        new_pass = self.validated_data.get('new_pass')
        user = User.objects.get(activation_code=code)
        user.set_password(new_pass)
        user.save()

