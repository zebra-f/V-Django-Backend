from django.shortcuts import get_object_or_404

from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers


def prevent_unauthorized_create_and_data_reveal(func):
    '''
    Decorate the `create` method of `SpeedFeedbackSerializer` and `SpeedBookmarkSerializer`.
    Prevents authenticated users from creating objects like `SpeedFeedback`, `SpeedBookmark` 
    that could reveal non-public speed data created by another user.
    ("Another user might have modified the 'is_public' attribute of their `Speed` object to `False`, 
    subsequently, an authenticated user with access to that `Speed` object's `id` 
    might try to create `SpeedFeedback` or `SpeedBookmark` objects that could reveal its content.)
    ("The `update` method is protected by a permission.")
    '''

    def wrapper(*args, **kwargs):
        if len(args) != 2:
                raise ValueError("Invalid number of keyword arguments.")
        
        # self
        serializer = args[0]
        validated_data = args[1]
        
        speed = validated_data['speed']
        user = serializer.context['request'].user

        if user != speed.user and speed.is_public == False:
            raise PermissionDenied("You do not have permission to perform this action.")
        
        return func(*args, **kwargs)
    
    return wrapper


def restrict_field_updates(*fields: str):
    """
    Applies field-level restrictions to the update method (that forbids the `PUT` HTTP method) 
    of serializers.ModelSerializer to prevent certain fields from being updated.
    """
    
    def decorator(func):

        def wrapper(*args, **kwargs):
            if len(args) != 3:
                raise ValueError("Invalid number of keyword arguments.")
            
            validated_data = args[2]
            
            for field_name in fields:
                if field_name in validated_data:
                    raise serializers.ValidationError(f"Can't change the {field_name} field.")
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator




