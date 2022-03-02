from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import utils
from .models import *
from .forms import ListingForm
from datetime import datetime
from django.contrib.auth.decorators import login_required

def index(request, *args, **kwargs):
    bidError=False
    if request.user.is_authenticated:
        if 'bidError' in request.session:
            bidError=True
            del request.session['bidError']
            request.session.modified = True
        listings = Listing.objects.all()
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
            for n in listingBids:
                bidHistory.append(n.amount)
            item.bidHistory=bidHistory
            item.lastBid=max(bidHistory)
    else:
        listings=[]
    for item in listings:
        print(item.lastBid)
    return render(request, "auctions/index.html"  , {"listings":listings, "bidError":bidError})


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
            print(lisSaved.id)
            lisData=Listing.objects.filter(pk=lisSaved.id)
            lisSaved.user=request.user
            lisSaved.save()
            return HttpResponseRedirect ('submitted')
        else:
            return HttpResponseRedirect ('newListing')

def listingMainPage(request, listingId):
    lis =Listing.objects.get(id=listingId)
    user=utils.get_user(lis.user_id)
    return render(request, "auctions/listingMainPage.html", {"lis":lis, "user":user})

def submitted(request):
    return render(request, "auctions/submitted.html")


def addToWatchList(request, listingId):
    #add the listing to user watchlist
    watchListRecord=WatchList()
    lis =Listing.objects.get(id=listingId)
    watchListRecord.listing=lis
    watchListRecord.user=request.user
    watchListRecord.save()
    return HttpResponseRedirect (reverse("index"))


def removeFromWatchList(request, listingId):
    lis =Listing.objects.get(id=listingId)
    #add the listing to user watchlist
    WatchList.objects.filter(listing=lis, user=request.user).delete()
    return HttpResponseRedirect (reverse("index"))

def bid(request):
    listingId=int(request.POST.get('listing'))
    bid=Bid()
    bid.amount=request.POST.get('amount')
    bid.user=request.user
    listing=Listing.objects.get(pk=listingId)
    bid.listing=listing
    bid.date=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    if(int(bid.amount) <= listing.startingBid):
        request.session['bidError']=True
        return HttpResponseRedirect (reverse("index"))
    #fetch last listing bids
    listingBids=Bid.objects.filter(listing=listing)
    bidHistory=[]
    for item in listingBids:
        bidHistory.append(item.amount)
    for n in bidHistory:
        if( int(bid.amount) <= n):
            request.session['bidError']=True  
            return HttpResponseRedirect (reverse("index"))
    bid.save()
    return HttpResponseRedirect (reverse("index"))