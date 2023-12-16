from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import NewListingForm
from django.http import JsonResponse
import json

from .models import User, AuctionListing, Bid, Comment, Watchlist


def index(request):
    # Get all rows from AuctionListing model where sold column is False
    listings = AuctionListing.objects.filter(sold=False)
    
    # Render 'auctions/index.html' with a variable holding all the rows extracted from the database

    
    return render(request, 'auctions/index.html', {'listings': listings})


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
    
    if request.user.is_authenticated:
        if request.method == "POST" and request.user:
            
            username = request.user.username
            
            # Get the user id from the database that matches the username of the current user
            user_id = User.objects.get(username=username).id

            form = NewListingForm(request.POST, request.FILES) 
            
            if form.is_valid():

                title = form.cleaned_data['title']

                description = form.cleaned_data['description']

                starting_bid = form.cleaned_data['starting_bid']
                image = form.cleaned_data['image']

                category = form.cleaned_data['category']
                
                new_listing = AuctionListing(title=title, description=description, seller_id=user_id, start_bid=starting_bid, current_bid=starting_bid, category=category, current_owner_id=user_id, image=image)
                
                new_listing.save()
                
                return HttpResponseRedirect(reverse("index"))
            
        else:
            return render(request, "auctions/create_listing.html", {'form': NewListingForm()})
    else:
        return HttpResponseRedirect(reverse("login"))
    
    
def listing_page(request, listing_id):
    
    if request.user.is_authenticated:
        
        user_id = User.objects.get(username=request.user.username).id
        product_belong_to_current_user = AuctionListing.objects.filter(seller=user_id, pk=listing_id).exists()
        found_in_watchlist = Watchlist.objects.filter(user=user_id, product=listing_id).exists()
        
        if request.method == "POST":
            pass
        elif request.POST.get('_method') == 'PUT':
            # heighest_bidder = 
            AuctionListing.objects.filter(pk=listing_id, user=user_id).update(current_owner=heighest_bidder, sold=True)
            
            
        elif request.method == "GET":
            listing = AuctionListing.objects.get(pk=listing_id)
            return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user})
        
    else:
        # messages.add_message(request, messages.ERROR, "Please log in first!")
        return HttpResponseRedirect(reverse("login"))
    
        
def add_to_watchlist(request):
    user_id = User.objects.get(username=request.user.username).id
    
    get_csrftoken = request.COOKIES['csrftoken']
    post_csrftoken = request.headers['X-CSRFToken']
    
    data = json.loads(request.body)  # Parse the JSON string
    listing_id = data.get('listing_id')  # Get the listing ID from the parsed 

    try:
        item = Watchlist(user_id=user_id, product_id=listing_id)
        item.save()
        return JsonResponse({'status': 'added'})
    except IntegrityError:
        item = Watchlist.objects.get(user_id=user_id, product_id=listing_id)
        item.delete()
        return JsonResponse({'status': 'removed'})
    except Exception as e:
        error_message = f"Somthing bad happend !, please contact support error is {str(e)}"
        return JsonResponse({'status': 'error', 'error_message': error_message})