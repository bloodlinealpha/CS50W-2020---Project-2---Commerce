from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, Watchlist, Bid, Comment


def index(request):
    context = {
        "listings": Listing.objects.all(),
    }
    return render(request, "auctions/index.html", context)

def closed(request):
    context = {
        "listings": Listing.objects.all(),
    }
    return render(request, "auctions/closed.html", context)

def category(request, cat_name):
    context = {
        "listings": Listing.objects.filter(category=cat_name),
        'category': cat_name,
    }
    return render(request, "auctions/category.html", context)

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

def create_listing(request):
    if request.method == "POST":
        current_user = request.user
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST["category"]
        starting_price = request.POST["starting_price"]
        url = request.POST["image_url"]

        listing = Listing(user=current_user, title=title, description=description, category=category, starting_price=starting_price, url=url)
        listing.save()

        #return to newly created listing
        return HttpResponseRedirect(reverse("index"))
    context = {
        'categories': Listing.CATEGORY,
    }
    return render(request, "auctions/create_listing.html", context)

def listing(request, listing_id):
    b = Bid.objects.filter(listing__pk=listing_id)
    comments_all = Comment.objects.filter(listing__pk=listing_id)
    try:
        winner_bid = Bid.objects.get(listing__pk=listing_id, winner="Yes")
    except:
        winner_bid = ""

    highest= 0

    for bid in b:
        price = bid.bid_price
        if price > highest:
            highest = bid.bid_price

    winning = Bid.objects.filter(bid_price=highest)

    if request.user.is_authenticated:
        current_user = request.user
       
        
        if Watchlist.objects.filter(user=current_user):
            w = Watchlist.objects.get(user=current_user)
            if w.watchlists.filter(pk=listing_id):
                watchlist = w.watchlists.get(pk=listing_id)
            else:
                watchlist = ""
        else:
            watchlist = ""
        context = {
            'listing': Listing.objects.get(pk=listing_id),
            'watchlists': watchlist,
            'bids': b,
            'winning': winning,
            'comments': comments_all,
            'winner':winner_bid,
        }
        #for bidding, adding comments
        if request.method == "POST":
            if 'bid_submit' in request.POST:
                try:
                    val = float(request.POST['bid'])
                except ValueError:
                    messages.add_message(request, messages.INFO, f"You did not enter a valid number", extra_tags="bid_error")
                    return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
               
                b2 = Bid.objects.filter(listing__pk=listing_id)
                starting_price = Listing.objects.get(pk=listing_id).starting_price
                highest2= starting_price

                for bid2 in b2:
                    price2 = bid2.bid_price
                    if price2 > highest2:
                        highest2 = bid2.bid_price

                if float(request.POST['bid']) <= float(highest2):
                    messages.add_message(request, messages.INFO, f"Your bid needs to be higher than ${highest2}", extra_tags="bid_error")
                    return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
                else:
                    current_user = request.user
                    bid = request.POST["bid"]
                    listing = Listing.objects.get(pk=listing_id)
                    b2 = Bid(user=current_user, listing=listing, bid_price=bid)
                    b2.save()
                    
                    messages.add_message(request, messages.INFO, 'Your Bid was successfully placed!', extra_tags="bid_success")
                    return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
            elif 'add_comment' in request.POST:
                comments = request.POST["comment"]
                listing = Listing.objects.get(pk=listing_id)
                c = Comment(user = current_user, listing=listing, comments=comments)
                c.save()

                return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
            elif 'end_listing' in request.POST:
                listing = Listing.objects.get(pk=listing_id)
                listing.active = "No"
                listing.save()

                b2 = Bid.objects.filter(listing__pk=listing_id)
                highest2= 0

                for bid2 in b2:
                    price2 = bid2.bid_price
                    if price2 > highest2:
                        highest2 = bid2.bid_price

                win = Bid.objects.get(bid_price=highest2)
                win.winner = "Yes"
                win.save()

                return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
            


        return render(request, "auctions/listing.html", context)



    return render(request, "auctions/listing.html", {
        'listing': Listing.objects.get(pk=listing_id),
        'bids': b,
        'winning': winning,
        'comments': comments_all,
        })

def watchlist(request):
    current_user = request.user

    watchlist_exist = Watchlist.objects.filter(user=current_user)             
    if watchlist_exist:
        user_list = Watchlist.objects.get(user=current_user)
        watchlists = user_list.watchlists.all()
        context = {
        'listings': watchlists,
        }

        if request.method == "POST":
            if 'add_watchlist' in request.POST:
                listing_id = request.POST["id"]
                w = Watchlist.objects.get(user=current_user)
                w.watchlists.add(listing_id)

                return HttpResponseRedirect(reverse('watchlist'))
            elif 'remove_watchlist' in request.POST:
                listing_id = request.POST["id"]
                w = Watchlist.objects.get(user=current_user)
                w.watchlists.remove(listing_id)

                return HttpResponseRedirect(reverse('watchlist'))

        return render(request, "auctions/watchlist.html", context)
        

    else:
        if request.method == "POST":
            if 'add_watchlist' in request.POST:
                listing_id = request.POST["id"]
                w = Watchlist(user=current_user)
                w.save()
                w.watchlists.add(listing_id)

                return HttpResponseRedirect(reverse('watchlist'))

        return render(request, "auctions/watchlist.html")

    
