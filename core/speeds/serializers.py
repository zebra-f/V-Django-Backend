from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, StringRelatedField

from django.shortcuts import get_object_or_404
from django.urls import reverse

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedReport, SpeedBookmark


class SpeedSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.StringRelatedField()
    feedback_counter = serializers.StringRelatedField()
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
            'author', 
            'is_public', 
            'feedback_counter',
            'user_speed_feedback'
            ]
        read_only_fields = ['id', 'created_at', 'author', 'feedback_counter']

    def get_user_speed_feedback(self, obj):
        return 0
    
    def get_url(self, obj):
        return reverse('myapp:my-model-detail', args=[obj.pk])


class SpeedFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedFeedback
        fields= ['id', 'vote', 'user', 'speed']
        extra_kwargs = {
            'user': {'write_only': True}
            }
    
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
                        speed_feedback_counter.downvotes -= 1
                if prev_vote == -1:
                    speed_feedback_counter.downvotes -= 1
                    if curr_vote == 1:
                        speed_feedback_counter.upvotes += 1
                speed_feedback_counter.save()
        
        return super().update(instance, validated_data)


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