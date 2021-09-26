"""Circles urls"""

# django
from django.urls import path, include

# views
from .views import circles as circle_views

from rest_framework.routers import DefaultRouter

from .views import memeberships as membership_views

router = DefaultRouter()
router.register(r'circles',circle_views.CircleViewSet,basename='circle')
router.register(
    r'circles/(?P<slug_name>[a-zA-Z0-9_-]+)/members',
    membership_views.MembershipViewSet,
    basename='membership'
)

urlpatterns = [
    path('', include(router.urls))
]
#urlpatterns = [
#    path('circles/',list_circles),
#    path('circles/create/',create_circle)
#]

