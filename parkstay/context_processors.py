from django.conf import settings


def parkstay_url(request):
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
        'QUEUE_ACTIVE_HOSTS' : settings.QUEUE_ACTIVE_HOSTS
    }
