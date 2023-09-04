from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import MaxValueValidator

from uuid import uuid4

from core.speeds.validators import CustomMinValueValidator


class Speed(models.Model):

    class Meta:
        ordering = ['-created_at']

    class SpeedType(models.TextChoices):
        AVERAGE = 'average'
        TOP = 'top'
        CONSTANT = 'constant'
        RELATIVE = 'relative'

    id = models.UUIDField(primary_key=True, default=uuid4)
    
    name = models.CharField(_('name'), max_length=128)
    description = models.CharField(_('description'), max_length=128, null=True, blank=True)
    speed_type = models.TextField(_('speed type'), choices=SpeedType.choices)
    tags = models.TextField(_('tags'), max_length=128)
    
    kmph = models.FloatField(_('speed in km/h'), validators=[
        MaxValueValidator(1_080_000_000),
        # CustomMinValueValidator checks whether a value is greater than 0
        CustomMinValueValidator(0)  
    ])
    estimated = models.BooleanField(_('estimated'), default=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)

    # for user:
    # >>> s1.feedback.add(user, through_defaults={"vote": 1})
    feedback = models.ManyToManyField(settings.AUTH_USER_MODEL, through='SpeedFeedback', related_name='+')

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __repr__(self) -> str:
        return self.name + ' ' + self.description


class Vote(models.IntegerChoices):
    DOWNVOTE = -1, _('Downvote')
    DEFAULT_STATE = 0, _('Default State')
    UPVOTE = 1, _('Upvote')


class SpeedFeedback(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="fb_unique_user_speed")
            ]

    # aka direction
    vote = models.IntegerField(_('vote'), choices=Vote.choices, default=Vote.DEFAULT_STATE)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE)
    

class SpeedFeedbackCounter(models.Model):
    speed = models.OneToOneField(Speed, on_delete=models.CASCADE, related_name='feedback_counter')
    
    downvotes = models.PositiveIntegerField(_('downvotes'), default=0)
    upvotes = models.PositiveIntegerField(_('upvotes'), default=0)

    @property
    def score(self) -> int:
        return self.upvotes - self.downvotes
    
    def recount_votes(self):
        with transaction.atomic():
            downvotes_counter = 0
            upvotes_counter = 0
            for feedback in SpeedFeedback.objects.select_for_update().filter(speed=self.speed):
                if feedback.vote == Vote.DOWNVOTE:
                    downvotes_counter += 1
                if feedback.vote == Vote.UPVOTE:
                    upvotes_counter += 1
        
            self.downvotes = downvotes_counter
            self.upvotes = upvotes_counter
            self.save(update_fields=['downvotes', 'upvotes'])

    @classmethod
    def recount_all_votes(cls):
        queryset = cls.objects.all()
        for object in queryset:
            object.recount_votes()
    
    def __str__(self):
        return f'{self.score}'


class SpeedBookmark(models.Model):
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="bm_unique_user_speed")
            ]

    category = models.CharField(_('category'), max_length=32, blank=True, null=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE, related_name='bookmark')


class SpeedReport(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="rp_unique_user_speed")
            ]
    
    class Report(models.TextChoices):
        SPAM = "spam"
        INCORRECT_DATA = "incorrcect data"
        NON_ENGLISH = "non english"
        INAPPROPRIATE_LANGUAGE = "inappropriate language"
        OTHER = "other"

    report = models.TextField(_('report'), choices=Report.choices, null=True, blank=True)
    other = models.TextField(_('other'), max_length=256, blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE, related_name='report')
