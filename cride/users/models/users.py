"""user model"""

# django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# utilities
from cride.utils.models import CRideModel

class User(CRideModel, AbstractUser):
    """User model

    Extend from django abstract user, change the username field to email
    and add some extra fields
    """
    email = models.EmailField(
        'email_address',
        unique=True,
        error_messages={
            'unique': 'A user with that email already exists'
        }
    )

    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +123456789 up to 15 digits'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_client = models.BooleanField(
        'client',
        default=True,
        help_text=(
            'help easily distinguish users and perform queries'
            'clients are the main type of user'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='Set to true when the user have verified its email address'
    )

    def __str__(self):
        """return username"""
        return self.username

    def get_short_name(self):
        """return username"""
        return self.username

