from django.contrib.gis import admin
from parkstay import models

from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from django.db.models import Q

#from ledger.accounts.models import EmailUser
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from django.http import HttpResponse

from copy import deepcopy

admin.site.index_template = 'admin-index.html'
admin.autodiscover()

@admin.register(models.EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    list_display = ('email','first_name','last_name','is_staff','is_active',)
    ordering = ('email',)
    search_fields = ('id','email','first_name','last_name')

    def has_change_permission(self, request, obj=None):
        if obj is None: # and obj.status > 1:
            return True
        return None 
    def has_delete_permission(self, request, obj=None):
        return None
        

@admin.register(models.CampsiteClass)
class CampsiteClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(models.Park)
class ParkAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'district')
    ordering = ('name',)
    list_filter = ('district',)
    search_fields = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

class CampgroundNoticeInline(admin.TabularInline):
    model = models.CampgroundNotice
    extra = 0

class CampsiteInline(admin.TabularInline):
    model = models.Campsite
    extra = 0
    exclude = ['wkb_geometry',]

@admin.register(models.Campground)
class CampgroundAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'park', 'promo_area', 'campground_type', 'site_type', 'max_advance_booking')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('campground_type', 'site_type')
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    inlines = [CampgroundNoticeInline,CampsiteInline]

#from django.forms.models import BaseInlineFormSet, ModelForm
#class AlwaysChangedModelForm(ModelForm):
#    def has_changed(self):
#        """ Should returns True if data differs from initial.
#        By always returning true even unchanged inlines will get validated and saved."""
#        return False
#    def save_new(self, form, commit=False):
#        pass
#        
#    def save_existing(self, form, instance, commit=False):
#        pass
#
#class ProductPlanningFormSet(BaseInlineFormSet):
#
#       def clean(self):
#          super(ProductPlanningFormSet, self).clean()
#          print ("CLEAN")
#
#       def save_new(self, form, commit=False):
#           print ('NEW P')
#           pass
#
#       def save_existing(self, form, instance, commit=False):
#           print ('NEW S')
#           pass

 
class CampgroundGroupAdminCampgroundInline(admin.TabularInline):
      model = models.CampgroundGroup.campgrounds.through
      raw_id_fields = ('campground',)
      #form = AlwaysChangedModelForm
      #formset = ProductPlanningFormSet

      def save_new_objects(self, commit=False):
          pass
      def save_new(self, form, commit=False):
          pass
      def save_existing(self, form, instance, commit=False):
          pass

class CampgroundGroupAdminMemberInline(admin.TabularInline):
      model = models.CampgroundGroup.members.through
      raw_id_fields = ('emailuserro',)

      def save_new_objects(self, commit=False):
          pass
      def save_new(self, form, commit=False):
          pass
      def save_existing(self, form, instance, commit=False):
          pass


@admin.register(models.CampgroundGroup)
class CampgroundGroupAdmin(admin.ModelAdmin):
    exclude = ('members','campgrounds',)
    inlines = [CampgroundGroupAdminCampgroundInline,CampgroundGroupAdminMemberInline,]

    def get_queryset(self, request):
        """ Filter based on the group of the user"""
        qs = super(CampgroundGroupAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.CampgroundGroup.objects.filter(members__in=[request.user, ])
        return qs.filter(id__in=group)

    def save_related(self, request, form, formsets, change):
        obj = form.instance
        for m in request.POST.lists():
            if m[0][:27] == 'CampgroundGroup_campgrounds':
               rowindex = m[0].split('-')
               if  m[0][-2:] == 'id': 
                   rowindex = m[0].split('-')
                   rowid = request.POST['CampgroundGroup_campgrounds-'+str(rowindex[1])+'-id']
                   campground = request.POST['CampgroundGroup_campgrounds-'+str(rowindex[1])+'-campground']
                   campgroundgroup = request.POST['CampgroundGroup_campgrounds-'+str(rowindex[1])+'-campgroundgroup']
                   campgroundgroup_prefix = request.POST['CampgroundGroup_campgrounds-__prefix__-campgroundgroup']
                   deleterow = False
                   if 'CampgroundGroup_campgrounds-'+str(rowindex[1])+'-DELETE'  in request.POST:
                        if request.POST['CampgroundGroup_campgrounds-'+str(rowindex[1])+'-DELETE'] == 'on':
                            deleterow = True
                          
                   if len(rowid) > 0:
                      if int(rowid) > 0:
                           if deleterow is True:
                              models.CampgroundGroupCampgrounds.objects.filter(id=int(rowid)).delete()
                           else:
                              cgc = models.CampgroundGroupCampgrounds.objects.get(id=int(rowid))
                              cgc.campground_id = int(campground)
                              cgc.campgroundgroup_id = int(campgroundgroup)
                              cgc.save()
                   else:
                       if len(campground) > 0:
                          models.CampgroundGroupCampgrounds.objects.create(campground_id=int(campground),campgroundgroup_id=int(campgroundgroup_prefix))

            if m[0][:23] == 'CampgroundGroup_members':
               rowindex = m[0].split('-')
               if  m[0][-2:] == 'id':

                   rowindex = m[0].split('-')
                   rowid = request.POST['CampgroundGroup_members-'+str(rowindex[1])+'-id']
                   emailuserro = request.POST['CampgroundGroup_members-'+str(rowindex[1])+'-emailuserro']
                   campgroundgroup = request.POST['CampgroundGroup_members-'+str(rowindex[1])+'-campgroundgroup']
                   campgroundgroup_prefix = request.POST['CampgroundGroup_members-__prefix__-campgroundgroup']
                   deleterow = False

                   if 'CampgroundGroup_members-'+str(rowindex[1])+'-DELETE'  in request.POST:
                        if request.POST['CampgroundGroup_members-'+str(rowindex[1])+'-DELETE'] == 'on':
                            deleterow = True

                   if len(rowid) > 0:
                      if int(rowid) > 0:
                           if deleterow is True:
                              models.CampgroundGroupMembers.objects.filter(id=int(rowid)).delete()
                           else:
                              cgc = models.CampgroundGroupMembers.objects.get(id=int(rowid))
                              cgc.emailuser_id = int(emailuserro)
                              cgc.campgroundgroup_id = int(campgroundgroup)
                              cgc.save()
                   else:
                       if len(emailuserro) > 0:
                          print ("CREEATEING NEW MEMBER")
                          models.CampgroundGroupMembers.objects.create(emailuser_id=int(emailuserro),campgroundgroup_id=int(campgroundgroup_prefix))


               if  m[0][-10:] == 'campgroundii':
                   rowindex = m[0].split('-')
                   CampgroundGroup_campgrounds-0-id


        for formset in formsets:
            instances = formset.save(commit=False)

@admin.register(models.EmailGroup)
class EmailGroupAdmin(admin.ModelAdmin):
    list_display = ('email','email_group','active')
    list_filter = ('email_group',)

@admin.register(models.Campsite)
class CampsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'campground',)
    ordering = ('name',)
    list_filter = ('campground',)
    search_fields = ('name',)

