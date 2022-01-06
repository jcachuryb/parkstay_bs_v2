import re
import datetime

#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
from parkstay.models import Booking


CHECKOUT_PATH = re.compile('^/ledger-api')

class BookingTimerMiddleware(object):

    def __init__(self, get_response):
            self.get_response = get_response

    def __call__(self, request):
            return self.pr(request)

    def pr(self, request):
        response= self.get_response(request)
        if 'ps_booking' in request.session:
            try:
                booking = Booking.objects.get(pk=request.session['ps_booking'])
            except:
                # no idea what object is in self.request.session['ps_booking'], ditch it
                del request.session['ps_booking']
                return response
            if booking.booking_type != 3:
                # booking in the session is not a temporary type, ditch it
                del request.session['ps_booking']
            elif timezone.now() > booking.expiry_time:
                # expiry time has been hit, destroy the Booking then ditch it
                #booking.delete()
                del request.session['ps_booking']
            elif CHECKOUT_PATH.match(request.path) and request.method == 'POST':
                # safeguard against e.g. part 1 of the multipart checkout confirmation process passing, then part 2 timing out.
                # on POST boosts remaining time to at least 2 minutes
                booking.expiry_time = max(booking.expiry_time, timezone.now()+datetime.timedelta(minutes=2))
                booking.save()

        # force a redirect if in the checkout
        if ('ps_booking_internal' not in request.COOKIES) and CHECKOUT_PATH.match(request.path):
            if ('ps_booking' not in request.session) and CHECKOUT_PATH.match(request.path):
                url_redirect = reverse('public_make_booking')
                response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a>")
                return response
                #return HttpResponseRedirect(reverse('public_make_booking'))
            else:
                return response
        return response


class CacheControl(object):

    def __init__(self, get_response):
            self.get_response = get_response

    def __call__(self, request):
       response= self.get_response(request)
       if request.path == '/map/':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:19] == '/api/search_suggest':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:12] == '/api/places/':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:20] == '/api/campground_map/':
            response['Cache-Control'] = 'public, max-age=300'
       elif request.path[:17] == '/campground-image':
            response['Cache-Control'] = 'public, max-age=86400'
       elif request.path[:31] == '/api/campsite_availablity_view/':
            response['Cache-Control'] = 'private, no-store'
       elif request.path[:5] == '/api/':
            response['Cache-Control'] = 'private, no-store'
            #response['Cache-Control'] = 'public, max-age=60'
       elif request.path[:8] == '/static/':
            response['Cache-Control'] = 'public, max-age=86400'
       elif request.path[:7] == '/media/':
            response['Cache-Control'] = 'public, max-age=86400'
       else:
            pass
            #response['Cache-Control'] = 'private, no-store'
       return response
    #def patch_response_headers(response, cache_timeout=None):
        #response['Cache-Control'] = 'private, no-store'
        #patch_cache_control(response, max_age=cache_timeout)        
    #def process_response(self, request, response):
        #print ("PATH")
        #print (request.path)
        #response['Cache-Control'] = 'private, no-store'
        #return add_cache_control(response)
