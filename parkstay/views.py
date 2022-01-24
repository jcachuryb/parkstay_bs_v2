import logging
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from ledger_api_client.utils import create_basket_session, create_checkout_session, place_order_submission, use_existing_basket, use_existing_basket_from_invoice, process_api_refund
from django import forms
#from ledger.basket.models import Basket
from parkstay.forms import LoginForm, MakeBookingsForm, AnonymousMakeBookingsForm, VehicleInfoFormset
from parkstay.exceptions import BindBookingException
from django.core.exceptions import ValidationError
from parkstay.models import (Campground,
                                CampgroundNotice,
                                CampsiteBooking,
                                Campsite,
                                CampsiteRate,
                                Booking,
                                BookingInvoice,
                                PromoArea,
                                Park,
                                Feature,
                                Region,
                                CampsiteClass,
                                Booking,
                                BookingVehicleRego,
                                CampsiteRate,
                                ParkEntryRate
                                )
from parkstay import models as parkstay_models
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.ledger_models import Address
from ledger_api_client.ledger_models import EmailIdentity
from ledger_api_client.ledger_models import Invoice
from ledger_api_client.ledger_models import Basket
#from ledger.accounts.models import EmailUser, Address, EmailIdentity
#from ledger.payments.models import Invoice
from django_ical.views import ICalFeed
from datetime import datetime, timedelta
from decimal import *
from django.db.models import Max
from django.core.cache import cache

from parkstay.helpers import is_officer
from parkstay import utils
from parkstay import booking_availability
from parkstay import context_processors
import json
import hashlib

logger = logging.getLogger('booking_checkout')

class CampsiteBookingSelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'


class CampsiteAvailabilitySelector(TemplateView):
    template_name = 'ps/campsite_booking_selector.html'

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id
        context = {}
        ratis_id = request.GET.get('parkstay_site_id', None)
        if ratis_id:
            cg = Campground.objects.filter(ratis_id=ratis_id)
            if cg.exists():
                context['ground_id'] = cg.first().id
        return render(request, self.template_name, context)

class AvailabilityAdmin(TemplateView):
    template_name = 'ps/availability_admin.html'

class CampgroundFeed(ICalFeed):
    timezone = 'UTC+8'

    # permissions check
    def __call__(self, request, *args, **kwargs):
        if not is_officer(self.request.user):
            raise Http403('Insufficient permissions')

        return super(ICalFeed, self).__call__(request, *args, **kwargs)

    def get_object(self, request, ground_id):
        # FIXME: add authentication parameter check
        return Campground.objects.get(pk=ground_id)

    def title(self, obj):
        return 'Bookings for {}'.format(obj.name)

    def items(self, obj):
        now = datetime.utcnow()
        low_bound = now - timedelta(days=60)
        up_bound = now + timedelta(days=90)
        return Booking.objects.filter(campground=obj, arrival__gte=low_bound, departure__lt=up_bound).order_by('-arrival','campground__name')

    def item_link(self, item):
        return 'http://www.geocities.com/replacethiswithalinktotheadmin'

    def item_title(self, item):
        return item.legacy_name

    def item_start_datetime(self, item):
        return item.arrival

    def item_end_datetime(self, item):
        return item.departure

    def item_location(self, item):
        return '{} - {}'.format(item.campground.name, ', '.join([
            x[0] for x in item.campsites.values_list('campsite__name').distinct()
        ] ))


class TestView(TemplateView):
    template_name = 'ps/test.html'

    def get(self, request, *args, **kwargs):
        context = {}
        context = {'LEDGER_UI_URL' : settings.LEDGER_UI_URL}
        response = render(request, self.template_name, context)
        return response


class TestViewAuth(UserPassesTestMixin, TemplateView):
    template_name = 'ps/test.html'

    def test_func(self):
        return is_officer(self.request.user)

    def get(self, request, *args, **kwargs):
        context = {}
        context = {'LEDGER_UI_URL' : settings.LEDGER_UI_URL}
        response = render(request, self.template_name, context)
        return response


class DashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'ps/dash/dash_tables_campgrounds.html'

    def test_func(self):
        return is_officer(self.request.user)

    def get(self, request, *args, **kwargs):
        # if page is called with ratis_id, inject the ground_id
        context = {}
        context = {'LEDGER_UI_URL' : settings.LEDGER_UI_URL}
        response = render(request, self.template_name, context)
        response.delete_cookie(settings.OSCAR_BASKET_COOKIE_OPEN)
        return response

