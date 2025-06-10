from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from parkstay import utils_cache
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
import requests
import json
import decouple

from datetime import timedelta, date

class Command(BaseCommand):
    help = 'Make available campgrond on release date available after release time.'

    def handle(self, *args, **options):

        try:
            today = timezone.now().date()
            nowtime = timezone.now()
            nowtime_local = nowtime.astimezone()
            crd_obj = models.CampgroundReleaseDate.objects.all().order_by('-id')
            cache.delete('CampgroundReleaseDate')

            for crd in crd_obj:
                if today == crd.booking_open_date:   
                    if crd.campground is not None:                    
                        print ("Checking : " +crd.campground.name)
                        campground_obj = models.Campground.objects.get(id=crd.campground.id)
                        release_time = campground_obj.release_time.strftime("%H:%M:%S")
                        booking_open_date = crd.booking_open_date.strftime('%Y-%m-%d')
                        campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                        nowtime_local_string = nowtime_local.strftime("%Y-%m-%d %H:%M")
                        campground_opentime_string = campground_opentime.strftime("%Y-%m-%d %H:%M")

                        campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                        if nowtime_local_string == campground_opentime_string:
                            for i in range((crd.release_date + timedelta(days=1) - today).days):
                                purge_date = today + timedelta(days=i)
                                if models.AvailabilityCache.objects.filter(campground=crd.campground, date=purge_date).count() > 0:
                                    models.AvailabilityCache.objects.filter(campground=crd.campground, date=purge_date).update(stale=True)
                                else:
                                    models.AvailabilityCache.objects.create(campground=crd.campground, date=purge_date,stale=True)
                            cache.delete('utils_cache.get_campground('+str(c.id)+')')                                                        
                    else:
                        campgrounds = utils_cache.all_campgrounds()
                        for c in campgrounds:     
                            print ("Checking : " +c["campground_name"]) 
                                                  
                            campground_obj = models.Campground.objects.get(id=c["id"])
                            release_time = campground_obj.release_time.strftime("%H:%M:%S")
                            booking_open_date = crd.booking_open_date.strftime('%Y-%m-%d')
                            campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                            nowtime_local_string = nowtime_local.strftime("%Y-%m-%d %H:%M")
                            campground_opentime_string = campground_opentime.strftime("%Y-%m-%d %H:%M")

                            campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                            if nowtime_local_string == campground_opentime_string:
                                for i in range((crd.release_date + timedelta(days=1) - today).days):
                                    purge_date = today + timedelta(days=i)
                                    if models.AvailabilityCache.objects.filter(campground=crd.campground, date=purge_date).count() > 0:
                                        models.AvailabilityCache.objects.filter(campground=crd.campground, date=purge_date).update(stale=True)
                                    else:
                                        models.AvailabilityCache.objects.create(campground=crd.campground, date=purge_date,stale=True)    
                            
                                cache.delete('utils_cache.get_campground('+str(c.id)+')')


                        
                

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
