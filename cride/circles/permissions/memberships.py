from cride.circles.models.memebership import Membership
from rest_framework.permissions import BasePermission

class IsActiveCircleMember(BasePermission):
    def has_permission(self,request,view):
        try:
            Membership.objects.get(
                user=request.user,
                circle=view.circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False
        return True


class IsSelfMember(BasePermission):
    def has_permission(self,request,view):
        obj = view.get_object()
        return self.has_object_permission(request,view,obj)

    def has_object_permission(self,request,view,obj):
        return request.user == obj.user