def abort_booking_view(request, *args, **kwargs):
    try:
        change = bool(request.GET.get('change', False))
        change_ratis = request.GET.get('change_ratis', None)
        change_id = request.GET.get('change_id', None)
        change_to = None
        booking = utils.get_session_booking(request.session)
        arrival = booking.arrival
        departure = booking.departure

        if change_ratis:
            try:
                c_id = Campground.objects.get(ratis_id=change_ratis).id
            except:
                c_id = booking.campground.id
        elif change_id:
            try:
                c_id = Campground.objects.get(id=change_id).id
            except:
                c_id = booking.campground.id
        else:
            c_id = booking.campground.id

        # only ever delete a booking object if it's marked as temporary
        if booking.booking_type == 3:
            booking.delete()
        utils.delete_session_booking(request.session)
        if change:
            # Redirect to the availability screen
            arrival_date = booking.arrival.strftime("%Y/%m/%d")
            departure_date = booking.departure.strftime("%Y/%m/%d")

            old_booking_data_url = ""
            booking_data_url = "?site_id="+str(booking.campground.id)+"&arrival="+arrival_date+"&departure="+departure_date+"&num_adult="+str(booking.details.get('num_adult',0))+"&num_concession="+str(booking.details['num_concession'])+"&num_children="+str(booking.details['num_child'])+"&num_infants="+str(booking.details['num_infant'])+"&num_vehicle="+str(booking.details['num_vehicle'])+"&num_campervan="+str(booking.details['num_campervan'])+"&num_motorcycle="+str(booking.details['num_motorcycle'])+"&num_trailer="+str(booking.details['num_trailer'])+"&num_caravan="+str(booking.details.get('num_caravan',0))+"&gear_type=all"

            if booking.old_booking is not None:
                if int(booking.old_booking) > 0:
                    old_booking_data_url = "&change_booking_id="+str(booking.old_booking)
            return redirect(reverse('search_availablity_campground') + booking_data_url + old_booking_data_url)
            #return redirect(reverse('search_availablity_campground') + '?site_id={}&arrival={}&departure={}'.format(c_id, arrival.strftime('%Y/%m/%d'), departure.strftime('%Y/%m/%d')))
        else:
            # Redirect to explore parks
            return redirect(settings.EXPLORE_PARKS_URL)
    except Exception as e:
        print ("EXCEPTION in booking abort")
        print (e)
        pass
    return redirect('public_make_booking')


