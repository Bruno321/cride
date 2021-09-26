from cride.circles import permissions, views

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from cride.circles.permissions import IsCircleAdmin

from cride.circles.serializers import CircleModelSerializer
from cride.circles.models import Circle, Membership

from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

class CircleViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):

    serializer_class = CircleModelSerializer
    lookup_field = 'slug_name'

    filter_backends = (SearchFilter,OrderingFilter,DjangoFilterBackend)
    search_fields = ('slug_name','name')
    ordering_fields = ('rides_offered','rides_taken','name','created','member_limit')
    ordering = ('-members__count','-rides_offered','-rides_taken')
    filter_fields = ('verified','is_limited')

    def get_queryset(self):
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.filter(is_public=True)
        return queryset

    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action in ['update','partial_update']:
            permissions.append(IsCircleAdmin)
        return [permission() for permission in permissions]

    def perform_create(self,serializer):
        circle = serializer.save()
        user = self.request.user
        profile = user.profile
        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10
        )