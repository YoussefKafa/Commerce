from django.contrib.auth.models import AbstractUser
from django.db import models

DEFAULT_CASE_ID=1
class User(AbstractUser):
    pass

class Listing(models.Model):
    title= models.TextField(null=True, blank=True)
    category= models.TextField(null=True, blank=True)
    description= models.TextField(null=True, blank=True)
    startingBid=models.FloatField(null=True, blank=True)
    image=models.ImageField( null=True, blank=True, upload_to='images/')
    winner=models.ForeignKey(to=User,default=DEFAULT_CASE_ID,on_delete = models.SET_DEFAULT, null = True, related_name='winner')
    closedDate=models.TextField(null=True, blank=True)
    closed=models.BooleanField(default=False)
    user=models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)

class Bid(models.Model):
    amount=models.IntegerField(null=True, blank=True)
    user=models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    listing=models.ForeignKey(to=Listing, on_delete=models.CASCADE, null=True)
    date = models.TextField(null=True, blank=True)

class Comment(models.Model):
    commentString=models.TextField(null=True, blank=True)
    user=models.ForeignKey(to=User,on_delete=models.CASCADE, null=True)
    listing=models.ForeignKey(to=Listing, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

class WatchList(models.Model):
    listing=models.ForeignKey(to=Listing, on_delete=models.CASCADE, null=True)
    user=models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)

