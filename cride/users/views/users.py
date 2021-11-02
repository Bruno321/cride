"""users view"""

#django rest framework
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

# permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from cride.users.permissions import IsAccountOwner


# serializers
from cride.circles.serializers import CircleModelSerializer
from cride.users.serializers import (
    UserLoginSerializer, 
    UserModelSerializer,
    UserSignUpSerializer,
    AccountVerificationSerializer
)

from cride.users.models import User
from cride.circles.models import Circle

from cride.users.serializers.profiles import ProfileModelSerializer


class UserViewSet(
    mixins.RetrieveModelMixin, 
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet):

    # que modelo usara para ser listado
    queryset = User.objects.filter(is_active=True,is_client=True)
    # que serializer usara
    serializer_class = UserModelSerializer
    lookup_field = 'username'

    def get_permissions(self):
        if self.action in ['signup','login','verify']:
            permissions = [AllowAny]
        elif self.action == ['retrieve','update','partial_update']:
            permissions = [IsAuthenticated,IsAccountOwner]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    @action(detail=False, methods=['post'])
    def login(self,request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user,token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'access_token':token
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def signup(self,request):
        """handle http post request"""
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
            
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False,methods=['post'])
    def verify(self,request):
        """handle http post request"""
        serializer = AccountVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'message': 'congratulation go and share rides'
        }
            
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True,methods=['put','patch'])
    def profile(self,request,*args,**kwargs):
        user = self.get_object()
        profile = user.profile
        partial = request.method == 'PATCH'
        serializer = ProfileModelSerializer(
            profile,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = UserModelSerializer(user).data
        return Response(data)

    def retrieve(self,request,*args,**kwargs):
        response = super(UserViewSet, self).retrieve(request,*args,*kwargs)
        circles = Circle.objects.filter(
            members=request.user,
            membership__is_active=True,
            is_active=True
        )
        data = {
            'user':response.data,
            'circles':CircleModelSerializer(circles, many=True).data
        }
        response.data = data
        return response