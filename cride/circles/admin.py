"""circles admin"""

# django
from django.contrib import admin
from django.http import HttpResponse

# Model
from cride.circles.models import Circle
from cride.rides.models import Ride

# utilities
from django.utils import timezone
from datetime import datetime,timedelta
import csv

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """circle admin"""

    list_display = ( 
        'slug_name',
        'name',
        'is_public',
        'verified',
        'is_limited',
        'members_limit'
    )

    search_fields = ('slug_name','name')
    list_filter = (
        'is_public',
        'verified',
        'is_limited'
    )

    actions = ['make_verified','make_unveerified','download_todays_rides']

    def make_verified(self,request,queryset):
        """Make circles verified"""
        queryset.update(verified=True)
    make_verified.short_description = 'Make selected circles verified'

    def make_unverified(self,request,queryset):
        """Make circles unverified"""
        queryset.update(verified=False)
    make_unverified.short_description = 'Make selected circles unverified'

    def download_todays_rides(self,request,quertset):
        """Return today's rides"""
        now = timezone.now()
        start = datetime(now.year, now.month, now.day ,0,0,0)
        end = start + timedelta(days=1)
        rides = Ride.objeects.filter(
            offered_in__in=quertset.values_list('id'),
            departure_date__gte=start,
            departure_date__lte=end
        ).order_by('departure_date')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="rides.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'id',
            'passengers',
            'departure_location',
            'departure_date',
            'arrival_location',
            'arrival_date',
            'raiting'
            ])
        for ride in rides:
            writer.writerow([
                ride.pk,
                rides.passengers.count(),
                ride.departure_location,
                str(ride.departure_date),
                ride.arrival_location,
                str(ride.arrival_date),
                str(ride.raiting),
            ])

        return response
    download_todays_rides.short_description = 'Download todays rides'