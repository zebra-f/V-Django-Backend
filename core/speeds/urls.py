from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import SpeedViewSet

router = SimpleRouter()
router.register(r'speeds', SpeedViewSet)

app_name = 'speeds'

urlpatterns = []