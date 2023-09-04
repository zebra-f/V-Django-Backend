from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import SpeedViewSet, SpeedFeedbackViewSet, SpeedBookmarkViewSet

router = SimpleRouter()
router.register(r'speeds', SpeedViewSet)
router.register(r'speeds-feedback',SpeedFeedbackViewSet)
router.register(r'speeds-bookmark',SpeedBookmarkViewSet)

app_name = 'speeds'

urlpatterns = []