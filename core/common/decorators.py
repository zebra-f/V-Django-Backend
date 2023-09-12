from rest_framework.exceptions import MethodNotAllowed
from rest_framework import serializers


def check_http_method_allowance(func):
    '''
    Checks whether an action is allowed for ViewsSets.
    '''

    def wrapper(*args, **kwargs):
        viewset_instance = args[0]
        request = args[1]
        
        if not hasattr(viewset_instance, 'http_method_names'):
            raise AttributeError("`http_method_names` is not defined for this ViewSet.")

        if request.method.lower() not in viewset_instance.http_method_names:
            raise MethodNotAllowed(request.method)
        
        return func(*args, **kwargs)

    return wrapper

def restrict_field_updates(*fields: str):
    '''
    Applies field-level restrictions to the update method (that forbids the `PUT` HTTP method) 
    of serializers.ModelSerializer to prevent certain fields from being updated.
    '''
    
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
