
from datetime import timedelta
from cride.rides import serializers
from rest_framework import mixins,viewsets, status
from cride.rides.serializers import (
    CreateRideSerializer,RideModelSerializer,JoinRideSerializer, EndRideSerializer)
from cride.circles.models import Circle
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from cride.rides.permissions.rides import IsRideOwner, IsNotRideOwner
from rest_framework.decorators import action
from rest_framework.response import Response

class RideViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    # serializer_class = CreateRideSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ('departure_date','arrival_date','available_seats')
    ordering_fields = ('departure_date', 'arrival_date','available_seats')
    search_fields = ('departure_location','arrival_location')

    def dispatch(self,request,*args,**kwargs):
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle,slug_name=slug_name)               
        return super(RideViewSet, self).dispatch(request,*args,**kwargs)

    def get_permissions(self):
        """Asign permission based on action"""
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action in ['update','partial_update','finish']:
            permissions.append(IsRideOwner)
        if action == 'join':
            permissions.append(IsNotRideOwner)
        return [p() for p in permissions]

    def get_serializer_context(self):
        """add circle to serializer context"""
        context = super(RideViewSet, self).get_serializer_context()
        context['circle'] = self.circle

        return context

    def get_serializer_class(self):
        """Return serializer based on action"""
        if self.action == 'create':
            return CreateRideSerializer
        if self.action == 'update':
            return JoinRideSerializer
        if self.action == 'finish':
            return EndRideSerializer
        return RideModelSerializer

    def get_queryset(self):
        """return active circles rides"""
        if self.action != 'finish':
            offset = timezone.now() + timedelta(minutes=10)
            return self.circle.rides_set.filter(
                departure_date__gte=offset,
                is_active=True,
                available_seats__gte=1
            )
        return self.circle.ride_set.all()

    @action(detail=True, methods=['post'])
    def join(self, request, *args, **kwargs):
        """Add requesting user to ride"""
        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={'passenger':request.user.pk},
            context={'ride':ride,'circle':self.circle},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data,status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finish(self,request,*args,**kwargs):
        """call by owners to finish a ride"""
        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={'is_active':False,'current_time':timezone.now()},
            context=self.get_serializer_context(),
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data,status=status.HTTP_200_OK)