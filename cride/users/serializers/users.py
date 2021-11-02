"""users serializers"""

#django
from django.conf import settings
from django.contrib.auth import authenticate,password_validation
from django.core.validators import RegexValidator

# django rest framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# models
from cride.users.models import User,Profile

# serializers
from cride.users.serializers.profiles import ProfileModelSerializer

# tasks
from cride.taskapp.tasks import send_confirmation_email

# Utilities
import jwt

class UserModelSerializer(serializers.ModelSerializer):

    profile = ProfileModelSerializer(read_only=True)

    """user model serializer"""
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile'
        )

class UserSignUpSerializer(serializers.Serializer):
    """user sign up serializer
    
    handle sign up data validation and user profile creation
    """
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +123456789 up to 15 digits'
    )
    phone_number = serializers.CharField(validators=[phone_regex])

    password = serializers.CharField(min_length=8,max_length=64)
    password_confirmation = serializers.CharField(min_length=8,max_length=64)

    first_name = serializers.CharField(min_length=2,max_length=30)
    last_name = serializers.CharField(min_length=2,max_length=30)

    def validate(self, data):
        passwd = data['password']
        passwd_conf = data['password_confirmation']

        if passwd != passwd_conf:
            raise serializers.ValidationError('password dont match')

        password_validation.validate_password(passwd)
        return data

    def create(self,data):
        data.pop('password_confirmation')
        user = User.objects.create_user(**data, is_verified=False, is_client=True)
        Profile.objects.create(user=user)
        send_confirmation_email.delay(user_pk=user.pk)
        return user


class UserLoginSerializer(serializers.Serializer):
    """user login serializers

    handle the login request data
    """
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self,data):
        """verify credentials"""
        user = authenticate(username=data['email'],password=data['password'])
        if not user:
            raise serializers.ValidationError('invalid credentials')
        if not user.is_verified:
            raise serializers.ValidationError('Account is not active yet')
        self.context['user'] = user
        return data

    def create(self,data):
        """generate or retrieve new token"""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class AccountVerificationSerializer(serializers.Serializer):

    token = serializers.CharField()
    
    def validate_token(self,data):
        try:
            payload = jwt.decode(data,settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('verifications link has expired')
        except jwt.PjJWTError:
            raise serializers.ValidationError('invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('invalid token')

        self.context['payload'] = payload
        return data
    
    def save(self):
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        user.is_verified=True
        user.save()