@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)
    search_fields = ('name',)


class BookingInvoiceInline(admin.TabularInline):
    model = models.BookingInvoice
    extra = 0

class BookingAdditionalInline(admin.TabularInline):
    model = models.AdditionalBooking
    extra = 0

class CampsiteBookingInline(admin.TabularInline):
    model = models.CampsiteBooking
    extra = 0
    raw_id_fields=('campsite',)

@admin.register(models.Booking)
class BookingAdmin(admin.ModelAdmin):
    #raw_id_fields = ('customer','overridden_by','canceled_by',)
    list_display = ('id','customer','arrival', 'departure', 'campground','booking_type', 'cost_total','property_cache_version','property_cache_stale')
    ordering = ('-id',)
    #search_fields = ('id','arrival', 'departure')
    search_fields = ('id',)
    list_filter = ('booking_type','arrival', 'departure', 'campground', )
    inlines = [BookingInvoiceInline, CampsiteBookingInline, BookingAdditionalInline]
    readonly_fields=('created','property_cache','customer','overridden_by','canceled_by')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(models.CampsiteBooking)
class CampsiteBookingAdmin(admin.ModelAdmin):
    list_display = ('id','campsite', 'date', 'booking', 'booking_type')
    #list_display = ('date', 'booking', 'booking_type')
    ordering = ('-id',)
    #search_fields = ('date',)
    list_filter = ('campsite', 'booking_type')
    raw_id_fields = ('campsite','booking',)


@admin.register(models.CampsiteRate)
class CampsiteRateAdmin(admin.ModelAdmin):
    list_display = ('campsite', 'rate', 'allow_public_holidays')
    list_filter = ('campsite', 'rate', 'allow_public_holidays')
    search_fields = ('campground__name',)


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number')
    search_fields = ('name', 'phone_number')


class ReasonAdmin(admin.ModelAdmin):
    list_display = ('code', 'text', 'editable')
    search_fields = ('code', 'text')
    readonly_fields = ('code',)

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj and not obj.editable:
            fields += ['text', 'editable']
        elif not obj:
            fields = []
        return fields

    def has_add_permission(self, request, obj=None):
        if obj and not obj.editable:
            return False
        return super(ReasonAdmin, self).has_delete_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not obj.editable:
            return False
        return super(ReasonAdmin, self).has_delete_permission(request, obj)


@admin.register(models.MaximumStayReason)
class MaximumStayReason(ReasonAdmin):
    pass


@admin.register(models.PriceReason)
class PriceReason(ReasonAdmin):
    pass


@admin.register(models.ClosureReason)
class ClosureReason(ReasonAdmin):
    pass


@admin.register(models.OutstandingBookingRecipient)
class OutstandingBookingRecipient(admin.ModelAdmin):
    pass


@admin.register(models.PromoArea)
class PromoAreaAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'wkb_geometry')
    ordering = ('name',)
    search_fields = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

@admin.register(models.Places)
class PlacesAdmin(admin.GeoModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

admin.site.register(models.Rate)
admin.site.register(models.Region)
admin.site.register(models.District)
admin.site.register(models.DiscountReason)
admin.site.register(models.BookingPolicy)
