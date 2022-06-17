from django.conf import settings
from parkstay import models
from parkstay import utils
from django.core.cache import cache
import json

def parkstay_url(request):
    session_id = request.COOKIES.get('sessionid', None)
    is_authenticated = False
    if request.user.is_authenticated is True:
        is_authenticated = request.user.is_authenticated

    # staff need to login and logout for permissions to refresh
    parkstay_permissions_cache = cache.get('parkstay_url_permissions'+str(is_authenticated)+str(session_id))

    parkstay_permissions = {}
    if parkstay_permissions_cache is None:
        for pg in models.ParkstayPermission.PERMISSION_GROUP:
            parkstay_permissions['p'+str(pg[0])] = False

        if request.user.is_authenticated:
            parkstay_permissions_obj = models.ParkstayPermission.objects.filter(email=request.user.email)
            for pp in parkstay_permissions_obj:
                if pp.active is True:
                   parkstay_permissions['p'+str(pp.permission_group)] = True
        cache.set('parkstay_url_permissions'+str(is_authenticated)+str(session_id), json.dumps(parkstay_permissions),  86400)
    else:
        parkstay_permissions = json.loads(parkstay_permissions_cache)

    lt = utils.get_ledger_totals()

    return {
        'EXPLORE_PARKS_SEARCH': '{}'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_CONTACT': '{}/contact-us'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_CONSERVE': '{}/know/conserving-our-parks'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_PEAK_PERIODS': '{}/know/when-visit'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_ENTRY_FEES': '{}/know/park-entry-fees'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_TERMS': '{}/know/online-camp-site-booking-terms-and-conditions'.format(settings.EXPLORE_PARKS_URL),
        'PARKSTAY_EXTERNAL_URL': settings.PARKSTAY_EXTERNAL_URL,
        'DEV_STATIC': settings.DEV_STATIC,
        'DEV_STATIC_URL': settings.DEV_STATIC_URL,
        'VERSION_NO': settings.VERSION_NO,
        'WAITING_QUEUE_ENABLED': settings.WAITING_QUEUE_ENABLED,
        'GIT_COMMIT_DATE' : settings.GIT_COMMIT_DATE,
        'GIT_COMMIT_HASH' : settings.GIT_COMMIT_HASH,
        'QUEUE_DOMAIN' : settings.QUEUE_DOMAIN,
        'QUEUE_URL' : settings.QUEUE_URL,
        'QUEUE_ACTIVE_HOSTS' : settings.QUEUE_ACTIVE_HOSTS,
        'LEDGER_UI_URL' : settings.LEDGER_UI_URL,
        'PARKSTAY_PERMISSIONS' : parkstay_permissions,
        'template_group' : 'parksv2',
        'LEDGER_SYSTEM_ID' : settings.PS_PAYMENT_SYSTEM_ID.replace("S","0"),
        'template_title' : '',
        'ledger_totals': lt,
    }
