from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, StringRelatedField
from rest_framework.validators import UniqueTogetherValidator

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django import forms
from django.db import IntegrityError

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedReport, SpeedBookmark
from .validators import (
    name_validator, 
    description_validator, 
    category_validator, 
    detail_validator
)
from .fields import TagsField
from .decorators import prevent_unauthorized_create_and_data_reveal
from core.users.models import User
from core.common.decorators import restrict_field_updates


class BaseSpeedSerializer(serializers.HyperlinkedModelSerializer):
    ''' 
    Serialzier for unauthenticated users. 
    '''
    tags = TagsField()
    feedback_counter = serializers.StringRelatedField()

    name = serializers.CharField(validators=[name_validator])
    description = serializers.CharField(validators=[description_validator])

    class Meta:
        model = Speed
        fields = [
            'url', 
            'id', 
            'name', 
            'description', 
            'speed_type', 
            'tags', 
            'kmph', 
            'estimated', 
            'is_public', 
            'user', 
            'feedback_counter',
            ]
        read_only_fields = [
            'id',
            'user', 
            'feedback_counter'
            ]

    def get_url(self, obj):
        return reverse('myapp:my-model-detail', args=[obj.pk])

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['user'] = instance.user.username
        representation['feedback_counter'] = int(representation['feedback_counter'])
        
        return representation


class SpeedSerializer(BaseSpeedSerializer):
    ''' 
    Serialzier for authenticated users. 
    '''
    user_speed_feedback = serializers.SerializerMethodField()
    user_speed_bookmark = serializers.SerializerMethodField()

    class Meta(BaseSpeedSerializer.Meta):
        fields = [
            *BaseSpeedSerializer.Meta.fields, 
            'user_speed_feedback',
            'user_speed_bookmark',
            ]
        read_only_fields = [
            *BaseSpeedSerializer.Meta.read_only_fields, 
            'user_speed_feedback', 
            'user_speed_bookmark',
            ]

    def get_user_speed_feedback(self, obj) -> None | dict:
        if len(obj.user_speed_feedback) == 1:
            return obj.user_speed_feedback[0]
        return None
    
    def get_user_speed_bookmark(self, obj) -> None | dict:
        if len(obj.user_speed_bookmark) == 1:
            return obj.user_speed_bookmark[0]
        return None


class SpeedFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpeedFeedback
        fields = [
            'id', 
            'vote', 
            'speed', 
            'user'
            ]
        read_only_fields = [
            'id', 
            'user',
            ]

    def to_representation(self, instance):
        self.fields['speed'] = BaseSpeedSerializer()
        
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        return representation
    
    @prevent_unauthorized_create_and_data_reveal
    def create(self, validated_data):
        # this is a workaround since passing this validator into the Meta's `validators` attribute won't work
        # the 'user' field is only available during the 'create' operation in validated_data (passed by the 'perform_create' method).
        validator = UniqueTogetherValidator(
                queryset=SpeedFeedback.objects.all(),
                fields=['user', 'speed'],
                message='The UNIQUE constraint failed; the speed object has already been voted on.'
            )
        validator(validated_data, self)    
        return super().create(validated_data)
    
    @restrict_field_updates('speed', 'user')
    def update(self, instance, validated_data):
        '''
        Only the 'vote' field is modifiable via the HTTP `PATCH` method.
        The HTTP `PUT` method is disabled in the feedback related view.
        '''
        # temporary solution
        x =  super().update(instance, validated_data)
        SpeedFeedbackCounter.recount_all_votes()
        return x


class SpeedBookmarkSerializer(serializers.ModelSerializer):
    category = serializers.CharField(default="favorites", validators=[category_validator])

    class Meta:
        model= SpeedBookmark
        fields= [
            'id', 
            'category',
            'speed',
            'user', 
            ]
        read_only_fields = [
            'id', 
            'user',
            ]

    def to_representation(self, instance):
        self.fields['speed'] = BaseSpeedSerializer()

        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        return representation

    @prevent_unauthorized_create_and_data_reveal
    def create(self, validated_data):
        # this is a workaround since passing this validator into the Meta's `validators` attribute won't work
        # the 'user' field is only available during the 'create' operation in validated_data (passed by the 'perform_create' method).
        validator = UniqueTogetherValidator(
                queryset=SpeedBookmark.objects.all(),
                fields=['user', 'speed'],
                message='The UNIQUE constraint failed; the speed object is already bookmarked.'
            )
        validator(validated_data, self)
        return super().create(validated_data)
    
    @restrict_field_updates('speed', 'user')
    def update(self, instance, validated_data):
        '''
        Only the 'category' field is modifiable via the HTTP `PATCH` method.
        The HTTP `PUT` method is disabled in the bookmark related view.
        '''
        return super().update(instance, validated_data)


class SpeedReportSerializer(serializers.ModelSerializer):
    detail = serializers.CharField(validators=[detail_validator])

    class Meta:
        model= SpeedReport
        fields= [
            'id', 
            'report_reason', 
            'detail', 
            'user', 
            'speed',
            'updated_at'
            ]
        read_only_fields = [
            'id', 
            'user', 
            'updated_at'
            ]

    def to_representation(self, instance):
        self.fields['speed'] = BaseSpeedSerializer()
        
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        return representation

    def create(self, validated_data):
        obj, created = SpeedReport.objects.update_or_create(
            user=validated_data['user'],
            speed=validated_data['speed'],
            defaults={
                "report_reason": validated_data['report_reason'],
                "detail": validated_data['detail']
                }
            )
        
        return obj