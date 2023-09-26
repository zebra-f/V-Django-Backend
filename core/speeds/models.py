from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import ArrayField

from django.db import transaction

from uuid import uuid4

from core.speeds.validators import CustomMinValueValidator


class Speed(models.Model):

    class Meta:
        ordering = ['-updated_at']
        indexes = [GinIndex(fields=['tags'])]

    class SpeedType(models.TextChoices):
        AVERAGE = 'average'
        TOP = 'top'
        CONSTANT = 'constant'
        RELATIVE = 'relative'

    id = models.UUIDField(primary_key=True, default=uuid4)
    
    name = models.CharField(_('name'), max_length=128)
    description = models.CharField(_('description'), max_length=128, null=True, blank=True)
    speed_type = models.CharField(_('speed type'), choices=SpeedType.choices)
    tags = ArrayField(models.CharField(max_length=20), size=4, blank=True)
    
    kmph = models.FloatField(_('speed in km/h'), validators=[
        MaxValueValidator(1_080_000_000),
        # CustomMinValueValidator checks whether a value is greater than 0
        CustomMinValueValidator(0)  
    ])
    estimated = models.BooleanField(_('estimated'), default=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)

    feedbacks = models.ManyToManyField(settings.AUTH_USER_MODEL, through='SpeedFeedback', related_name='+')

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    # feedback counter 
    downvotes = models.PositiveIntegerField(_('downvotes'), default=0)
    # default `1` is set accordingly to SpeedFeedback; which is created by the `speed_post_save_handler` signal
    upvotes = models.PositiveIntegerField(_('upvotes'), default=1)
    score = models.IntegerField(_('score'), default=1)

    def set_score(self) -> int:
        self.score = self.upvotes - self.downvotes
        self.save()
        return self.score
    
    def recount_votes(self):
        downvotes_counter = 0
        upvotes_counter = 0
        with transaction.atomic():
            for feedback in SpeedFeedback.objects.select_for_update().filter(speed=self):
                if feedback.vote == Vote.DOWNVOTE:
                    downvotes_counter += 1
                if feedback.vote == Vote.UPVOTE:
                    upvotes_counter += 1
        
            self.downvotes = downvotes_counter
            self.upvotes = upvotes_counter
            self.score = upvotes_counter - downvotes_counter
            self.save(update_fields=['downvotes', 'upvotes', 'score'])

    @classmethod
    def recount_all_votes(cls):
        queryset = cls.objects.all()
        for object in queryset:
            object.recount_votes()

    def __repr__(self) -> str:
        return self.name + ' ' + self.description
    
    def __str__(self) -> str:
        return self.name + ' (' + self.description[:25] + '...)'


class Vote(models.IntegerChoices):
    DOWNVOTE = -1, _('Downvote')
    DEFAULT_STATE = 0, _('Default State')
    UPVOTE = 1, _('Upvote')


class SpeedFeedback(models.Model):

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="fb_unique_user_speed")
            ]

    # aka direction
    vote = models.IntegerField(_('vote'), choices=Vote.choices, default=Vote.DEFAULT_STATE)

    created_at = models.DateTimeField(_('created at'), default=timezone.now)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE, related_name='feedback')

    def __str__(self) -> str:
        return str(self.vote)
    

# class SpeedFeedbackCounter(models.Model):
#     speed = models.OneToOneField(Speed, on_delete=models.CASCADE, related_name='feedback_counter')
    
#     downvotes = models.PositiveIntegerField(_('downvotes'), default=0)
#     upvotes = models.PositiveIntegerField(_('upvotes'), default=0)

#     @property
#     def score(self) -> int:
#         return self.upvotes - self.downvotes
    
#     def recount_votes(self):
#         with transaction.atomic():
#             downvotes_counter = 0
#             upvotes_counter = 0
#             for feedback in SpeedFeedback.objects.select_for_update().filter(speed=self.speed):
#                 if feedback.vote == Vote.DOWNVOTE:
#                     downvotes_counter += 1
#                 if feedback.vote == Vote.UPVOTE:
#                     upvotes_counter += 1
        
#             self.downvotes = downvotes_counter
#             self.upvotes = upvotes_counter
#             self.save(update_fields=['downvotes', 'upvotes'])

#     @classmethod
#     def recount_all_votes(cls):
#         queryset = cls.objects.all()
#         for object in queryset:
#             object.recount_votes()
    
#     def __str__(self):
#         # don't modify the return statement
#         # the returned value is used by serializers.StringRelatedField()
#         return f'{self.score}'


class SpeedBookmark(models.Model):
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="bm_unique_user_speed")
            ]

    category = models.CharField(_('category'), max_length=32, blank=True, null=True)

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE, related_name='bookmark')

    def __str__(self) -> str:
        return self.category


class SpeedReport(models.Model):

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(fields=('user', 'speed'), name="rp_unique_user_speed")
            ]
    
    class ReportReason(models.TextChoices):
        SPAM = "spam"
        INCORRECT_DATA = "incorrect data"
        NON_ENGLISH = "non english"
        INAPPROPRIATE_LANGUAGE = "inappropriate language"
        OTHER = "other"

    report_reason = models.CharField(_('report reason'), choices=ReportReason.choices, null=True, blank=True)
    detail = models.CharField(_('detail'), max_length=256, blank=True, null=True)

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    speed = models.ForeignKey(Speed, on_delete=models.CASCADE, related_name='report')

    def __str__(self) -> str:
        return self.report_reason + ' (' + self.detail[:25] + '...)'
