from parkstay import models
from django.conf import settings


def update_property_cache(booking_id):
    print ("THREADING")
    b = models.Booking.objects.get(id=int(booking_id))
    b.property_cache = b.update_property_cache(save=False)
    b.property_cache_version = settings.BOOKING_PROPERTY_CACHE_VERSION
    b.save(rebuild_cache=False)