class MakeBookingsView(TemplateView):
    template_name = 'ps/booking/make_booking.html'

    def render_page(self, request, booking, form, vehicles, show_errors=False):
        # for now, we can assume that there's only one campsite per booking.
        # later on we might need to amend that

        context = {'cg': {'campground': {},'campground_notices': []}}
        #campground_id = request.GET.get('site_id', None)
        #num_adult = request.GET.get('num_adult', 0)
        #num_concession= request.GET.get('num_concession', 0)
        #num_children= request.GET.get('num_children', 0)
        #num_infants= request.GET.get('num_infants', 0)
        context['allow_price_override'] = False
        context['booking_without_payment'] = False
        if request.user.is_authenticated: 
            if request.user.is_staff is True:
                 if parkstay_models.ParkstayPermission.objects.filter(email=request.user.email,permission_group=1).count() > 0:
                      context['allow_price_override'] = True
                 if parkstay_models.ParkstayPermission.objects.filter(email=request.user.email,permission_group=4).count() > 0:
                      context['booking_without_payment'] = True




        if booking:
            context['cg']['campground_id'] = booking.campground.id
            context['cg']['num_adult'] = booking.details['num_adult']
            context['cg']['num_concession'] = booking.details['num_concession']
            context['cg']['num_children'] = booking.details['num_child']
            context['cg']['num_infants'] = booking.details['num_infant']

            delta = booking.departure - booking.arrival 

            context['cg']['nights'] = delta.days 

            context = booking_availability.campground_booking_information(context, booking.campground.id)

        #campground_query = Campground.objects.get(id=context['cg']['campground_id'])
        #max_people = Campsite.objects.filter(campground_id=context['cg']['campground_id']).aggregate(Max('max_people'))["max_people__max"]
        #max_vehicles = Campsite.objects.filter(campground_id=context['cg']['campground_id']).aggregate(Max('max_vehicles'))["max_vehicles__max"]

        #context['cg']['campground']['id'] = campground_query.id
        #context['cg']['campground']['name'] = campground_query.name
        #context['cg']['campground']['largest_camper'] = max_people
        #context['cg']['campground']['largest_vehicle'] = max_vehicles
        #context['cg']['campground']['park'] = {}
        #context['cg']['campground']['park']['id'] = campground_query.park.id
        #context['cg']['campground']['park']['alert_count'] = campground_query.park.alert_count
        #context['cg']['campground']['park']['alert_url'] = settings.ALERT_URL

        #context['cg']['campground_notices_red'] = 0
        #context['cg']['campground_notices_orange'] = 0
        #context['cg']['campground_notices_blue'] = 0

        expiry = booking.expiry_time.isoformat() if booking else ''
        timer = (booking.expiry_time-timezone.now()).seconds if booking else -1
        campsite = booking.campsites.all()[0].campsite if booking else None
        entry_fees = ParkEntryRate.objects.filter(Q(period_start__lte = booking.arrival), Q(period_end__gte=booking.arrival)|Q(period_end__isnull=True)).order_by('-period_start').first() if (booking and campsite.campground.park.entry_fee_required) else None

        pricing = {
            'adult': Decimal('0.00'),
            'concession': Decimal('0.00'),
            'child': Decimal('0.00'),
            'infant': Decimal('0.00'),
            'vehicle': entry_fees.vehicle if entry_fees else Decimal('0.00'),
            'vehicle_conc': entry_fees.concession if entry_fees else Decimal('0.00'),
            'motorcycle': entry_fees.motorbike if entry_fees else Decimal('0.00'),
            'campervan' : entry_fees.campervan if entry_fees else Decimal('0.00'),
            'trailer': entry_fees.trailer if entry_fees else Decimal('0.00')
        }

        if booking:
            pricing_list = utils.get_visit_rates(Campsite.objects.filter(pk=campsite.pk), booking.arrival, booking.departure)[campsite.pk]
            pricing['adult'] = sum([x['adult'] for x in pricing_list.values()])
            pricing['concession'] = sum([x['concession'] for x in pricing_list.values()])
            pricing['child'] = sum([x['child'] for x in pricing_list.values()])
            pricing['infant'] = sum([x['infant'] for x in pricing_list.values()])

        override_reasons = []
        if context['allow_price_override'] is True: 
             override_reasons = parkstay_models.DiscountReason.objects.all()
       
        return render(request, self.template_name, {
            'form': form, 
            'vehicles': vehicles,
            'booking': booking,
            'campsite': campsite,
            'expiry': expiry,
            'timer': timer,
            'pricing': pricing,
            'show_errors': show_errors,
            'cg' : context['cg'],
            'allow_price_override' : context['allow_price_override'],
            'booking_without_payment' : context['booking_without_payment'],
            'request': request,
            'override_reasons' : override_reasons
        })

    def get(self, request, *args, **kwargs):
        # TODO: find campsites related to campground
        booking = None
        form = None
        if 'ps_booking' in request.session:
            if Booking.objects.filter(pk=request.session['ps_booking']).count() > 0:
                booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
                print ("CURRENT")
                print (booking.id)

        #booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
        form_context = {
            'num_adult': booking.details.get('num_adult', 0) if booking else 0,
            'num_concession': booking.details.get('num_concession', 0) if booking else 0,
            'num_child': booking.details.get('num_child', 0) if booking else 0,
            'num_infant': booking.details.get('num_infant', 0) if booking else 0,
            'country': 'AU',
        }

        #form = AnonymousMakeBookingsForm(form_context)
        if request.user.is_authenticated:
            if request.user.is_staff:
                form = AnonymousMakeBookingsForm(form_context)
            else:
                form_context['first_name'] = request.user.first_name
                form_context['last_name'] = request.user.last_name
                form_context['phone'] = request.user.phone_number
                form = MakeBookingsForm(form_context)

        vehicles = VehicleInfoFormset()
        return self.render_page(request, booking, form, vehicles)


    def post(self, request, *args, **kwargs):

        booking = None
        if 'ps_booking' in request.session:
            if Booking.objects.filter(pk=request.session['ps_booking']).count() > 0:
                booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None
            else:
                del request.session['ps_booking']

        #booking = Booking.objects.get(pk=request.session['ps_booking']) if 'ps_booking' in request.session else None

        if request.user.is_authenticated:
            if request.user.is_staff:
        #if request.user.is_anonymous:
                form = AnonymousMakeBookingsForm(request.POST)
            else:
                form = MakeBookingsForm(request.POST)
        else:
            form = MakeBookingsForm(request.POST)
        
        vehicles = VehicleInfoFormset(request.POST)   
        
        # re-render the page if there's no booking in the session
        if not booking:
            return self.render_page(request, booking, form, vehicles)
    
        # re-render the page if the form doesn't validate
        if (not form.is_valid()) or (not vehicles.is_valid()):
            return self.render_page(request, booking, form, vehicles, show_errors=True)


        bvr = BookingVehicleRego.objects.filter(booking=booking)
        vehicle_errors = False
        for v in bvr:
            if len(v.rego) == 0 and v.hire_car is False:
                 vehicle_errors = True
                 form.add_error(None, 'Vehicle is missing rego.')

        if vehicle_errors is True:
            return self.render_page(request, booking, form, vehicles, show_errors=True)

        # update the booking object with information from the form
        if not booking.details:
            booking.details = {}

        booking.details['first_name'] = form.cleaned_data.get('first_name')
        booking.details['last_name'] = form.cleaned_data.get('last_name')
        booking.details['phone'] = form.cleaned_data.get('phone')
        booking.details['country'] = form.cleaned_data.get('country').iso_3166_1_a2
        booking.details['postcode'] = form.cleaned_data.get('postcode')
        booking.details['num_adult'] = form.cleaned_data.get('num_adult')
        booking.details['num_concession'] = form.cleaned_data.get('num_concession')
        booking.details['num_child'] = form.cleaned_data.get('num_child')
        booking.details['num_infant'] = form.cleaned_data.get('num_infant')
        booking.details['toc'] = request.POST.get('toc',False)
        booking.details['outsideregion'] = request.POST.get('outsideregion', False)
        booking.details['trav_res'] = request.POST.get('trav_res', False)
        booking.details['no_payment'] = request.POST.get('no_payment', False)

        # update vehicle registrations from form
        VEHICLE_CHOICES = {'0': 'vehicle', '1': 'concession', '2': 'motorbike', '3': 'campervan', '4': 'trailer', '5': 'caravan'}



        #for vehicle in vehicles:
        #     rego = vehicle.cleaned_data.get('vehicle_rego')
        #     type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')]
        #     entry_fee=vehicle.cleaned_data.get('entry_fee').exists()
             

        #BookingVehicleRego.objects.filter(booking=booking).delete()
        #for vehicle in vehicles:
        #    obj_check = BookingVehicleRego.objects.filter(booking = booking,
        #    rego = vehicle.cleaned_data.get('vehicle_rego'),
        #    type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')],
        #    entry_fee=vehicle.cleaned_data.get('entry_fee')).exists()

        #    if(not obj_check):
        #        BookingVehicleRego.objects.create(
        #            booking=booking, 
        #            rego=vehicle.cleaned_data.get('vehicle_rego'), 
        #            type=VEHICLE_CHOICES[vehicle.cleaned_data.get('vehicle_type')],
        #            entry_fee=vehicle.cleaned_data.get('entry_fee')
        #        )
        #    else:
        #        form.add_error(None, 'Duplicate regos not permitted.If unknown add number, e.g. Hire1, Hire2.')
        #        return self.render_page(request, booking, form, vehicles, show_errors=True)

        # Check if number of people is exceeded in any of the campsites
        max_people_accumulated_campsites = 0
        min_people_accumulated_campsites = 0
        appended_already = []
        for c in booking.campsites.all():
                 if c.campsite.id not in appended_already: 
                    max_people_accumulated_campsites = max_people_accumulated_campsites + c.campsite.max_people
                    min_people_accumulated_campsites = min_people_accumulated_campsites + c.campsite.min_people
                    # stop site duplication
                    appended_already.append(c.campsite.id)


        if booking.num_guests > max_people_accumulated_campsites:
               form.add_error(None, 'Number of people exceeded for the current camp site.')
               return self.render_page(request, booking, form, vehicles, show_errors=True)

        # Prevent booking if less than min people 
        if booking.num_guests < min_people_accumulated_campsites:
               form.add_error('Number of people is less than the minimum allowed for the current campsite.')
               return self.render_page(request, booking, form, vehicles, show_errors=True)

        # generate final pricing
        try:
            #lines = utils.price_or_lineitems(request, booking, booking.campsite_id_list)

            lines = utils.price_or_lineitemsv2(request, booking)
            
        except Exception as e:
            print (e)
            form.add_error(None, '{} Please contact Parks and Visitors services with this error message, the campground/campsite and the time of the request.'.format(str(e)))
            return self.render_page(request, booking, form, vehicles, show_errors=True)
            
        #print(lines)
        #total = sum([Decimal(p['price_incl_tax'])*p['quantity'] for p in lines])
        total = sum([Decimal(p['price_incl_tax']) for p in lines])
        # get the customer object
        #if request.user.is_anonymous:
        if request.user.is_authenticated:
            if request.user.is_staff:
                  # searching on EmailIdentity looks for both EmailUser and Profile objects with the email entered by user
                  customer_qs = EmailIdentity.objects.filter(email__iexact=form.cleaned_data.get('email'))
                  if customer_qs:
                      customer = customer_qs.first().user
                  else:
                      customer = EmailUser.objects.create(
                              email=form.cleaned_data.get('email').lower(),
                              first_name=form.cleaned_data.get('first_name'),
                              last_name=form.cleaned_data.get('last_name'),
                              phone_number=form.cleaned_data.get('phone'),
                              mobile_number=form.cleaned_data.get('phone')
                      )
                      customer = EmailUser.objects.filter(email__iexact=form.cleaned_data.get('email').lower())[0] 
                      Address.objects.create(line1='address', user=customer, postcode=form.cleaned_data.get('postcode'), country=form.cleaned_data.get('country').iso_3166_1_a2)
            else:
                  customer = request.user
        
        # FIXME: get feedback on whether to overwrite personal info if the EmailUser
        # already exists
 
        # finalise the booking object
        booking.customer = customer
        booking.cost_total = total
        booking.save()

        # generate invoice
        reservation = u"Reservation for {} confirmation {}".format(u'{} {}'.format(booking.customer.first_name, booking.customer.last_name), booking.id)
        
        logger.info(u'{} built booking {} and handing over to payment gateway'.format(u'User {} with id {}'.format(booking.customer.get_full_name(),booking.customer.id) if booking.customer else u'An anonymous user',booking.id))

        result = utils.checkout(request, booking, lines, invoice_text=reservation)
        return result

