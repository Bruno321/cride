"""users urls"""

# django
from django.urls import path, include

from rest_framework.routers import DefaultRouter

# views
from .views import users as users_views

router = DefaultRouter()
router.register(r'users',users_views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]