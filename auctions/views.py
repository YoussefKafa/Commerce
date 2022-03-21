from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import utils
from .models import *
from .forms import ListingForm
from datetime import datetime
import datetime as dt
from django.contrib.auth.decorators import login_required
from django.db.models import Max
def index(request, *args, **kwargs):
    if request.user.is_authenticated:
            listings = Listing.objects.all()
    else:
        listings=[]
    return render(request, "auctions/index.html"  , {"listings":listings, "current_user":request.user.id})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def newListing(request):
    return render(request, "auctions/listing.html")


def saveListing(request, *args, **kwargs):
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            lisSaved=form.save()
            lisData=Listing.objects.filter(pk=lisSaved.id)
            lisSaved.user=request.user
            lisSaved.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect ('newListing')

def listingMainPage(request, listingId):
    x=getListingMainPage(request,listingId)
    owner=False
    lis=Listing.objects.get(pk=listingId)
    if(lis.user == request.user):
        owner=True
    return render(request, "auctions/listingMainPage.html", {"owner":owner,"watched":x["watched"],"lis":x["lis"], "Cuser":x["Cuser"], "comments":x["comments"]})

def submitted(request):
    return render(request, "auctions/submitted.html")


def addToWatchList(request, listingId):
    #add the listing to user watchlist
    watchListRecord=WatchList()
    lis =Listing.objects.get(id=listingId)
    watchListRecord.listing=lis
    watchListRecord.user=request.user
    watchListRecord.save()
    x=getListingMainPage(request,listingId)
    return reverse(request, "auctions/listingMainPage.html", {"watched":x["watched"],"lis":x["lis"], "Cuser":x["Cuser"], "comments":x["comments"]})


def removeFromWatchList(request, listingId):
    lis =Listing.objects.get(id=listingId)
    #add the listing to user watchlist
    WatchList.objects.filter(listing=lis, user=request.user).delete()
    x=getListingMainPage(request,listingId)
    return render(request, "auctions/listingMainPage.html", {"watched":x["watched"],"lis":x["lis"], "Cuser":x["Cuser"], "comments":x["comments"]})

def bid(request):
    bidError=False
    listingId=int(request.POST.get('lis'))
    bid=Bid()
    bid.amount=request.POST.get('amount')
    bid.user=request.user
    listing=Listing.objects.get(pk=listingId)
    listingComments=Comment.objects.filter(listing=listing)
    bid.listing=listing
    bid.date=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    if(int(bid.amount) <= listing.startingBid):
        bidError=True
        return render(request, "auctions/listingMainPage.html", {"lis":listing,"bidError":bidError, "Cuser":request.user, "comments":listingComments})
    #fetch last listing bids
    listingBids=Bid.objects.filter(listing=listing)
    bidHistory=[]
    for item in listingBids:
        bidHistory.append(item.amount)
    for n in bidHistory:
        if( int(bid.amount) <= n):
            request.session['bidError']=True  
            bidError=True
            return render(request, "auctions/listingMainPage.html", {"lis":listing,"bidError":bidError, "Cuser":request.user, "comments":listingComments})
    bid.save()
    lis =Listing.objects.get(id=listingId)
    listingBids=Bid.objects.filter(listing=lis)
    listingComments=Comment.objects.filter(listing=lis)
    bidHistory=[]
    for n in listingBids:
      bidHistory.append(n.amount)
      lis.bidHistory=bidHistory
      if(len(bidHistory) != 0):
          lis.lastBid=max(bidHistory)
    user=utils.get_user(lis.user_id)
    return render(request, "auctions/listingMainPage.html", {"lis":lis, "Cuser":request.user, "comments":listingComments})

def closeListing(request, listingId):
    #close the listing 
    listing= Listing.objects.get(pk=listingId)
    listing.closed= True
    listing.closedDate= dt.datetime.now()
    #define the winner
    listingBids=Bid.objects.filter(listing=listing)
    maxBidAmount= Bid.objects.aggregate(Max('amount'))
    maxBid= Bid.objects.filter(amount=maxBidAmount['amount__max'])
    winnerBid= maxBid.first()
    listing.winner=winnerBid.user
    listing.save()
    x=getListingMainPage(request,listingId)
    lis=Listing.objects.get(pk=listingId)
    return render(request, "auctions/listingMainPage.html", {"watched":x["watched"],"lis":x["lis"], "Cuser":x["Cuser"], "comments":x["comments"]})

def saveComment(request):
    listing= Listing.objects.get(pk=int(request.POST.get('listing')))
    comment=Comment()
    comment.commentString=request.POST.get('comment')
    comment.user=request.user
    comment.listing=listing
    comment.date=dt.datetime.now()
    comment.save()
    lis =Listing.objects.get(id=int(request.POST.get('listing')))
    listingBids=Bid.objects.filter(listing=lis)
    listingComments=Comment.objects.filter(listing=lis)
    bidHistory=[]
    for n in listingBids:
      bidHistory.append(n.amount)
      lis.bidHistory=bidHistory
      lis.lastBid=max(bidHistory)
    user=utils.get_user(lis.user_id)
    return render(request, "auctions/listingMainPage.html", {"lis":lis, "Cuser":user, "comments":listingComments})


def watchList(request):
    watchList=WatchList.objects.filter(user=request.user.id)
    listings=[]
    for obj in watchList:
        listing=Listing.objects.get(pk=obj.listing.id)
        listings.append(listing)
    return render(request, "auctions/watchList.html", {"listings":listings})


def categories(request):
   activeListings=Listing.objects.filter(closed=False)
   cats=[]
   for listing in activeListings:
       if (listing.category not in cats):
           cats.append(listing.category)
   print(cats)
   return render(request, "auctions/categories.html", {"cats":cats})

def byCategory(request,category):
    bidError=False
    owner=False
    if request.user.is_authenticated:
        listings = Listing.objects.filter(category=category)
        #fetch user watchlist
        watchlist=WatchList.objects.filter(user=request.user)
        watched=[]
        for item in watchlist:
           exist= item.user==request.user
           watched.append(item.listing)
        for item in listings:
            if (item in watched):
                item.watched=True
            else:
                item.watched=False
            listingBids=Bid.objects.filter(listing=item)
            bidHistory=[]
            if ( item.user == request.user ):
                owner=True
            for n in listingBids:
                bidHistory.append(n.amount)
            item.bidHistory=bidHistory
            if(len(bidHistory) != 0):
                item.lastBid=max(bidHistory)
    else:
        listings=[]
    return render(request, "auctions/index.html"  , {"listings":listings, "bidError":bidError, "owner":owner, "current_user":request.user.id})




def isWatched(user, listing):
    watchlist=WatchList.objects.filter(user=user)
    for item in watchlist:
        if(item.listing==listing):
            print("watched")
            return True
    print("not watched")
    return False

def getListingMainPage(request,listingId):
    lis =Listing.objects.get(id=listingId)
    listingBids=Bid.objects.filter(listing=lis)
    listingComments=Comment.objects.filter(listing=lis)
    bidHistory=[]
    for n in listingBids:
      bidHistory.append(n.amount)
      lis.bidHistory=bidHistory
      if(len(bidHistory) != 0):
          lis.lastBid=max(bidHistory)
    user=utils.get_user(lis.user_id)
    watched=isWatched(request.user, lis)
    return  {"watched":watched,"lis":lis, "Cuser":request.user, "comments":listingComments}