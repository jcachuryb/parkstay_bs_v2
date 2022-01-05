from __future__ import unicode_literals
#from ledger.accounts.models import EmailUser
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from parkstay import models as parkstay_models
from django.core.cache import cache


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    belongs_to_value = cache.get('User-belongs_to'+str(user.id)+'group_name:'+group_name)
    if belongs_to_value:
        print ('From Cache - User-belongs_to'+str(user.id)+'group_name:'+group_name)
    if belongs_to_value is None:
       belongs_to_value = user.groups().filter(name=group_name).exists()
       cache.set('User-belongs_to'+str(user.id)+'group_name:'+group_name, belongs_to_value, 3600)
    return belongs_to_value

    
    #return user.groups().filter(name=group_name).exists()


def is_officer(user):
    is_officer_value = cache.get('User-is_officer'+str(user.id))
    is_officer_value = None
    if is_officer_value is None:
        is_officer_value = user.is_authenticated and (belongs_to(user, 'Parkstay Officers') or user.is_superuser)
        cache.set('User-is_officer'+str(user.id), is_officer_value, 3600)
    else:
        print ("From Cache is_officer")
    return is_officer_value
    #return user.is_authenticated and (belongs_to(user, 'Parkstay Officers') or user.is_superuser)


def is_customer(user):
    """
    Test if the user is a customer
    Rules:
        Not an officer
    :param user:
    :return:
    """
    is_customer_value = cache.get('User-is_customer'+str(user.id))
    if is_customer_value is None:
        is_customer_value = user.is_authenticated and not is_officer(user)
        cache.set('User-is_customer'+str(user.id), is_customer_value, 3600)
    else:
        print ("From Cache is_customer")

    return is_customer_value
    #return user.is_authenticated and not is_officer(user)


def get_all_officers():
    return EmailUser.objects.filter(groups__name='Parkstay Officers')

def can_view_campground(user, campground):
    # REVIEW FORE CACHING
    allowed_groups = parkstay_models.CampgroundGroupMembers.objects.filter(emailuser_id=user.id)
    for g in campground.campgroundgroup_set.all():
        for m in allowed_groups:
            if g.id == m.campgroundgroup_id:
                return True
        #if g.id == 3:
        #    print (g.id)
            #print (g.members.all()) 
            #if user in g.members.all():
            #    print ("can_view_campground True")
            #    return True
    return False
