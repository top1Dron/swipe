import logging

from rest_framework import serializers

from users.models import Developer, User, Client, Agent, Notary

logger = logging.getLogger(__name__)

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('first_name', 'last_name', 'phone_number', 'email', 'client')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'email')

class ClientSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone_number = serializers.CharField(source='user.phone_number')
    password = serializers.CharField(source='user.password', write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'agent', 'password', 'password2')

    def validate(self, data):
        password2 = data.pop('password2', None)
        if (self.partial and data.get('user').get('password') is None):
            pass
        else:
            if data['user']['password'] != password2:
                raise serializers.ValidationError('Пароли не совпадают')
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['user']['email'], 
            phone_number=validated_data['user']['phone_number'], 
            password=validated_data['user']['password']
        )
        user.first_name = validated_data['user']['first_name']
        user.last_name = validated_data['user']['last_name']
        user.save()
        return user.client
    
    def update(self, instance, validated_data):
        client = self.context['request'].user.client
        if client.pk != instance.pk:
            raise serializers.ValidationError('Вы не можете редактировать данные другого пользователя')

        user_data = validated_data.pop('user', {})
        user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.update(instance.user, user_data)
        super(ClientSerializer, self).update(instance, validated_data)
        return instance

class DeveloperSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone_number = serializers.RegexField(source='user.phone_number', regex=r'^(?:\+38)?(?:\(0[0-9][0-9]\)[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|044[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|0[0-9][0-9][0-9]{7})$')
    password = serializers.CharField(source='user.password', write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = Developer
        exclude = 'user',

    def validate(self, data):
        password2 = data.pop('password2', None)
        if data['user']['password'] != password2:
            raise serializers.ValidationError('Пароли не совпадают')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['user']['email'], 
            phone_number=validated_data['user']['phone_number'], 
            password=validated_data['user']['password']
        )
        user.first_name = validated_data['user']['first_name']
        user.last_name = validated_data['user']['last_name']
        user.save()
        dev = Developer.objects.create(user=user)
        return dev


class NotarySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone_number = serializers.RegexField(source='user.phone_number', regex=r'^(?:\+38)?(?:\(0[0-9][0-9]\)[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|044[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|0[0-9][0-9][0-9]{7})$')
    password = serializers.CharField(source='user.password', write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = Notary
        exclude = 'user',

    def validate(self, data):
        password2 = data.pop('password2', None)
        if data['user']['password'] != password2:
            raise serializers.ValidationError('Пароли не совпадают')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['user']['email'], 
            phone_number=validated_data['user']['phone_number'], 
            password=validated_data['user']['password']
        )
        user.first_name = validated_data['user']['first_name']
        user.last_name = validated_data['user']['last_name']
        user.save()
        dev = Notary.objects.create(user=user)
        return dev