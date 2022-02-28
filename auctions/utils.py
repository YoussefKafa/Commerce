from auctions.models import Listing
from auctions.models import User


def get_listing(id):
   obj = Listing.objects.get(pk=id)
   return obj


def get_user(id):
   obj=User.objects.get(pk=id)
   return obj