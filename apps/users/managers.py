from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


# Custom User Manager : Create User
class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valid email address"))

    def create_user(
        self,
        username,
        first_name,
        last_name,
        email,
        password=None,
        **extra_fields
    ):
        """
        Creates a new user with the given username, first name, last name, and email.

        Args:
            username (str): The username of the new user.
            first_name (str): The first name of the new user.
            last_name (str): The last name of the new user.
            email (str): The email address of the new user.
            password (str, optional): The password for the new user. Defaults to None.
            **extra_fields: Additional fields to be set for the new user.

        Returns:
            User
        """
        if not username:
            raise ValueError(_("The Username field must be filled"))

        if not first_name:
            raise ValueError(_("The First Name field must be filled"))

        if not last_name:
            raise ValueError(_("The Last Name field must be filled"))

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("Base User Account : You must provide an email address"))

        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault(
            "is_staff", False
        )  # Default value for is_staff is False
        extra_fields.setdefault(
            "is_superuser", False
        )  # Default value for is_superuser is False

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        first_name,
        last_name,
        email,
        password=None,
        **extra_fields
    ):
        """
        Creates a superuser with given parameters.
        Superuser must have is_staff=True, is_superuser=True, is_active=True.
        """
        if not password:
            raise ValueError(_('Superuser must have a password'))

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_('Admin Account : You must provide an email'))

        user = self.create_user(
            username, first_name, last_name, email, password, **extra_fields
        )
        user.save(using=self._db)
        return user
