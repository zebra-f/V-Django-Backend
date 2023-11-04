from rest_framework.routers import SimpleRouter

from .views import (
    SpeedViewSet,
    SpeedFeedbackViewSet,
    SpeedBookmarkViewSet,
    SpeedReportViewSet,
)


router = SimpleRouter()
router.register(r"speeds", SpeedViewSet)
router.register(r"speeds-feedback", SpeedFeedbackViewSet)
router.register(r"speeds-bookmark", SpeedBookmarkViewSet)
router.register(r"speed-report", SpeedReportViewSet)

app_name = "speeds"
