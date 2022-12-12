from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    # hang off a user object for convenience in layout header
    def all_listings(self):
        return Listing.objects.all()

    # hang off a user object for convenience in layout header
    def active_listings(self):
        return Listing.objects.filter(active=True)



class Listing(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_listings")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='images/listings', blank=True)
    active = models.BooleanField(default=True)
    starting_bid = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_listings")
    categories = models.ManyToManyField('Category', blank=True, related_name="listings")

    def __str__(self):
        return f'{self.title}'

    def toggle_watcher(self, user):
        user_is_watching = self.watchers.filter(id=user.id).exists()
        if user_is_watching:
            self.watchers.remove(user)
        else:
            self.watchers.add(user)

    def minimum_bid(self):
        return max(self.starting_bid, 1+self.high_bid_amount())

    def high_bid_amount(self):
        bid = self.bids.all().order_by('-created_at').first()
        if bid:
            return bid.amount
        else:
            return 0

    def watcher_count(self):
        return len(self.watchers.all())
 
            

class Bid(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.IntegerField()


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=500)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='images/categories', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name