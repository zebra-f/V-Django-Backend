from django.core.validators import MinValueValidator, RegexValidator


# Models

class CustomMinValueValidator(MinValueValidator):

    def compare(self, a: int, b: int) -> bool:
        return a <= b 
    

# Serializers

# Speed.name (CharField)
name_validator = RegexValidator(
    regex=r"^[A-Za-z0-9_'-]{2,128}$",
    message=(
        "The name must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols (excluding the next comma): ' - , "
        "the name should be between 2 and 128 characters in length." 
    )
)

# Speed.description (CharField)
description_validator = RegexValidator(
    regex=r"^[A-Za-z0-9,'\".()-]{8,128}$",
    message=(
        "The description must consist of letters (both uppercase and lowercase), numbers, white spaces, and the following symbols: , ' . - \" . ( ) , "
        "the description should be between 8 and 128 characters in length." 
    )
)
