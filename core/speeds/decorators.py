from django.shortcuts import get_object_or_404

from rest_framework.exceptions import PermissionDenied

from .models import Speed


def prevent_unauthorized_create_and_data_reveal(func):
    '''
    Decorate the create method of SpeedFeedbackSerializer, SpeedBookmarkSerializer method.
    Prevents authenticated users from creating objects like SpeedFeedback, SpeedBookmark 
    that could reveal non-public speed data created by another user.
    ("Another user might have modified the 'is_public' attribute of their Speed object to `False`. 
    Subsequently, an authenticated user with access to that Speed object's `id` 
    might try create SpeedFeedback or SpeedBookmark objects that could reveal its content.)
    ("The update method is protected by a permission.")
    '''

    def wrapper(*args, **kwargs):
        self = args[0]
        validated_data = args[1]
        
        speed = validated_data['speed']
        user = self.context['request'].user

        if user != speed.user and speed.is_public == False:
            raise PermissionDenied("You do not have permission to perform this action. b")
        
        return func(*args, **kwargs)
    
    return wrapper