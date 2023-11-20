from functools import wraps

from rest_framework.exceptions import MethodNotAllowed
from rest_framework import serializers


def check_http_method_allowance(func):
    """
    Checks whether an action is allowed for ViewsSets.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        viewset_instance = args[0]
        request = args[1]

        if not hasattr(viewset_instance, "http_method_names"):
            raise AttributeError(
                "`http_method_names` is not defined for this ViewSet."
            )

        if request.method.lower() not in viewset_instance.http_method_names:
            raise MethodNotAllowed(request.method)

        return func(*args, **kwargs)

    return wrapper


def restrict_field_updates(*fields: str):
    """
    Applies field-level restrictions to the Serializers's update method via the `PATCH` HTTP method
    to prevent certain fields from being updated.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) != 3:
                raise ValueError("Invalid number of keyword arguments.")

            serializer_instance = args[0]
            validated_data = args[2]

            if serializer_instance.context.get("request").method != "PATCH":
                return func(*args, **kwargs)

            error_details = []
            error_flag = False
            for field_name in fields:
                if field_name in validated_data:
                    error_flag = True
                    error_details.append(
                        f"Can't change the {field_name} field."
                    )
            if error_flag:
                raise serializers.ValidationError(error_details)

            return func(*args, **kwargs)

        return wrapper

    return decorator
