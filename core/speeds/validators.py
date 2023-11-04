import re

from django.core.validators import MinValueValidator, RegexValidator
from rest_framework import serializers


# Models


class CustomMinValueValidator(MinValueValidator):
    def compare(self, a: int, b: int) -> bool:
        return a <= b


# Serializers/Filters


class TagsValidator:
    def __call__(self, tags: list[str], max_length: int = 4):
        error_messages = {}
        valid = True

        if not isinstance(tags, list):
            error_messages[
                "incorrect_data_type"
            ] = "The data type provided is incorrect; it should be a list."
            valid = False
        if isinstance(tags, list) and len(tags) > max_length:
            error_messages[
                "incorect_data_item_type"
            ] = f"Maximum limit exceeded. The list can have a maximum of {max_length} items."
            valid = False

        if isinstance(tags, list):
            for tag in tags:
                if not isinstance(tag, str):
                    error_messages[
                        "incorect_data_item_type"
                    ] = "The data's item type provided is incorrect; it should be a string."
                    valid = False
                if isinstance(tag, str) and len(tag) > 20:
                    error_messages[
                        "item_too_long"
                    ] = "Tag length exceeds the maximum limit. Each tag can have a maximum of 20 characters."
                    valid = False

                pattern = r"^[a-zA-Z0-9'-]+$"
                if isinstance(tag, str) and not re.fullmatch(pattern, tag):
                    error_messages[
                        "string_contains_invalid_character"
                    ] = "Tags must consist of letters (both uppercase and lowercase), numbers, and the following symbols (excluding the next dot): ' - ."
                    valid = False

        if not valid:
            raise serializers.ValidationError(error_messages)


# Speed.tags (ArrayField)
tags_validator = TagsValidator()

# Speed.name (CharField)
name_validator = RegexValidator(
    regex=r"^[A-Za-z0-9_' -]{2,128}$",
    message=(
        "The name must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols (excluding the next comma): ' - , "
        "the name should be between 2 and 128 characters in length."
    ),
)

# Speed.description (CharField)
description_validator = RegexValidator(
    regex=r"^[A-Za-z0-9,'\".() -]{8,128}$",
    message=(
        "The description must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols: , ' . - \" . ( ) , , "
        "the description should be between 8 and 128 characters in length."
    ),
)

# SpeedBookmark.category (CharField)
category_validator = RegexValidator(
    regex=r"^[A-Za-z0-9' -]{1,32}$",
    message=(
        "The category must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols (excluding the next comma): ' - , "
        "the category should be between 1 and 32 characters in length."
    ),
)

# SpeedReport.detail (TextField)
detail_validator = RegexValidator(
    regex=r"^[A-Za-z0-9'.,,:;?!() -]{1,256}$",
    message=(
        "The category must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols: ' . , , : ; ? ! ( ) - , "
        "the category should be between 1 and 256 characters in length."
    ),
)
