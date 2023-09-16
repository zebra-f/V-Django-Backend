from rest_framework.serializers import Field


class TagsField(Field):
    initial = [""]
    default_error_messages = {
        "incorrect_data_type": "The data type provided is incorrect; it should be a list.",
    }

    def to_representation(self, value: list[str]) -> list[str]:
        return value
    
    def to_internal_value(self, data: list[str]) -> list[str]:
        # ensure that the data is a list before passing it to the validator.
        if not isinstance(data, list):
            self.fail("incorrect_data_type", input_type=type(data).__name__)
        
        # include tags that don't meet `isinstance(tag, str)` condition, the validator will return an appropriate message
        return [tag.lower() if isinstance(tag, str) else tag for tag in data]