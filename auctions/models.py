from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title= models.TextField()
    category= models.TextField()
    description= models.TextField()
    startingBid=models.FloatField()
    image=models.ImageField( null=True, blank=True, upload_to='images/')
    user=models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)

class Bid(models.Model):
    amount=models.IntegerField()
    user=models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    listing=models.ForeignKey(to=Listing, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

class Comment(models.Model):
    commentString=models.TextField()
    user=models.ForeignKey(to=User,on_delete=models.CASCADE, null=True)
    listing=models.ForeignKey(to=Listing, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

class WatchList(models.Model):
    listing=models.ForeignKey(to=Listing, on_delete=models.CASCADE, null=True)
    user=models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)

