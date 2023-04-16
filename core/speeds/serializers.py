from rest_framework import serializers

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedReport, SpeedBookmark


class SpeedSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Speed
        fields = ['url', 'id', 'name', 'description', 'speed_type', 'tags', 'kmph', 'estimated', 'author', 'is_public', 'feedback', 'feedback_counter']
        read_only_fields = ['id', 'created_at', 'author', 'feedback', 'feedback_counter']


class SpeedFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedFeedback
        fields= ['id', 'vote', 'user', 'speed']
        extra_kwargs = {
            'user': {'write_only': True}
            }
        

class SpeedFeedbackCounterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpeedFeedbackCounter
        fields = ['id', 'speed', 'upvotes', 'downvotes']
        read_only_fields = ['id']
        extra_kwargs = {
            'speed': {'write_only': True}
            }


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