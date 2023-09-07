import re

from rest_framework import serializers


class TagsField(serializers.Field):
    initial = [""]
    default_error_messages = {
        "incorrect_data_type": "The data type provided is incorrect; it should be a list of strings.",
        "incorect_data_item_type": "The data type provided is incorrect; it should be a list of strings.",
        "string_contains_invalid_character": (
            "Tags must consist of letters (both uppercase and lowercase), numbers, and the following symbols (excluding the next dot): ' - ."
        ),
        "input_too_long": "Excessive or elongated tags. Remove or shorten some tags",
    }
    
    # used for testing
    # invalid_symbols = {
    #     '*', '&', '$', '%', '#', '!', '?', ':', ';', '"', '[', ']', '{', '}', '(', ')', '/', '+', '=', '<', '>',
    #     }
    # escape_sequences = ['\\', '\'', '\"', '\n', '\t', '\r', '\b', '\f', '\v', '\ooo', '\xhh']
    
    def to_representation(self, value: str) -> list:
        """ 
            TODO: cahnge to split by a comma!!!
            TODO: cahnge to split by a comma!!! 
            TODO: cahnge to split by a comma!!! 
        """
        return value.split(' ')
    
    def to_internal_value(self, data: list[str]) -> str:
        if not isinstance(data, list):
            self.fail("incorrect_data_type", input_type=type(data).__name__)
        
        # validation
        total_len = 0
        for item in data:
            if not isinstance(item, str):
                self.fail("incorect_data_item_type", input_type=type(item).__name__)
            
            pattern = r"^[a-zA-Z0-9'-]+$"
            print(item)
            print(re.fullmatch(pattern, item))
            print(re.fullmatch(pattern, 'a'))
            if not re.fullmatch(pattern, item):
                self.fail("string_contains_invalid_character")
            
            total_len += len(item)
        
        #  (len(data) - 1): the number of commas that will be added by the join method
        if total_len + (len(data) - 1) > 128:
            self.fail("input_too_long")
        
        return ','.join(data)