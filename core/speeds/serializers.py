from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField, StringRelatedField

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django import forms

from .models import Speed, SpeedFeedback, SpeedFeedbackCounter, SpeedReport, SpeedBookmark
from core.users.models import User


class TagsField(serializers.Field):
    initial = [""]
    default_error_messages = {
        "incorrect_data_type": "incorrect data type.",
        "incorect_data_item_type": "incorect data item type.",
        "str_contains_invalid_symbol": "A string object in the list contains an invalid symbol.",
        "str_contains_escape_sequnce": "A string object in the list contains an escape sequence.",
        "input_too_long": "Excessive or elongated tags.",
    }
    invalid_symbols = {
        '*', '&', '$', '%', '#', '!', '?', ':', ';', '"', '[', ']', '{', '}', '(', ')', '/', '+', '=', '<', '>',
        }
    escape_sequences = ['\\', '\'', '\"', '\n', '\t', '\r', '\b', '\f', '\v', '\ooo', '\xhh']
    
    def to_representation(self, value: str) -> list:
        """ TODO: cahnge to split by a comma! """
        return value.split(' ')
    
    def to_internal_value(self, data: list[str]) -> str:
        if not isinstance(data, list):
            self.fail("incorrect_data_type", input_type=type(data).__name__)
        
        total_len = 0
        for item in data:
            if not isinstance(item, str):
                self.fail("incorect_data_item_type", input_type=type(item).__name__)
            has_invalid_symbol = any(symbol in item for symbol in self.invalid_symbols)
            if has_invalid_symbol:
                self.fail("str_contains_invalid_symbol")
            has_escape_sequence = any(escape_sequence in item for escape_sequence in self.escape_sequences)
            if has_escape_sequence:
                self.fail("str_contains_escape_sequnce")
            len_ += len(item)
        if total_len + len(data) - 1 > 128:
            self.fail("input_too_long")
        
        return ','.join(data)


class SpeedSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagsField()
    feedback_counter = serializers.StringRelatedField()
    # user_speed_feedback directions:
    # 1 upvote 
    # 0 default, 
    # -1 downvote, 
    # -2 no data for logged in user,
    # -3 not logged in user
    # -4 update method default 
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
            'is_public', 
            'user', 
            'feedback_counter',
            'user_speed_feedback'
            ]
        read_only_fields = ['id', 'created_at', 'user', 'feedback_counter', 'user_speed_feedback']

    def get_user_speed_feedback(self, obj):
        try:
            if obj.user_speed_feedback:
                return obj.user_speed_feedback
            return -2
        except:
            # should never happen, workaround in `create` and `update` method
            return -4
    
    def get_url(self, obj):
        return reverse('myapp:my-model-detail', args=[obj.pk])
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        return representation
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.user_speed_feedback = 1
        return instance
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.user_speed_feedback = -4
        return instance


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
    ''' Utilized by methods in views.py tailored for frontend requests that do not include a Vote pk. '''

    class Meta:
        model = SpeedFeedback
        fields = ['vote', 'speed']

# TODO       

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