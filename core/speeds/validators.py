import re

from django.core.validators import MinValueValidator, RegexValidator
from django.utils.deconstruct import deconstructible
from rest_framework import serializers


# Models

class CustomMinValueValidator(MinValueValidator):

    def compare(self, a: int, b: int) -> bool:
        return a <= b 
    

# Serializers/Filters

@deconstructible
class TagsValidator:

    def __call__(self, tags: list, max_length: int=4):
        if not isinstance(tags, list):
            raise serializers.ValidationError("The data type provided is incorrect; it should be a list.")
        if len(tags) > max_length:
            raise serializers.ValidationError(f"Maximum limit exceeded. The list can have a maximum of {max_length} items.")

        for tag in tags:
            if not isinstance(tag, str):
                raise serializers.ValidationError("The data's item type provided is incorrect; it should be a string.")
            if len(tag) > 20:
                raise serializers.ValidationError("Tag length exceeds the maximum limit. Each tag inside can have a maximum of 20 characters.")
            
            pattern = r"^[a-zA-Z0-9'-]+$"
            if not re.fullmatch(pattern, tag):
                raise serializers.ValidationError(
                    "Tags must consist of letters (both uppercase and lowercase), numbers, and the following symbols (excluding the next dot): ' - ."
                    )

# Speed.tags (ArrayField)
tags_validator = TagsValidator()

# Speed.name (CharField)
name_validator = RegexValidator(
    regex=r"^[A-Za-z0-9_' -]{2,128}$",
    message=(
        "The name must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols (excluding the next comma): ' - , "
        "the name should be between 2 and 128 characters in length." 
    )
)

# Speed.description (CharField)
description_validator = RegexValidator(
    regex=r"^[A-Za-z0-9,'\".() -]{8,128}$",
    message=(
        "The description must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols: , ' . - \" . ( ) , , "
        "the description should be between 8 and 128 characters in length." 
    )
)

# SpeedBookmark.category (CharField)
category_validator = RegexValidator(
    regex=r"^[A-Za-z0-9' -]{1,32}$",
    message=(
        "The category must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols (excluding the next comma): ' - , "
        "the category should be between 1 and 32 characters in length." 
    )
)

# SpeedReport.detail (TextField)
detail_validator = RegexValidator(
    regex=r"^[A-Za-z0-9'.,,:;?!() -]{1,256}$",
    message=(
        "The category must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols: ' . , , : ; ? ! ( ) - , "
        "the category should be between 1 and 256 characters in length." 
    )
)

