from django.core.validators import MinValueValidator, RegexValidator


# Models

class CustomMinValueValidator(MinValueValidator):

    def compare(self, a: int, b: int) -> bool:
        return a <= b 
    

# Serializers

# Speed.name (CharField)
name_validator = RegexValidator(
    regex=r"^[A-Za-z0-9_'\"-]{2,128}$",
    message=(
        "Name can only contain letters, numbers, and underscores, "
        "name should have length of at least 2 characters."
    )
)

# Speed.description (CharField)
description_validator = RegexValidator(
    regex=r"^[A-Za-z0-9_,'\". ()-]{9,127}$",
    message=(
        "Description should be at least 10 characters long, allowed symbols: \"_,''.-\"."
    )
)

# for Python's built in `re` module
tags_pattern_validator = r"^[a-zA-Z0-9]+$"



    
