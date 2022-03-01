from django.urls import path

from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("submitted", views.submitted, name="submitted"),
    path("newListing",views.newListing, name="newListing"),
    path("saveListing",views.saveListing,name="saveListing"),
    path("listingMainPage/<str:listingId>", views.listingMainPage,name="listingMainPage"),
    path("addToWatchList/<str:listingId>", views.addToWatchList, name="addToWatchList"),
    path("removeFromWatchList/<str:listingId>", views.removeFromWatchList, name="removeFromWatchList"),
    path("bid", views.bid, name="bid")
]

urlpatterns += staticfiles_urlpatterns()