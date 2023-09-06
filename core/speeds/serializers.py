from typing import Union

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, StringRelatedField

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django import forms
from django.db import IntegrityError

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedReport, SpeedBookmark
from core.users.models import User
from .validators import name_validator, description_validator
from .fields import TagsField


class SpeedSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagsField()
    feedback_counter = serializers.StringRelatedField()
    # user_speed_feedback directions:
    # 1 upvote 
    # 0 default, 
    # -1 downvote, 
    # -2 no data for logged in user,
    # -3 not logged in user
    # -4 a response for the update/post method default 
    user_speed_feedback = serializers.SerializerMethodField()
    user_speed_bookmark = serializers.SerializerMethodField()

    # validating Meta class fields
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
            'user_speed_feedback',
            'user_speed_bookmark',
            ]
        read_only_fields = ['id', 'created_at', 'user', 'feedback_counter', 'user_speed_feedback', 'user_speed_bookmark']

    def get_user_speed_feedback(self, obj) -> int:
        try:
            # obj.user_speed_feebdack might be equal to 0
            if obj.user_speed_feedback:
                return obj.user_speed_feedback
            return -2
        except:
            # related to a response of the post/update method response 
            # should never happen, workaround in `create` and `update` method
            return -4
    
    def get_user_speed_bookmark(self, obj) -> Union[None, str]:
        try:
            if obj.user_speed_bookmark:
                return obj.user_speed_bookmark
            # obj.user_speed_feedback == False
            return None
        except:
            # related to a response of the post/update method
            # should never happen, workaround in `create` and `update` method
            return None
    
    def get_url(self, obj):
        return reverse('myapp:my-model-detail', args=[obj.pk])
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        return representation
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        # default set by a signal
        instance.user_speed_feedback = 1
        instance.user_speed_bookmark = None
        return instance
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.user_speed_feedback = -4
        instance.user_speed_bookmark = None
        return instance


class SpeedFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpeedFeedback
        fields = [
            'id', 
            'vote', 
            'speed', 
            'user'
            ]
        read_only_fields = ['id', 'speed']
    
    def update(self, instance, validated_data):
        # vote field may be eqaul to 0
        if validated_data.get('vote', None) != None:
            prev_vote = instance.vote
            curr_vote = validated_data['vote']
            if prev_vote != curr_vote:
                speed_feedback_counter = get_object_or_404(SpeedFeedbackCounter, speed=instance.speed)
                if prev_vote == 1:
                    speed_feedback_counter.upvotes -= 1
                    if curr_vote == -1:
                        speed_feedback_counter.downvotes += 1
                if prev_vote == -1:
                    speed_feedback_counter.downvotes -= 1
                    if curr_vote == 1:
                        speed_feedback_counter.upvotes += 1
                speed_feedback_counter.save()
        
        return super().update(instance, validated_data)

 
class SpeedFeedbackFrontendSerializer(serializers.ModelSerializer):
    ''' Utilized by methods in views.py tailored for frontend requests that do not include a Vote pk. '''

    class Meta:
        model = SpeedFeedback
        fields = ['vote', 'speed']

    
class SpeedBookmarkSerializer(serializers.ModelSerializer):
    category = serializers.CharField(default="favorites")

    class Meta:
        model= SpeedBookmark
        fields= [
            'id', 
            'category', 
            'user', 
            'speed'
            ]
        read_only_fields = ['id', 'user',]

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            if str(e) == "UNIQUE constraint failed: speeds_speedbookmark.user_id, speeds_speedbookmark.speed_id":
                raise serializers.ValidationError("UNIQUE constraint failed; the speed is already bookmarked.")
            raise serializers.ValidationError("Something went wrong.")
        except Exception as e:
            raise serializers.ValidationError("Something went wrong.")
        
    def update(self, instance, validated_data):
        """ 
        Only the 'category' field is modifiable via the PATCH method.
        The PUT method is disabled in views.
        """
        if 'user' in validated_data:
            raise serializers.ValidationError("Can't change the user field.")
        if 'speed' in validated_data:
            raise serializers.ValidationError("Can't change the speed field.")
        return super().update(instance, validated_data)

# TODO   


class SpeedReportSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedReport
        fields= ['id', 'report', 'other', 'user', 'speed']
        read_only_fields = ['id']


