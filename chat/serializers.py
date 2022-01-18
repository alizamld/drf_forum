from account.models import MyUser
from rest_framework import serializers
from chat.models import Message
from rest_framework.permissions import IsAuthenticated


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = ['email', 'password']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.email')
    receiver = serializers.SlugRelatedField(many=False, slug_field='email', queryset=MyUser.objects.all())

    permission_classes = [IsAuthenticated, ]
    
    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        print(self.context['request'])
        request = self.context.get('request')
        sender = request.user
        validated_data['sender'] = sender
        return super().create(validated_data)
