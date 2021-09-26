"""rides permissions"""

# Django rest framework
from rest_framework.permissions import BasePermission

class IsRideOwner(BasePermission):
    """Verify requesting user is the ride create"""

    def has_object_permission(self,request,view,obj):
        return request.user == obj.offered_by

class IsNotRideOwner(BasePermission):
    """Verify users that arent the ride create"""

    def has_object_permission(self,request,view,obj):
        return not request.user == obj.offered_by

