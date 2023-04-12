from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import MaxValueValidator

from uuid import uuid4

from core.speeds.validators import CustomMinValueValidator


class Speed(models.Model):

    class Meta:
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid4)
    
    name = models.CharField(_('name'), max_length=128)
    description = models.CharField(_('description'), max_length=128, null=True, blank=True)
    tags = models.TextField(_('tags'), max_length=128)
    kmph = models.PositiveIntegerField(_('speed'), validators=[
        MaxValueValidator(1_080_000_000),
        # CustomMinValueValidator checks whether a value is greater than 0
        CustomMinValueValidator(0)  
    ])

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    public = models.BooleanField(default=True)

    # for author:
    # >>> s1.feedback.add(user, through_defaults={"vote": 1})
    feedback = models.ManyToManyField(settings.AUTH_USER_MODEL, through='SpeedFeedback', related_name='+')

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)


class SpeedFeedback(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="fb_unique_user_speed")
            ]

    class Vote(models.IntegerChoices):
        DOWNVOTE = -1, _('Downvote')
        DEFAULT_STATE = 0, _('Default State')
        UPVOTE = 1, _('Upvote')

    vote = models.IntegerField(_('vote'), choices=Vote.choices, default=Vote.DEFAULT_STATE)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE)


class SpeedReport(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="rp_unique_user_speed")
            ]
    
    class Report(models.TextChoices):
        SPAM = "S"
        INCORRECT_DATA = "I"
        NON_ENGLISH = "NE"
        INAPPROPRIATE_LANGUAGE = "IL"
        OTHER = "O"

    report = models.TextField(_('report'), choices=Report.choices, null=True, blank=True)
    other = models.TextField(_('other'), max_length=256, blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE)


class SpeedBookmark(models.Model):
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="bm_unique_user_speed")
            ]

    category = models.CharField(_('category'), max_length=64, blank=True, null=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE)
    

    

    
