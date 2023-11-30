from django.core.management.base import (
    BaseCommand,
    CommandError,
    CommandParser,
)
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = """
    Creates a user with a custom command: `python manage.py createsentineluser <username>`.
    If the `--sentinel` flag is set, a user with a random password will be created.
    If the `--password` and `--email` flags are provided, a user with the specified password and email will be created.
    Examples:
        python3 manage.py createuser --sentinel deleted
        python3 manage.py createuser --email example@example.com --password strongpassword testuser1
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--sentinel",
            action="store_true",
            help="Create a user with a random password. If `--sentinel` flag is set, the `--password` and `--email` flags will be ignored.",
        )
        parser.add_argument(
            "--password", nargs="?", type=str, help="Set the user's password"
        )
        parser.add_argument(
            "--email", nargs="?", type=str, help="Set the user's email"
        )
        parser.add_argument(
            "username", nargs=1, type=str, help="Specify the required username"
        )

    def handle(self, *args, **options):
        sentinel: bool = options["sentinel"]
        username: str = options["username"][0]

        password: str = None
        email: str = None
        if sentinel:
            password = get_random_string(length=40)
            email = f"{username}@v"
        else:
            password = options["password"]
            if not password:
                raise CommandError(
                    "The `--password` flag is either set incorrectly or not set at all. Provide a password or use the `--sentinel` flag to create a sentinel user."
                )
            email = options["email"]
            if not email:
                raise CommandError(
                    "The `--email` flag is either set incorrectly or not set at all. Provide an email or use the `--sentinel` flag to create a sentinel user."
                )

        user, created = get_user_model().objects.get_or_create(
            email=email, username=username
        )
        if created:
            # if sentintel:
            #   user.set_unusable_password()
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"User {username} ({email}) has been created."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"User {username} ({email}) already exists!")
            )
