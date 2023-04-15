from rest_framework import serializers

from .models import Speed, SpeedFeedback, SpeedReport, SpeedBookmark


class SpeedSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Speed
        fields = ['url', 'id', 'name', 'description', 'speed_type', 'tags', 'kmph', 'estimated', 'author', 'is_public', 'feedback']
        read_only_fields = ['id', 'created_at', 'author']


class SpeedFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedFeedback
        fields= ['id', 'vote', 'user', 'speed']
        extra_kwargs = {
            'user': {'write_only': True}}


class SpeedReportSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedFeedback
        fields= ['id', 'report', 'other', 'user', 'speed']
        extra_kwargs = {
            'user': {'write_only': True}}
      

class SpeedBookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model= SpeedFeedback
        fields= ['id', 'category', 'user', 'speed']
        extra_kwargs = {
            'user': {'write_only': True}}