from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, StringRelatedField

from django.shortcuts import get_object_or_404
from django.urls import reverse

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedReport, SpeedBookmark
from core.users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username'
            ]


class SpeedSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    feedback_counter = serializers.StringRelatedField()
    # user_speed_feedback directions:
    # 1 upvote 
    # 0 default, 
    # -1 downvote, 
    # -2 no data for logged in user,
    # -3 not logged in user
    user_speed_feedback = serializers.SerializerMethodField()

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
            'user', 
            'is_public', 
            'feedback_counter',
            'user_speed_feedback'
            ]
        read_only_fields = ['id', 'created_at', 'user', 'feedback_counter', 'user_speed_feedback']

    def get_user_speed_feedback(self, obj):
        print(obj)
        if obj.user_speed_feedback:
            return obj.user_speed_feedback
        return -2
    
    def get_url(self, obj):
        return reverse('myapp:my-model-detail', args=[obj.pk])


class SpeedFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpeedFeedback
        fields = ['id', 'vote', 'speed', 'user']
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
    ''' Utilized by methods tailored for frontend requests, that not include a Vote pk '''

    class Meta:
        model = SpeedFeedback
        fields = ['vote', 'speed', 'user']


    def create(self, validated_data):

        return super().create(validated_data)
        

class SpeedReportSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedReport
        fields= ['id', 'report', 'other', 'user', 'speed']
        read_only_fields = ['id']
        extra_kwargs = {
            'user': {'write_only': True},
            'speed': {'write_only': True}
            }


class SpeedBookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedBookmark
        fields= ['id', 'category', 'user', 'speed']
        read_only_fields = ['id']
        extra_kwargs = {
            'user': {'write_only': True},
            'speed': {'write_only': True}
            }