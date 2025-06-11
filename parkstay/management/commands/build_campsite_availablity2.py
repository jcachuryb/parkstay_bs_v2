from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
#from mooring.models import RegisteredVessels
from parkstay import models
from parkstay import utils_cache
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta, date, timezone as timezone_dt
import requests
import json
import os
from datetime import timedelta
from parkstay import datasets

class Command(BaseCommand):
    help = 'Rebuild Availablity Datasets '

    def add_arguments(self, parser):
        parser.add_argument('-a' '--action', type=str , help='Select an action')
        parser.add_argument('-d' '--date', type=str, help='Enter a date please')
        parser.add_argument('-c' '--campground_id', type=int, help='Please enter campground id')

    def handle(self, *args, **options):
        action = options['a__action']
        date_arg = options['d__date']
        campground_id_arg = options['c__campground_id']

        params = {}
        params['status'] = {1: 'available', 2: 'booked', 3: 'closed', 4: 'legacy booking'}
        params['today'] = date.today()
        if action == 'full':
            params['start_date'] = params['today']
            #period_days = 90
            #params['start_date'] = datetime.strptime('2022-02-17', "%Y-%m-%d").date()
            params['period_days'] = 730
            params['end_date'] = params['start_date'] + timedelta(days=params['period_days'])
        if action == 'date': 
            try:
               params['start_date'] =  datetime.strptime(date_arg, '%Y-%m-%d').date()
               params['period_days'] = 0
               params['end_date'] = params['start_date'] + timedelta(days=params['period_days'])
            except Exception as e:
               print (e)
               print ('Invaild Date format YYYY-MM-DD')
               return

            if campground_id_arg:
                try:
                   params['campground_id'] = int(campground_id_arg) 
                except:
                   print ("Please provide a campground id")
                   return

        if action == 'campground':
             params['start_date'] = params['today']
             params['period_days'] = 730
             params['end_date'] = params['start_date'] + timedelta(days=params['period_days'])

             if campground_id_arg:
                 try:
                     params['campground_id'] = int(campground_id_arg)
                 except:
                     print ("Please provide a campground id")
                     return

        try: 
           if action == 'table':
               availablity_cache = models.AvailabilityCache.objects.filter(stale=True)[:120]
               for a in  availablity_cache:
                   print ("Running for date "+str(a.date)+" for campground "+a.campground.name+" with id "+str(a.campground.id)+"")
                   params['start_date'] = a.date
                   params['campground_id'] = a.campground.id 
                   params['period_days'] = 0
                   params['end_date'] = params['start_date'] + timedelta(days=params['period_days'])
                   datasets.build_campground_calender(params)
                   datasets.build_campground_daily_calender(params)
                   a.stale=False
                   a.save()
           else:
               print ("Start Date")
               print (params['start_date'])
               print ("End Date")
               print (params['end_date'])

               datasets.build_campground_calender(params)
               datasets.build_campground_daily_calender(params)

           #daily_calender = {"campgrounds": {}}
           #for day in range(0, params['period_days']+1):
           #    nextday = params['start_date'] + timedelta(days=day)
           #    nextday_string = nextday.strftime('%Y-%m-%d')
           #    print (nextday_string)

           #    data_file = settings.BASE_DIR+"/datasets/daily/"+str(nextday_string)+"-availablity.json"
           #    #cg = models.Campground.objects.all()
           #    cg = utils_cache.all_campgrounds()
           #    for c in cg:
           #        cg_id = c['id']
           #        cg_calender = {}
           #        campground_data_file = settings.BASE_DIR+"/datasets/"+str(cg_id)+"-campground-availablity.json"
           #        if os.path.isfile(campground_data_file):
           #           f = open(campground_data_file, "r")
           #           datajsonstring = f.read()
           #           cg_calender = json.loads(datajsonstring)
           #           #print (cg_calender)

           #        if c['campground_type'] == 0:
           #            daily_calender['campgrounds'][cg_id] = {}
           #            #campsites = models.Campsite.objects.filter(campground_id=c['id'])
           #            # get closure
           #            #cgbr_qs = models.CampgroundBookingRange.objects.filter(
           #            #    Q(campground_id=cg_id),
           #            #    Q(status=1),
           #            #    Q(range_start__lt=nextday) & (Q(range_end__gt=nextday) | Q(range_end__isnull=True))
           #            #)

           #            #cg_closed = False
           #            #if cgbr_qs.count() > 0:
           #            #    cg_closed = True
           #                
           #            campsites = utils_cache.all_campground_campsites(c['id'])
           #            for cs in campsites:
           #                cs_id = cs['id']
           #                #print ("Read From Data Files")
           #                #print (cg_calender)
           #                #print (cg_id)
           #                #print (cs_id)
           #                #print (cg_calender['campsites'][str(cs_id)])
           #                #print (cg_calender['campsites'][str(cs_id)][nextday_string])
           #                avail_status = params['status'][1]
           #                if 'campsites' in cg_calender:
           #                    if str(cs_id) in cg_calender['campsites']:
           #                        if nextday_string in cg_calender['campsites'][str(cs_id)]:
           #                             avail_status = cg_calender['campsites'][str(cs_id)][nextday_string]

           #                if cs_id not in daily_calender['campgrounds'][cg_id]:
           #                    daily_calender['campgrounds'][cg_id][cs_id] = {}

           #                daily_calender['campgrounds'][cg_id][cs_id][nextday_string] = avail_status
           #                #csbr_qs = models.CampsiteBookingRange.objects.filter(
           #                #    Q(campsite_id=cs['id']),
           #                #    Q(status=1),
           #                #    Q(range_start__lt=nextday) & (Q(range_end__gt=nextday) | Q(range_end__isnull=True))
           #                #)

           #                #cs_closed = False
           #                #if csbr_qs.count() > 0:
           #                #      cs_closed = True

           #                #csbooking = models.CampsiteBooking.objects.filter(booking__is_canceled=False, campsite_id=cs['id'], date=nextday)
           #                #cs_booked = False
           #                #if csbooking.count() > 0:
           #                #     cs_booked = True


           #                #lcsbooking = models.CampsiteBookingLegacy.objects.filter(is_cancelled=False, campsite_id=cs['id'], date=nextday)
           #                #lcs_booked = False
           #                #if lcsbooking.count() > 0:
           #                #     lcs_booked = True
           #                #     
           #                ## dont forget legecy bookings

           #                #if cs_id not in daily_calender['campgrounds'][cg_id]:
           #                #    daily_calender['campgrounds'][cg_id][cs_id] = {}
           #                #if cg_closed is True:
           #                #    daily_calender['campgrounds'][cg_id][cs_id][nextday_string] = params['status'][3] 
           #                #elif cs_closed is True:
           #                #    daily_calender['campgrounds'][cg_id][cs_id][nextday_string] = params['status'][3]
           #                #elif cs_booked is True:
           #                #    daily_calender['campgrounds'][cg_id][cs_id][nextday_string] = params['status'][2]
           #                #elif lcs_booked is True:
           #                #    daily_calender['campgrounds'][cg_id][cs_id][nextday_string] = params['status'][4]
           #                #else:
           #                #    daily_calender['campgrounds'][cg_id][cs_id][nextday_string] = params['status'][1]

           #    f = open(data_file, "w")
           #    f.write(json.dumps(daily_calender, indent=4))
           #    f.close() 

           print ("Completed")
        except Exception as e:
            print (e)
            #Send fail email
            content = "Error message: {}".format(e)