class PeakPeriodGroup(TemplateView):
    template_name = 'ps/dash/peak_periods.html'

    def get(self, request, *args, **kwargs):
        #peakgroups = parkstay_models.PeakGroup.objects.all()
        #context = {'peakgroups': peakgroups}
        context = {}
        response = render(request, self.template_name, context)
        return response

class BookingPolicy(TemplateView):
    template_name = 'ps/dash/booking_policy.html'

    def get(self, request, *args, **kwargs):
        #booking_id = kwargs['booking_id']
        #parkstay_models.PeakGroup.objects.create(name='Test 2')
        context = {}
        response = render(request, self.template_name, context)
        return response

class ChangeBookingView(TemplateView):
    #template_name = 'ps/booking/change_booking.html'
     def get(self, request, *args, **kwargs):
         booking_id = kwargs['booking_id']
         booking = None
         booking_data = Booking.objects.filter(id=booking_id, is_canceled=False)
         if booking_data.count() > 0:
             booking = booking_data[0]
             if booking.customer.id == request.user.id or request.user.is_staff is True:
                  arrival_date = booking.arrival.strftime("%Y/%m/%d")
                  departure_date = booking.departure.strftime("%Y/%m/%d")
                     
                  response = HttpResponse("<script>window.location='/search-availablity/campground/?site_id="+str(booking.campground.id)+"&arrival="+arrival_date+"&departure="+departure_date+"&num_adult="+str(booking.details.get('num_adult',0))+"&num_concession="+str(booking.details['num_concession'])+"&num_children="+str(booking.details['num_child'])+"&num_infants="+str(booking.details['num_infant'])+"&num_vehicle="+str(booking.details['num_vehicle'])+"&num_campervan="+str(booking.details['num_campervan'])+"&num_motorcycle="+str(booking.details['num_motorcycle'])+"&num_trailer="+str(booking.details['num_trailer'])+"&num_caravan="+str(booking.details.get('num_caravan',0))+"&gear_type=all&change_booking_id="+str(booking.id)+"';</script>", content_type='text/html')
                  return response
         context = {}
         self.template_name = 'ps/search_availabilty_campground_cancel_booking_error.html'
         return render(request, self.template_name, context)



