
from rest_framework import serializers
from cride.rides.models import Ride
from datetime import timedelta
from django.utils import timezone
from cride.circles.models import Membership
from cride.users.serializers import UserModelSerializer
from cride.users.models import User

class RideModelSerializer(serializers.ModelSerializer):
    """Ride model serializer"""

    offerd_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField()
    
    passangers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = (
            'offered_by',
            'offered_in',
            'raiting'
        )

    def update(self,instance,data):
        """Allow updates only before departure date"""
        now = timezone.now()
        if instance.departure_date <= now:
            raise serializers.ValidationError('on going rides cannot be modified')
        return super(RideModelSerializer, self).update(instance,data)

class CreateRideSerializer(serializers.ModelSerializer):

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1,max_value=15)

    class Meta:
        model = Ride
        exclude = (
            'offered_in',
            'passengers',
            'raiting',
            'is_active'
        )

    def validate_departure_date(self,data):
        min_date = timezone.now + timedelta(minutes=10)     
        if data < min_date:
            raise serializers.ValidationError('departure time must be at least pass the next 20 minutes')

        return data

    def validate(self,data):
        """validate. 
        
        Verify that the person who offers the ride is member
        and also the same user making the request
        """
        if self.context['request'].user != data['offered_by']:
            raise serializers.ValidationError('Rides offered on behalf of other are not allowed')
        
        user = data['offered_by']
        circle = self.context['circle']
        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle') 

        if data['arrival_date'] <= data['departure_date']:
            raise serializers.ValidationError('Departure date must happen after arrival date') 

        self.context['membership'] = membership
        return data

    def create(self,data):
        """upgrade ride and update stats"""
        circle = self.context['circle']
        ride = Ride.objects.create(**data, circle=circle)

        # circle
        circle.rides_offered += 1
        circle.save()

        # membership
        membership = self.context['membership']
        membership.rides_offered += 1
        membership.save()

        # profile
        profile = data['offered_by'].profile
        profile.offered_by += 1
        profile.save()

        return ride


class JoinRideSerializer(serializers.ModelSerializer):
    """Join ride serializer"""

    passenger = serializers.IntegerField()

    class Meta:
        """meta class"""
        model = Ride
        fields = ('passengers',)

    def validate_passenger(self,data):
        """verify passenger exists and is a circle member"""
        try:
            user = User.objects.get(pk=data)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid passengers')

        circle = self.context['circle']
        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle') 

        self.context['user'] = user
        self.context['user'] = membership
        return data

    def validate(self,data):
        """verify rides allow passengers"""
        ride = self.context['ride']
        if ride.departure_date <= timezone.now():
            raise serializers.ValidationError("you cant join this ride now")

        if ride.available_seats < 1:
            raise serializers.ValidationError("Ride is alreeady full")

        if Ride.objects.filter(passengers__pk=sdata['passenger']):
            raise serializers.ValidationError("Passenger is alreeady in this trip")

        return data

    def update(self,instance,data):
        """Add passenger to ride, and update stats"""
        ride = self.context['ride']
        circle = self.context['circle']
        user = self.context['user']

        ride.passengers.add(user)

        # profile
        profile = user.profile
        profile.rides_taken += 1
        profile.save()

        # membership
        member = self.context['member']
        member.rides_taken += 1

        # circle
        circle = self.context['circle']
        circle.rides_taken += 1
        circle.save()

        return ride


class EndRideSerializer(serializers.ModelSerializer):
    """End ride serializer"""

    current_time = serializers.DateTimeField()

    class Meta:
        
        model = Ride
        fields = ('is_active','current_time')

    def validate_current_time(self,data):
        """verify ride in deed started"""

        ride = self.context['view'].get_object()
        if data <= ride.departure_date:
            raise serializers.Validation_error('Ride has not started yet')
        
        return data