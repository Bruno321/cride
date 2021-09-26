
from django.utils import timezone
from cride.circles.models.invitations import Invitation
from rest_framework import serializers

from cride.users.serializers import UserModelSerializer

from cride.circles.models import Membership

class MembershipModelSerializer(serializers.ModelSerializer):

    user = UserModelSerializer(read_only=True)
    invited_by = serializers.StringRelatedField()
    joined_at = serializers.DateTimeField(source='created',read_only=True)

    class Meta:
        model = Membership
        fields = (
            'user',
            'is_admin',
            'is_active',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered',
            'joined_at'
        )
        read_only_fields = (
            'user',
            'used_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered'
        )


class AddMemberSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(min_length=8)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self,data):
        circle = self.context['circle']
        user = data
        q = Membership.objects.filter(circle=circle,user=user)
        if q.exists():
            raise serializers.ValidationError('User is already member of the circle')

    def validate_invitation_code(self,data):
        try:
            invitation = Invitation.ojects.get(
                code=data,
                circle=self.context['circle'],
                used=False
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('invalid invitation code')
        self.context['invitation'] = invitation
        return data

    def validate(self,data):
        circle = self.context['circle']
        if circle.is_limited and circle.members.count() >= circle.members_limit:
            raise serializers.ValidationError('circle has reached its members limit')
        return data

    def create(self,data):
        circle = self.context['circle']
        invitation = self.context['invitation']
        user = data['user']

        now = timezone.now()

        member = Membership.objects.create(
            user=user,
            profile=user.profile,
            circle=circle,
            invited_by=invitation.issued_by
        )

        invitation.used_by = user
        invitation.used = True
        invitation.used_at = now
        invitation.save()

        issuer = Membership.objects.get(user=invitation.issued_by,circle=circle)
        issuer.used_invitations += 1
        issuer.remaining_invitations -= 1
        issuer.save()

        return member

