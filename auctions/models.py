from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    
class Listing(models.Model):
	CATEGORY = [
		('Books', 'Books'),
		('Home', "Home"),
		('Electronics', 'Electronics'),
		('Vehicles', 'Vehicles'),
		('Other', 'Other'),
	]
	ACTIVE = [
	('Yes', 'Yes'),
	('No', 'No'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	create_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now=True)
	title = models.CharField(max_length=64)
	description = models.CharField(max_length=500)
	starting_price = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.CharField(max_length=32, choices=CATEGORY, default='Other')
	url = models.CharField(max_length=256, blank=True)
	active = models.CharField(max_length=3, choices=ACTIVE, default='Yes')


	def __str__(self):
		return f"{self.title} - User: {self.user} - Active: {self.active}"

class Watchlist(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	watchlists = models.ManyToManyField(Listing, blank=True)

	def __str__(self):
		return f"{self.user}"

class Bid(models.Model):

	WINNER = [
	('Yes', 'Yes'),
	('No', 'No'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	create_bid = models.DateTimeField(auto_now_add=True)
	update_bid = models.DateTimeField(auto_now=True)
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
	bid_price = models.DecimalField(max_digits=8, decimal_places=2)
	winner = models.CharField(max_length=256, choices=WINNER, default="No")

	def __str__(self):
		return f"User: {self.user} - Title: {self.listing.title} - Price: ${self.bid_price}"

class Comment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	create_comments = models.DateTimeField(auto_now_add=True)
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
	comments = models.CharField(max_length=500)

	def __str__(self):
		return f"{self.user} - {self.listing.title}"