class CancelBookingView(TemplateView):
    template_name = 'ps/booking/cancel_booking.html'

    def get(self, request, *args, **kwargs):
        booking_id = kwargs['booking_id']

        #today = timezone.now().date()
        today = datetime.now().date()

        only_cancel_booking = False
        cancel_past_booking = False
        cancel_past_booking_override = request.GET.get('override_cancellation','false')
        cancel_past_booking_override_access = False

        if request.user.is_authenticated:
            if request.user.is_staff is True:
                if parkstay_models.ParkstayPermission.objects.filter(email=request.user.email,permission_group=2).count() > 0:
                       only_cancel_booking = True

        if request.user.is_authenticated:
            if request.user.is_staff is True:
                if parkstay_models.ParkstayPermission.objects.filter(email=request.user.email,permission_group=3).count() > 0:
                       cancel_past_booking = True

        if cancel_past_booking_override == 'true' and cancel_past_booking == True:
               cancel_past_booking_override_access = True

        booking = None
        booking_data = Booking.objects.filter(id=booking_id, is_canceled=False)
        if booking_data.count() > 0:
            booking = booking_data[0]
            if booking.customer.id == request.user.id or request.user.is_staff is True:
                    if booking.arrival > today or cancel_past_booking_override_access == True:
                             booking_totals = utils.booking_total_to_refund(booking)
                             totalbooking = booking_totals['refund_total']
                             campsitebooking = booking_totals['campsitebooking']
                             cancellation_data = booking_totals['cancellation_data']

                             #campsitebooking = CampsiteBooking.objects.filter(booking_id=booking_id)
                             #totalbooking = Decimal('0.00')

                             #cancellation_data = utils.booking_cancellation_fees(booking)  
                             #for cb in campsitebooking:
                             #     totalbooking = totalbooking + cb.amount_adult + cb.amount_infant + cb.amount_child + cb.amount_concession

                             #additional_booking = parkstay_models.AdditionalBooking.objects.filter(booking=booking, identifier='vehicles')
                             #for ab in additional_booking:
                             #     totalbooking = totalbooking + ab.amount

                             ##totalbooking = totalbooking - Decimal(cancellation_data['cancellation_fee'])

                             context = {
                                 'booking': booking,
                                 'campsitebooking': campsitebooking,
                                 'cancellation_data' : cancellation_data,
                                 'totalbooking' : str(totalbooking),
                                 'only_cancel_booking' : only_cancel_booking,
                                 'cancel_past_booking_override_access' : cancel_past_booking_override_access
                                 }

                             response = render(request, self.template_name, context)
                             return response
        context = {'cancel_past_booking': cancel_past_booking, 'booking': booking , 'today': today}

        self.template_name = 'ps/search_availabilty_campground_cancel_booking_error.html'
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        booking_id = kwargs['booking_id']
        booking = Booking.objects.get(id=int(booking_id))
        only_cancel_booking = False 

        if request.user.is_authenticated:
            if request.user.is_staff is True:
                if parkstay_models.ParkstayPermission.objects.filter(email=request.user.email,permission_group=2).count() > 0:
                       ocb = request.POST.get('only_cancel_booking', False)
                       if ocb == 'true':
                           only_cancel_booking = True

        if booking.customer.id == request.user.id or request.user.is_staff is True:

               if only_cancel_booking is True:
                    jsondata = {}
                    booking.is_canceled = True
                    booking.canceled_by = request.user
                    booking.cancelation_time = timezone.now()
                    booking.cancellation_reason = "Booking Cancelled Online"
                    booking.save()
                    jsondata['message'] = 'success'
                    jsondata['status'] = 200
                    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
                    return response
               else:
                    # > remove any sessions
                    if request.session:
                       if 'ps_booking' in request.session:
                           booking_session = utils.get_session_booking(request.session)
                           if booking_session.booking_type == 3:
                              booking_session.delete()
                           utils.delete_session_booking(request.session)
                    # < remove any sessions

                    # Attemping to refund
                    booking_totals = utils.booking_total_to_refund(booking)
                    totalbooking = booking_totals['refund_total']
                    campsitebooking = booking_totals['campsitebooking']
                    cancellation_data = booking_totals['cancellation_data']

                    ## PLACE IN UTILS
                    lines = []
                    lines = utils.price_or_lineitemsv2old_booking(request,booking, lines)
                    #cancellation_data =  utils.booking_change_fees(booking)
                    cancellation_data = utils.booking_cancellation_fees(booking)
                    
                    
                    lines.append({'ledger_description':'Booking Cancellation Fee',"quantity":1,"price_incl_tax":str(cancellation_data['cancellation_fee']),"oracle_code":booking.campsite_oracle_code, 'line_status': 1})
           
                    basket_params = {
                        'products': lines,
                        'vouchers': [],
                        'system': settings.PS_PAYMENT_SYSTEM_ID,
                        'custom_basket': True,
                        'booking_reference': settings.BOOKING_PREFIX+'-'+str(booking.id),
                        'booking_reference_link': settings.BOOKING_PREFIX+'-'+str(booking.id)

                    }
                    checkouthash =  hashlib.sha256(str(booking.pk).encode('utf-8')).hexdigest()
                    request.session['checkouthash'] = checkouthash

                    return_url = request.build_absolute_uri()+"/booking/cancellation-success/?checkouthash="+checkouthash
                    return_preload_url = request.build_absolute_uri()+"/booking/return-cancelled/"
                    jsondata = process_api_refund(request, basket_params, booking.customer.id, return_url, return_preload_url)
                    if jsondata['message'] == 'success':
                        booking.is_canceled = True
                        booking.canceled_by = request.user
                        booking.cancelation_time = timezone.now()
                        booking.cancellation_reason = "Booking Cancelled Online"
                        booking.save()
                    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
                    return response

