from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import SpeedViewSet, SpeedFeedbackViewSet

router = SimpleRouter()
router.register(r'speeds', SpeedViewSet)
router.register(r'speeds-feedback',SpeedFeedbackViewSet)

app_name = 'speeds'

urlpatterns = []