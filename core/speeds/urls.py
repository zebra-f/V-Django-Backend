from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpeedViewSet

router = DefaultRouter()
router.register(r'speeds', SpeedViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