class BookingSuccessView(TemplateView):
    template_name = 'ps/booking/success.html'

    def get(self, request, *args, **kwargs):
        checkouthash = request.GET.get('checkouthash','')
        try:
            basket = None
            session_checkouthash = request.session.get('checkouthash')
            if session_checkouthash == checkouthash:
                pass
            else:
                context = {}
                self.template_name = 'ps/booking/success-error.html'
                response = render(request, self.template_name, context)
                return response
            booking = utils.get_session_booking(request.session)

            #if self.request.user.is_authenticated:
            #    basket = Basket.objects.filter(status='Submitted', owner=request.user).order_by('-id')[:1]
            #else:
            basket = Basket.objects.filter(status='Submitted', booking_reference=settings.BOOKING_PREFIX+'-'+str(booking.id)).order_by('-id')[:1]
            if basket.count() > 0:
                pass
            else:
                raise ValidationError('Error unable to find basket') 

            try:
                utils.bind_booking(booking, basket)
                utils.delete_session_booking(request.session)
                request.session['ps_last_booking'] = booking.id

            except BindBookingException:
                return redirect('public_make_booking')
            
        except Exception as e:
            print ("SUCCESS EXCEPTION")
            print (e)
            if ('ps_last_booking' in request.session) and Booking.objects.filter(id=request.session['ps_last_booking']).exists():
                booking = Booking.objects.get(id=request.session['ps_last_booking'])
            else:
                return redirect('home')

        context = {
            'booking': booking
        }
        print("BookingSuccessView - get 6.0.1", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        response = render(request, self.template_name, context)
        response.delete_cookie(settings.OSCAR_BASKET_COOKIE_OPEN)
        return response


class MyBookingsView(LoginRequiredMixin, TemplateView):
    template_name = 'ps/booking/my_bookings.html'

    def get(self, request, *args, **kwargs):
        
        bookings = Booking.objects.filter(customer=request.user, booking_type__in=(0, 1), )
        today = timezone.now().date()
        action = request.GET.get('action')

        context = {}
        if action == '' or action is None or action == 'upcoming':

             context = {
                 'action': 'upcoming',
                 'current_bookings': self.booking_filter_upcoming(request.user), #bookings.filter(departure__gte=today).order_by('arrival'),
                 'past_bookings': [],
                 'today' : today
             }

        if action == 'past_bookings':
             context = {
                'action': 'past_bookings',
                'current_bookings': [],
                'past_bookings': self.booking_filter_past_bookings(request.user), #bookings.filter(departure__lt=today).order_by('-arrival'),
                'today' : today
             }
        return render(request, self.template_name, context)

    def last_booking_update(self, customer):
        lub = ''
        today = timezone.now().date()
        last_updated_booking = Booking.objects.filter(customer=customer, booking_type__in=(0, 1)).values('updated').order_by('-updated')[:1]
        if last_updated_booking.count() > 0:
            lub = last_updated_booking[0]['updated'].strftime("%d/%m/%Y %H:%M:%S")
            lub = lub + "-"+ today.strftime("%d/%m/%Y")
            return lub

    def booking_filter_upcoming(self, customer):
        today = timezone.now().date()

        bookings_store = []
        lub = self.last_booking_update(customer)
        cached_data = cache.get('booking_filter_upcoming:'+str(customer.id)+":"+str(lub))
        #cached_data = None
        if cached_data is None:
             bookings = Booking.objects.filter(customer=customer, booking_type__in=(0, 1), departure__gte=today).order_by('is_canceled','arrival')
             for b in bookings:
                 row = {}
                 row['id']  = b.id
                 row['campground']  = {}
                 row['campground']['name'] = b.campground.name
                 row['campground']['first_image']  = {}
                 row['campground']['first_image']['image'] = {}
                 row['campground']['first_image']['image']['url'] = b.campground.first_image.image.url
                 row['departure_str'] = b.departure.strftime("%Y-%m-%d")
                 row['arrival_str'] = b.arrival.strftime("%Y-%m-%d")
                 row['is_canceled'] = b.is_canceled
                 row['confirmation_number'] = b.confirmation_number
                 row['first_campsite'] = {} 
                 row['first_campsite']['type'] = b.first_campsite.type
                 row['first_campsite']['name'] = b.first_campsite.name
                 row['stay_dates'] = b.stay_dates
                 row['stay_guests'] = b.stay_guests
                 row['property_cache'] = b.property_cache
                 row['details'] = b.details

                 bookings_store.append(row)
        
                 cache.set('booking_filter_upcoming:'+str(customer.id)+":"+str(lub), json.dumps(bookings_store),  86400)
        else:
            bookings_store = json.loads(cached_data)

        bs = 0
        while bs < len(bookings_store):
            bookings_store[bs]['arrival'] = datetime.strptime(bookings_store[bs]['arrival_str'], "%Y-%m-%d").date()
            bookings_store[bs]['departure'] = datetime.strptime(bookings_store[bs]['departure_str'], "%Y-%m-%d").date()
            bs += 1

        return bookings_store

    def booking_filter_past_bookings(self, customer):
        today = timezone.now().date()
        bookings_store = []
        lub = self.last_booking_update(customer)
        cached_data = cache.get('booking_filter_past_bookings:'+str(customer.id)+":"+str(lub))
        #bookings = Booking.objects.filter(customer=customer, booking_type__in=(0, 1), departure__lt=today).order_by('-arrival'),
        
        if cached_data is None:
             bookings_past = Booking.objects.filter(customer=customer, booking_type__in=(0, 1), departure__lt=today).order_by('-arrival')[:60]
             for b in bookings_past:
                 row = {}
                 row['id']  = b.id
                 row['campground']  = {}
                 row['campground']['name'] = b.campground.name
                 row['campground']['first_image']  = {}
                 row['campground']['first_image']['image'] = {}
                 row['campground']['first_image']['image']['url'] = b.campground.first_image.image.url
                 row['departure_str'] = b.departure.strftime("%Y-%m-%d")
                 row['arrival_str'] = b.arrival.strftime("%Y-%m-%d")
                 row['is_canceled'] = b.is_canceled
                 row['confirmation_number'] = b.confirmation_number
                 row['first_campsite'] = {} 
                 row['first_campsite']['type'] = b.first_campsite.type
                 row['first_campsite']['name'] = b.first_campsite.name
                 row['stay_dates'] = b.stay_dates
                 row['stay_guests'] = b.stay_guests
                 row['details'] = b.details

                 bookings_store.append(row)
        
                 cache.set('booking_filter_past_bookings:'+str(customer.id)+":"+str(lub), json.dumps(bookings_store),  86400)
        else:
            bookings_store = json.loads(cached_data)

        bs = 0
        while bs < len(bookings_store):
            bookings_store[bs]['arrival'] = datetime.strptime(bookings_store[bs]['arrival_str'], "%Y-%m-%d").date()
            bookings_store[bs]['departure'] = datetime.strptime(bookings_store[bs]['departure_str'], "%Y-%m-%d").date()   
            bs += 1

        return bookings_store




class ParkstayRoutingView(TemplateView):
    template_name = 'ps/index.html'

    def get(self, *args, **kwargs):
        print ("PATH")
        if self.request.path == "/":
             return redirect(reverse('search_availablity_information'))
        #if self.request.user.is_authenticated:
        #    if is_officer(self.request.user):
        #        return redirect('dash-campgrounds')
        #    return redirect('public_my_bookings')
        kwargs['form'] = LoginForm
        return super(ParkstayRoutingView, self).get(*args, **kwargs)

class SearchAvailablity(TemplateView):

    template_name = 'ps/search_availabilty.html'

    def get(self, request, *args, **kwargs):
        context = {}
        features_obj = []
        features_obj_cache = cache.get('features_array_type_0:')

        if features_obj_cache is None:
            features_query = Feature.objects.filter(type=0)
            for f in features_query:
                features_obj.append({'id': f.id,'name': f.name, 'symb': 'RF8G', 'description': f.description, 'type': f.type, 'key': 'twowheel','remoteKey': [f.name]})
                cache.set('features_array_type_0:', json.dumps(features_obj),  86400)
        else:
            features_obj = json.loads(features_obj_cache)

        context['features'] = features_obj
        context['features_json'] = json.dumps(features_obj)
        return render(request, self.template_name, context)

    #def get(self, *args, **kwargs):
    #    return super(SearchAvailablity, self).get(*args, **kwargs)


class SearchAvailablityByCampground(TemplateView):

    template_name = 'ps/search_availabilty_campground.html'

    def get(self, request, *args, **kwargs):
        context = {'cg': {'campground': {},'campground_notices': []}}
        context_p = context_processors.parkstay_url(request)
        campground_id = request.GET.get('site_id', None)
        num_adult = request.GET.get('num_adult', 0)
        num_concession= request.GET.get('num_concession', 0)
        num_children= request.GET.get('num_children', 0)
        num_infants= request.GET.get('num_infants', 0)
        
        num_vehicle= request.GET.get('num_vehicle', 1) # cars
        num_campervan = request.GET.get('num_campervan', 0) 
        num_motorcycle = request.GET.get('num_motorcycle', 0)
        num_trailer = request.GET.get('num_trailer',0)
        num_caravan = request.GET.get('num_caravan',0)

        arrival=request.GET.get('arrival', None)
        departure=request.GET.get('departure', None)
        change_booking_id = request.GET.get('change_booking_id', None)

        today = timezone.now().date()
        context['change_booking'] = None
        if self.request.user.is_authenticated:
              if change_booking_id is not None:
                    if int(change_booking_id) > 0:
                          if Booking.objects.filter(id=change_booking_id, is_canceled=False).count() > 0:
                               cb = Booking.objects.get(id=change_booking_id)
                               if cb.customer.id == request.user.id or request.user.is_staff is True:
                                       if cb.arrival > today:
                                            context['change_booking'] = cb
                                       else:
                                           pass
                                           if request.user.is_staff is True:
                                                context['change_booking'] = cb
                                           else:
                                                context["error_message"] = "Sorry,  your booking has already started and cannot be changed."
                                       if 'selecttype' in cb.details:
                                          if cb.details['selecttype'] == 'multiple':
                                             if context_p['PARKSTAY_PERMISSIONS']['p0'] is True:
                                                 pass
                                             else:
                                                 context["error_message"] = "Sorry, you don't have the ability to manage a booking with mulitple sites"
                                       else:
                                           cb.details['selecttype'] = 'single'

                                       


        if context['change_booking'] is None:
              if change_booking_id is not None:
                      self.template_name = 'ps/search_availabilty_campground_change_booking_error.html'
                      return render(request, self.template_name, context)


        context['cg']['campground_id'] = campground_id
        context['cg']['num_adult'] = num_adult
        context['cg']['num_concession'] = num_concession
        context['cg']['num_children'] = num_children
        context['cg']['num_infants'] = num_infants
  
        context['cg']['num_vehicle'] = num_vehicle
        context['cg']['num_campervan'] = num_campervan
        context['cg']['num_motorcycle'] = num_motorcycle
        context['cg']['num_trailer'] = num_trailer
        context['cg']['num_caravan'] = num_caravan

        context['cg']['arrival'] = arrival
        context['cg']['departure'] = departure

        campground_query = Campground.objects.get(id=campground_id)
        max_people = Campsite.objects.filter(campground_id=campground_id).aggregate(Max('max_people'))["max_people__max"]
        max_vehicles = Campsite.objects.filter(campground_id=campground_id).aggregate(Max('max_vehicles'))["max_vehicles__max"]

        context['cg']['campground']['id'] = campground_query.id
        context['cg']['campground']['name'] = campground_query.name
        context['cg']['campground']['largest_camper'] = max_people
        context['cg']['campground']['largest_vehicle'] = max_vehicles
        context['cg']['campground']['campground_type'] = campground_query.campground_type
        context['cg']['campground']['park'] = {}
        context['cg']['campground']['park']['id'] = campground_query.park.id
        context['cg']['campground']['park']['alert_count'] = campground_query.park.alert_count
        context['cg']['campground']['park']['alert_url'] = settings.ALERT_URL
        context['cg']['campground']['description'] = campground_query.description
        context['cg']['campground']['about'] = campground_query.about
        context['cg']['campground']['booking_information'] = campground_query.booking_information
        context['cg']['campground']['campsite_information'] = campground_query.campsite_information
        context['cg']['campground']['facilities_information'] = campground_query.facilities_information
        context['cg']['campground']['campground_rules'] = campground_query.campground_rules
        context['cg']['campground']['fee_information'] = campground_query.fee_information
        context['cg']['campground']['health_and_safety_information'] = campground_query.health_and_safety_information
        context['cg']['campground']['location_information'] = campground_query.location_information
        context['cg']['campground']['campground_map'] = campground_query.campground_map

        if campground_query.campground_image:
            context['cg']['campground']['campground_image'] = campground_query.campground_image.image_size(1200,800)
        else:
            context['cg']['campground']['campground_image'] = ""
       
        context['cg']['campground']['camping_images'] = []
        campimages = parkstay_models.CampgroundImage.objects.filter(campground_id=campground_query.id)
        for ci in campimages:
            context['cg']['campground']['camping_images'].append({ 'image_url': ci.image.url })


        context['cg']['campground_notices_red'] = 0
        context['cg']['campground_notices_orange'] = 0
        context['cg']['campground_notices_blue'] = 0

        campground_notices_query = CampgroundNotice.objects.filter(campground_id=campground_id).order_by("order")
        
        campground_notices_array = []
        for cnq in campground_notices_query:
               if cnq.notice_type == 0:
                   context['cg']['campground_notices_red'] = context['cg']['campground_notices_red'] + 1
               if cnq.notice_type == 1:
                   context['cg']['campground_notices_orange'] = context['cg']['campground_notices_orange'] + 1
               if cnq.notice_type == 2:
                   context['cg']['campground_notices_blue'] = context['cg']['campground_notices_blue'] + 1

               campground_notices_array.append({'id': cnq.id, 'notice_type' : cnq.notice_type,'message': cnq.message})

        features_obj = []
        context['cg']['campground_notices'] = campground_notices_array
        features_query = Feature.objects.filter(type=1)
        for f in features_query:
            features_obj.append({'id': f.id,'name': f.name, 'symb': 'RF8G', 'description': f.description, 'type': f.type, 'key': 'twowheel','remoteKey': [f.name]})
        # {name: '2WD accessible', symb: 'RV2', key: 'twowheel', 'remoteKey': ['2WD/SUV ACCESS']},
        context['features'] = features_obj
        context['features_json'] = json.dumps(features_obj)
        return render(request, self.template_name, context)


class MapView(TemplateView):
    template_name = 'ps/map.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'ps/profile.html'
