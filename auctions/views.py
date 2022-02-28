from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import utils
from .models import *
from .forms import ListingForm


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html"  , {"listings":listings})


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