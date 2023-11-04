from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import APIException

from django.urls import reverse
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model

from . import logger
from .models import Speed, SpeedFeedback, SpeedReport, SpeedBookmark, Vote
from .validators import (
    name_validator,
    description_validator,
    category_validator,
    detail_validator,
    tags_validator,
)
from .fields import TagsField
from .decorators import prevent_unauthorized_create_and_data_reveal

from .services import sync_or_add_document_to_meiliserach
from core.common.decorators import restrict_field_updates


class BasicSpeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speed
        fields = [
            "id",
            "name",
            "description",
            "speed_type",
            "tags",
            "kmph",
            "estimated",
            "is_public",
            "user",
            "score",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["user"] = instance.user.username

        return representation


class SpeedBaseHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialzier for unauthenticated users.
    """

    tags = TagsField(validators=[tags_validator])

    name = serializers.CharField(validators=[name_validator])
    description = serializers.CharField(validators=[description_validator])

    class Meta:
        model = Speed
        fields = [
            "url",
            "id",
            "name",
            "description",
            "speed_type",
            "tags",
            "kmph",
            "estimated",
            "is_public",
            "user",
            "score",
        ]
        read_only_fields = ["id", "user", "score"]

    def get_url(self, obj):
        return reverse("myapp:my-model-detail", args=[obj.pk])

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["user"] = instance.user.username

        return representation


class SpeedHyperlinkedSerializer(SpeedBaseHyperlinkedSerializer):
    """
    Serialzier for authenticated users.
    """

    user_speed_feedback = serializers.SerializerMethodField()
    user_speed_bookmark = serializers.SerializerMethodField()

    class Meta(SpeedBaseHyperlinkedSerializer.Meta):
        fields = [
            *SpeedBaseHyperlinkedSerializer.Meta.fields,
            "user_speed_feedback",
            "user_speed_bookmark",
        ]
        read_only_fields = [
            *SpeedBaseHyperlinkedSerializer.Meta.read_only_fields,
            "user_speed_feedback",
            "user_speed_bookmark",
        ]

    def get_user_speed_feedback(self, obj) -> None | dict:
        if len(obj.user_speed_feedback) == 1:
            return obj.user_speed_feedback[0]
        return None

    def get_user_speed_bookmark(self, obj) -> None | dict:
        # a workaround for the 'POST' method
        request = self.context.get("request")
        if request.method == "POST":
            return None

        if len(obj.user_speed_bookmark) == 1:
            return obj.user_speed_bookmark[0]
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        method = self.context.get("request").method
        if method in ("POST", "PATCH", "PUT", "DELETE"):
            sync_or_add_document_to_meiliserach(
                index_name="speeds",
                action="add" if method == "POST" else "update",
                data={**representation},
            )

        return representation

    def create(self, validated_data):
        instance = super().create(validated_data)
        speed_feedback = SpeedFeedback(
            vote=Vote.UPVOTE, user=instance.user, speed=instance
        )
        speed_feedback.save()

        # don't save, a workaround for the 'POST' method
        instance.user_speed_feedback = [
            {
                "feedback_id": speed_feedback.id,
                "feedback_vote": speed_feedback.vote,
            },
        ]

        return instance

    def update(self, instance, validated_data):
        # ref: `core.speeds.views.SpeedViewSet.perform_delete`
        method = self.context.get("request").method
        if method == "DELETE":
            # set this here to bypass `read_only_fields`
            validated_data = {
                "user": get_user_model().objects.get(username="deleted"),
                "is_public": False,
            }

        return super().update(instance, validated_data)


class SpeedFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeedFeedback
        fields = ["id", "vote", "speed", "user"]
        read_only_fields = [
            "id",
            "user",
        ]

    def to_representation(self, instance):
        self.fields["speed"] = SpeedBaseHyperlinkedSerializer()

        representation = super().to_representation(instance)
        representation["user"] = instance.user.username
        return representation

    @prevent_unauthorized_create_and_data_reveal
    def create(self, validated_data):
        # this is a workaround since passing this validator into the Meta's `validators` attribute won't work
        # the 'user' field is only available during the 'create' operation in validated_data (passed by the 'perform_create' method).
        validator = UniqueTogetherValidator(
            queryset=SpeedFeedback.objects.all(),
            fields=["user", "speed"],
            message="The UNIQUE constraint failed; the speed object has already been voted on.",
        )
        validator(validated_data, self)
        return super().create(validated_data)

    @restrict_field_updates("speed", "user")
    def update(self, instance, validated_data):
        """
        Only the 'vote' field is modifiable via the HTTP `PATCH` method.
        The HTTP `PUT` method is disabled in the feedback related view.
        """

        prev_vote = instance.vote
        curr_vote = validated_data["vote"]
        if curr_vote == prev_vote:
            return instance

        # prevents a race conditions
        with transaction.atomic():
            speed = Speed.objects.select_for_update().get(id=instance.speed.id)

            if prev_vote == -1:
                speed.downvotes -= 1
            elif prev_vote == 1:
                speed.upvotes -= 1

            if curr_vote == -1:
                speed.downvotes += 1
            elif curr_vote == 1:
                speed.upvotes += 1

            speed.score = speed.upvotes - speed.downvotes
            try:
                speed.save()
                speed_feedback = super().update(instance, validated_data)
            except IntegrityError as e:
                logger.error(f"core.speeds.{__name__}; {str(e)}")
                raise APIException(
                    "An unexpected error occurred while processing your request. Please try again later."
                )
            except Exception as e:
                logger.warning(f"core.speeds.{__name__}; {str(e)}")
                raise APIException(
                    "An unexpected error occurred while processing your request. Please try again later."
                )

        # fix for the nested representation of the Speed's score
        speed_feedback.speed.score = speed.score
        return speed_feedback


class SpeedBookmarkSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        default="favorites", validators=[category_validator]
    )

    class Meta:
        model = SpeedBookmark
        fields = [
            "id",
            "category",
            "speed",
            "user",
        ]
        read_only_fields = [
            "id",
            "user",
        ]

    def to_representation(self, instance):
        self.fields["speed"] = SpeedBaseHyperlinkedSerializer()

        representation = super().to_representation(instance)
        representation["user"] = instance.user.username
        return representation

    @prevent_unauthorized_create_and_data_reveal
    def create(self, validated_data):
        # this is a workaround since passing this validator into the Meta's `validators` attribute won't work
        # the 'user' field is only available during the 'create' operation in validated_data (passed by the 'perform_create' method).
        validator = UniqueTogetherValidator(
            queryset=SpeedBookmark.objects.all(),
            fields=["user", "speed"],
            message="The UNIQUE constraint failed; the speed object is already bookmarked.",
        )
        validator(validated_data, self)
        return super().create(validated_data)

    @restrict_field_updates("speed", "user")
    def update(self, instance, validated_data):
        """
        Only the 'category' field is modifiable via the HTTP `PATCH` method.
        The HTTP `PUT` method is disabled in the bookmark related view.
        """
        return super().update(instance, validated_data)


class SpeedReportSerializer(serializers.ModelSerializer):
    detail = serializers.CharField(validators=[detail_validator])

    class Meta:
        model = SpeedReport
        fields = [
            "id",
            "report_reason",
            "detail",
            "user",
            "speed",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "updated_at"]

    def to_representation(self, instance):
        self.fields["speed"] = SpeedBaseHyperlinkedSerializer()

        representation = super().to_representation(instance)
        representation["user"] = instance.user.username
        return representation

    def create(self, validated_data):
        obj, created = SpeedReport.objects.update_or_create(
            user=validated_data["user"],
            speed=validated_data["speed"],
            defaults={
                "report_reason": validated_data["report_reason"],
                "detail": validated_data["detail"],
            },
        )

        return obj
