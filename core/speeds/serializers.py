from rest_framework import serializers

from .models import Speed


class SpeedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Speed
        fields = ['id', 'name', 'description', 'speed_type', 'tags', 'kmph', 'estimated', 'is_public']
        read_only_fields = ['id', 'created_at', 'author']