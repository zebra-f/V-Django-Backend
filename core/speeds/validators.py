from django.core.validators import MinValueValidator


class CustomMinValueValidator(MinValueValidator):

    def compare(self, a: int, b: int) -> bool:
        return a <= b