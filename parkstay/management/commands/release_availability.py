from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from parkstay import utils_cache
from parkstay import datasets
from datetime import datetime
from django.conf import settings
from django.db.models import Q
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
            
            is_running = cache.get('release_availability.py')
            if is_running is None:
                cache.set('release_availability.py', str(nowtime), 14400)
                crd_obj = models.CampgroundReleaseDate.objects.filter(active=True).order_by('-id')
                

                for crd in crd_obj:                
                    if today == crd.booking_open_date or crd.force_rebuild is True:   
                        if crd.campground is not None:                    
                            print ("Checking : " +crd.campground.name)
                            campground_obj = models.Campground.objects.get(id=crd.campground.id)
                            release_time = campground_obj.release_time.strftime("%H:%M:%S")
                            booking_open_date = crd.booking_open_date.strftime('%Y-%m-%d')
                            campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                            nowtime_local_string = nowtime_local.strftime("%Y-%m-%d %H:%M")
                            campground_opentime_string = campground_opentime.strftime("%Y-%m-%d %H:%M")

                            campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                            
                            if nowtime_local_string == campground_opentime_string or crd.force_rebuild is True:  
                                cache.delete('CampgroundReleaseDate')                          
                                params = {}
                                params['status'] = {1: 'available', 2: 'booked', 3: 'closed', 4: 'legacy booking'}
                                params['today'] = date.today()
                                params['start_date'] = today
                                params['campground_id'] = crd.campground.id 
                                params['period_days'] = (crd.release_date + timedelta(days=1) - today).days
                                params['end_date'] = crd.release_date + timedelta(days=1)                            
                                datasets.build_campground_calender(params)
                                datasets.build_campground_daily_calender(params)
                                cache.delete('utils_cache.get_campground('+str(crd.campground.id )+')')     
                                cache.delete('CampgroundReleaseDate')                                                   
                        else:
                            campgrounds = utils_cache.all_campgrounds()
                            campground_changed = False
                            for c in campgrounds:     
                                print ("Checking : " +c["campground_name"]) 
                                                    
                                campground_obj = models.Campground.objects.get(id=c["id"])
                                release_time = campground_obj.release_time.strftime("%H:%M:%S")
                                booking_open_date = crd.booking_open_date.strftime('%Y-%m-%d')
                                campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                                nowtime_local_string = nowtime_local.strftime("%Y-%m-%d %H:%M")
                                campground_opentime_string = campground_opentime.strftime("%Y-%m-%d %H:%M")
                                #campground_opentime_string = campground_opentime.strftime("%Y-%m-%d ")+'21:40'

                                campground_opentime = datetime.strptime(booking_open_date+' '+release_time, '%Y-%m-%d %H:%M:%S')
                                                        
                                if nowtime_local_string == campground_opentime_string or crd.force_rebuild is True:   
                                    cache.delete('CampgroundReleaseDate')                             
                                    # for i in range((crd.release_date + timedelta(days=1) - today).days):
                                    #     purge_date = today + timedelta(days=i)
                                    #     if models.AvailabilityCache.objects.filter(campground=crd.campground, date=purge_date).count() > 0:
                                    #         models.AvailabilityCache.objects.filter(campground=crd.campground, date=purge_date).update(stale=True)
                                    #     else:
                                    #         models.AvailabilityCache.objects.create(campground=crd.campground, date=purge_date,stale=True)                                    
                                    params = {}
                                    params['status'] = {1: 'available', 2: 'booked', 3: 'closed', 4: 'legacy booking'}
                                    params['today'] = date.today()
                                    params['start_date'] = today
                                    params['campground_id'] = c['id']
                                    params['period_days'] = (crd.release_date + timedelta(days=1) - today).days
                                    params['end_date'] = crd.release_date + timedelta(days=1)                            
                                    datasets.build_campground_calender(params)
                                    campground_changed = True

                            if campground_changed is True:    
                                params = {}
                                params['status'] = {1: 'available', 2: 'booked', 3: 'closed', 4: 'legacy booking'}
                                params['today'] = date.today()
                                params['start_date'] = today                            
                                params['period_days'] = (crd.release_date + timedelta(days=1) - today).days
                                params['end_date'] = crd.release_date + timedelta(days=1)                                    
                                datasets.build_campground_daily_calender(params)                                
                                
                                cache.delete('utils_cache.get_campground('+str(c['id'])+')')
                                cache.delete('CampgroundReleaseDate')
                    crd_update = models.CampgroundReleaseDate.objects.get(id=crd.id)
                    crd_update.force_rebuild = False
                    crd_update.save()
                cache.delete('release_availability.py')
            else:
                print ("Process is already running.  Cannot run another process.")


                        
                

        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
            cache.delete('release_availability.py')
