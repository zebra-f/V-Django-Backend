from functools import wraps

from rest_framework.exceptions import PermissionDenied


def prevent_unauthorized_create_and_data_reveal(func):
    """
    Decorate the `create` method of serializers that save objects with
    `speed` and `user` (Foreign Key) fields.
    Prevents authenticated users from creating objects like `SpeedFeedback`, `SpeedBookmark`
    that could reveal non-public speed data created by another user.
    ("Another user might have modified the 'is_public' attribute of their `Speed` object to `False`,
    subsequently, an authenticated user with access to that `Speed` object's `id`
    might try to create `SpeedFeedback` or `SpeedBookmark` objects that could reveal its content.)
    ("The `update` method is protected by a permission.")
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) != 2:
            raise ValueError("Invalid number of keyword arguments.")

        # self
        serializer_instance = args[0]
        validated_data = args[1]

        speed = validated_data["speed"]
        user = serializer_instance.context["request"].user

        if user != speed.user and speed.is_public == False:
            raise PermissionDenied(
                "You do not have permission to perform this action."
            )

        return func(*args, **kwargs)

    return wrapper
