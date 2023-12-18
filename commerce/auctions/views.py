from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import NewListingForm, AddBidForm, CommentForm
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
    
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the request method is POST and the user exists
        if request.method == "POST" and request.user:
            
            # Get the user id from the database that matches the username of the current user
            user_id = User.objects.get(username=request.user.username).id

            # Create a form instance with the data from the request
            form = NewListingForm(request.POST, request.FILES) 
            
            # Validate the form data
            if form.is_valid():

                # Extract the cleaned data from the form
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                starting_bid = form.cleaned_data['starting_bid']
                image = form.cleaned_data['image']
                category = form.cleaned_data['category']
                
                # Create a new AuctionListing instance with the form data and the current user's id
                new_listing = AuctionListing(title=title, description=description, seller_id=user_id, start_bid=starting_bid, current_bid=starting_bid, category=category, current_owner_id=user_id, image=image)
                
                # Save the new AuctionListing instance to the database
                new_listing.save()
                
                # Redirect the user to the index page
                return HttpResponseRedirect(reverse("index"))
            
            # If the form data is not valid, re-render the form with the existing data
            return render(request, "auctions/create_listing.html", {'form': form})
        
        # If the request method is not POST, render an empty form
        else:
            return render(request, "auctions/create_listing.html", {'form': NewListingForm()})
    
    # If the user is not authenticated, redirect them to the login page
    else:
        return HttpResponseRedirect(reverse("login"))

    
    
def listing_page(request, listing_id):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    # Get the listing with the provided id
    listing = AuctionListing.objects.get(pk=listing_id)
    
    user_id = User.objects.get(username=request.user.username).id
    
    # Check if the current user is the seller of the product
    product_belong_to_current_user = AuctionListing.objects.filter(seller=user_id, pk=listing_id).exists()
    
    # Check if the product is in the current user's watchlist
    found_in_watchlist = Watchlist.objects.filter(user=user_id, product=listing_id).exists()
    
    bid_form = AddBidForm()
    
    comment_form = CommentForm(initial={'commenter': user_id, 'product': listing_id})
    
    # Get all comments for the product
    comments = Comment.objects.filter(product=listing_id)
    
    # Check if there are any bids for the product
    if Bid.objects.filter(product=listing_id).exists():  
        
        # Count the number of bids
        bid_count = Bid.objects.filter(product_id=listing_id).count()
        
        # Get the highest bidder
        heighest_bidder = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bidder
        
        # Get the highest bid amount
        heighest_bid = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bid_amount
        
        # Check if the current user has placed any bids
        if Bid.objects.filter(product=listing_id, bidder_id=user_id).exists():
                    
            # Get the highest bid amount of the current user
            current_user_heighest_bid = Bid.objects.filter(product=listing_id, bidder_id=user_id).order_by('-bid_amount').first().bid_amount
                    
            # Check if the current user's highest bid is the current highest bid or bigger
            if current_user_heighest_bid >= heighest_bid:
                
                # Set the bid message to indicate that the current user's bid is the highest
                bid_msg = f"{bid_count} bid(s) so far. Your bid is the current bid"
                
            else:
                        
                # Set the bid message to indicate that the current highest bid belongs to another user
                bid_msg = f"{bid_count} bid(s) so far. The current bid belongs to {heighest_bidder}"
                
        else:
            
            # Set the bid message to indicate that the current highest bid belongs to another user
            bid_msg = f"{bid_count} bid(s) so far. The current bid belongs to {heighest_bidder}"
    else:
        # Set the bid message to indicate that there are no bids yet
        bid_msg = "No bids yet for this listing !"

    
    
    if request.method == "POST":
        
        # Checking if the request method is PUT
        if request.POST.get('_method') == 'PUT':
            
            # Checking if there are no bids for the product
            if not Bid.objects.filter(product=listing_id).exists():
                
                # If there are no bids, the product is marked as sold
                AuctionListing.objects.filter(pk=listing_id, seller=user_id).update(sold=True)

                return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
            
            # Getting the highest bidder for the product
            heighest_bidder = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bidder
            
            # Updating the current owner to the highest bidder and marking the product as sold
            AuctionListing.objects.filter(pk=listing_id, seller=user_id).update(current_owner=heighest_bidder, sold=True)
            
            return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
        
        else:
            
            # Checking if the bid form is submitted
            if 'bid_form_submit' in request.POST:
            
                bid_form = AddBidForm(request.POST)   
                
                if bid_form.is_valid():
                    
                    minimum_listing_price = listing.current_bid
                    
                    bid_amount = bid_form.cleaned_data["bid_amount"]
                    
                    # Checking if the bid amount is less than the minimum listing price
                    if bid_amount < minimum_listing_price:
                        # Adding an error to the bid form
                        bid_form.add_error("bid_amount", "The minimum bid amount should be equal or more the current price !!") 
                        # Rendering the listing page with the error
                        return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': bid_form, 'bid_msg': bid_msg, 'comment_form': comment_form, 'comments':comments})
                    
                    # Checking if there are any bids for the product
                    if Bid.objects.filter(product_id=listing_id).exists():
                        
                        heighest_bid = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bid_amount
                        
                        if bid_amount > heighest_bid :
                            
                            # Updating the current bid to the bid amount
                            AuctionListing.objects.filter(pk=listing_id).update(current_bid=bid_amount)
                            
                            # Saving the bid
                            Bid(bidder_id=user_id, bid_amount=bid_amount, product_id=listing_id).save()
                            
                        return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
                    else:
                        
                        AuctionListing.objects.filter(pk=listing_id).update(current_bid=bid_amount)
                        
                                    #$#$
                        # Here when I was inserting the bid user submitted, I used in "bidder" field in Bid(bidder), a user instance instead of just his 'id' (user_id)
                        
                        current_user_instance = User.objects.get(username=request.user.username)
                        
                        Bid(bidder=current_user_instance, bid_amount=bid_amount, product=listing).save()
                        
                        # SO here is another method to insert data in database
                        '''
                        Bid(bidder_id=user_id, bid_amount=bid_amount, product_id=listing_id).save()
                        '''
                                    #$#$
                        
                        return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
                else:
                    return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': bid_form, 'bid_msg': bid_msg, 'comment_form': comment_form, 'comments':comments})
                
            elif 'comment_form_submit' in request.POST:
                
                comment_form = CommentForm(request.POST)
                
                if comment_form.is_valid():
                    
                    comment_form.save()
                    
                    return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
                else:
                    # messages.error(request, comment_form.errors)
                    return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': bid_form, 'bid_msg': bid_msg, 'comment_form': comment_form, 'comments':comments})
                
    elif request.method == "GET":
            
        # Check if the listing has been sold
        if listing.sold:
            # Check if the seller is the current owner of the product
            if listing.seller == listing.current_owner:
                # Set a message indicating that the auction has been closed and wasn't sold to anyone
                closed_auction_msg = f"This Auction has been closed and wasn't sold to any one !, as there were no bidders"
                # Render the listing page with the relevant context variables
                return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': AddBidForm(), 'bid_msg': bid_msg, 'comment_form': comment_form, 'closed_auction_msg': closed_auction_msg})
            else:
                # Set a message indicating that the auction has been closed and sold to the current owner
                closed_auction_msg = f"This Auction has been closed and sold to {listing.current_owner}"
                # Render the listing page with the relevant context variables
                return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': AddBidForm(), 'bid_msg': bid_msg, 'comment_form': comment_form, 'closed_auction_msg': closed_auction_msg})
        else:
            # If the listing has not been sold, render the listing page with the relevant context variables
            return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': bid_form, 'bid_msg': bid_msg, 'comment_form': comment_form, 'comments':comments})
        
        
