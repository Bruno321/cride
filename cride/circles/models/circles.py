"""circle model"""

# django
from django.db import models

# utilities
from cride.utils.models import CRideModel

class Circle(CRideModel):
    """Circle model

    a circle is a private group
    """

    name = models.CharField('circle name', max_length=140)
    slug_name = models.SlugField(unique=True, max_length=40)

    aabout = models.CharField('circle description', max_length=255)
    picture = models.ImageField(upload_to='circles/pictures', blank=True, null=True)

    memebers = models.ManyToManyField(
        'users.User', 
        through='circles.Membership',
        through_fields=('circle','user')
    )

    # stats
    rides_offered = models.PositiveIntegerField(default=0)
    rides_taken = models.PositiveIntegerField(default=0)

    verified = models.BooleanField(
        'verified circle', 
        default=False,
        help_text='Verified circle are also known as oiffical communities'    
    )

    is_public = models.BooleanField(
        default=True,
        help_text='public circles are lsited in the main page'
    )

    is_limited = models.BooleanField(
        'limited',
        default=False,
        help_text='Limited circles can grow up to a fixed number of members'
    )
    members_limit = models.PositiveIntegerField(
        default=0,
        help_text='if circle is limited this will be the limit'
    )


    def __str__(self):
        """return circle name"""
        return self.name

    class Meta(CRideModel.Meta):
        """Meta class"""

        ordering = ['-rides_taken','-rides_offered']
