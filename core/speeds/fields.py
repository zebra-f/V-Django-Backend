import re

from rest_framework import serializers


class TagsField(serializers.Field):
    initial = [""]
    default_error_messages = {
        "incorrect_data_type": "The data type provided is incorrect; it should be a list.",
        "incorect_data_item_type": "The data's item type provided is incorrect; it should be a string.",
        "string_contains_invalid_character": (
            "Tags must consist of letters (both uppercase and lowercase), numbers, and the following symbols (excluding the next dot): ' - ."
        ),
        "item_too_long": "Item length exceeds the maximum limit. Each string inside the list can have a maximum of 20 characters.",
        "data_too_long": "Maximum limit exceeded. The list can have a maximum of 4 items."
    }

    def to_representation(self, value: list[str]) -> list[str]:
        return value
    
    def to_internal_value(self, data: list[str]) -> list[str]:
        if not isinstance(data, list):
            self.fail("incorrect_data_type", input_type=type(data).__name__)
        if len(data) > 4:
            self.fail('data_too_long')

        tags = []
        for item in data:
            if not isinstance(item, str):
                self.fail("incorect_data_item_type", input_type=type(item).__name__)
            if len(item) > 20:
                self.fail("item_too_long")
            
            pattern = r"^[a-zA-Z0-9'-]+$"
            if not re.fullmatch(pattern, item):
                self.fail("string_contains_invalid_character")

            tags.append(item.lower())
            
        return tags