def add_remove_to_watchlist(request):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    user_id = User.objects.get(username=request.user.username).id
    
    # Was Testing to see if I was adding the csrf token successfully to the cookie
    '''    
    get_csrftoken = request.COOKIES['csrftoken']
    post_csrftoken = request.headers['X-CSRFToken']
    '''
    
    data = json.loads(request.body)  # Parse the JSON string
    listing_id = data.get('listing_id')  # Get the listing Iv from the parsed 

    try:
        # Create a new Watchlist item with the current user and listing
        item = Watchlist(user_id=user_id, product_id=listing_id)
        # Save the new item to the database
        item.save()
        # If successful, return a JSON response indicating the item was added
        return JsonResponse({'status': 'added'})
    # If an IntegrityError occurs (likely because the item already exists)
    except IntegrityError:
        # Get the existing item from the database
        item = Watchlist.objects.get(user_id=user_id, product_id=listing_id)
        # Delete the existing item
        item.delete()
        # Return a JSON response indicating the item was removed
        return JsonResponse({'status': 'removed'})
    # If any other exception occurs
    except Exception as e:
        # Create an error message
        error_message = f"Something bad happened! Please contact support. Error is {str(e)}"
        # Return a JSON response with the error status and message
        return JsonResponse({'status': 'error', 'error_message': error_message})

    
    
def watchlist(request):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    user_id = User.objects.get(username=request.user.username).id
    
    watchlists = Watchlist.objects.filter(user=user_id)
    
    return render(request, "auctions/watchlist.html", {'watchlists': watchlists})


def get_categories(request):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    categories=['Fashion', 'Toys', 'Electronics', 'Home', 'Clothing', 'Shoes', 'Furniture and Decor', 'Food and Beverage']
    return render(request, "auctions/categories.html", {'categories': categories})


def get_listing_in_a_category(request, category):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    listings_in_category = AuctionListing.objects.filter(category=category, sold=False)
    return render(request, "auctions/listings_in_a_category.html", {'listings_in_category': listings_in_category, 'category': category})