from rest_framework import serializers


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
    escape_sequences = ['\\']
    # escape_sequences = ['\\', '\'', '\"', '\n', '\t', '\r', '\b', '\f', '\v', '\ooo', '\xhh']
    
    def to_representation(self, value: str) -> list:
        """ TODO: cahnge to split by a comma! """
        return value.split(' ')
    
    def to_internal_value(self, data: list[str]) -> str:
        if not isinstance(data, list):
            self.fail("incorrect_data_type", input_type=type(data).__name__)
        
        # validation
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
            total_len += len(item)
        if total_len + len(data) - 1 > 128:
            self.fail("input_too_long")
        
        return ','.join(data)