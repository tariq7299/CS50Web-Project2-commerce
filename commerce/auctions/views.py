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
    
    if request.user.is_authenticated:
        if request.method == "POST" and request.user:
            
            # Get the user id from the database that matches the username of the current user
            user_id = User.objects.get(username=request.user.username).id

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
            return render(request, "auctions/create_listing.html", {'form': form})
        else:
            return render(request, "auctions/create_listing.html", {'form': NewListingForm()})
    else:
        return HttpResponseRedirect(reverse("login"))
    
    
def listing_page(request, listing_id):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    listing = AuctionListing.objects.get(pk=listing_id)
    user_id = User.objects.get(username=request.user.username).id
    product_belong_to_current_user = AuctionListing.objects.filter(seller=user_id, pk=listing_id).exists()
    found_in_watchlist = Watchlist.objects.filter(user=user_id, product=listing_id).exists()
    bid_form = AddBidForm()
    comment_form = CommentForm(initial={'commenter': user_id, 'product': listing_id})
    comments = Comment.objects.filter(product=listing_id)
    print('comments', comments )
    
    # The folloewong if code will define and detirmine the bid message that will appear above the bid input field
    if Bid.objects.filter(product=listing_id).exists():  
        
        bid_count = Bid.objects.filter(product_id=listing_id).count()
        
        heighest_bidder = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bidder
        
        heighest_bid = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bid_amount
        
        if Bid.objects.filter(product=listing_id, bidder_id=user_id).exists():
                    
            current_user_heighest_bid = Bid.objects.filter(product=listing_id, bidder_id=user_id).order_by('-bid_amount').first().bid_amount
                    
            if current_user_heighest_bid >= heighest_bid:
                
                bid_msg = f"{bid_count} bid(s) so far. Your bid is the current bid"
                
            else:
                        
                bid_msg = f"{bid_count} bid(s) so far. The current bid belongs to {heighest_bidder}"
                
        else:
            
            bid_msg = f"{bid_count} bid(s) so far. The current bid belongs to {heighest_bidder}"
    else:
        bid_msg = "No bids yet for this listing !"
    
    
    if request.method == "POST":
        
        if request.POST.get('_method') == 'PUT':
            
            if not Bid.objects.filter(product=listing_id).exists():
                
                AuctionListing.objects.filter(pk=listing_id, seller=user_id).update(sold=True)

                return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
            
            heighest_bidder = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bidder
            AuctionListing.objects.filter(pk=listing_id, seller=user_id).update(current_owner=heighest_bidder, sold=True)
            
            return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
        
        else:
            
            if 'bid_form_submit' in request.POST:
            
                bid_form = AddBidForm(request.POST)   
                
                if bid_form.is_valid():
                    
                    listing = AuctionListing.objects.get(pk=listing_id)
                    
                    minimum_listing_price = listing.current_bid
                    
                    bid_amount = bid_form.cleaned_data["bid_amount"]
                    
                    if bid_amount < minimum_listing_price:
                        bid_form.add_error("bid_amount", "The minimum bid amount should be equal or more the current price !!") 
                        
                        return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': bid_form, 'bid_msg': bid_msg, 'comment_form': comment_form, 'comments':comments})
                    
                    if Bid.objects.filter(product_id=listing_id).exists():
                        
                        heighest_bid = Bid.objects.filter(product=listing_id).order_by('-bid_amount').first().bid_amount
                        
                        if bid_amount > heighest_bid :
                            
                            AuctionListing.objects.filter(pk=listing_id).update(current_bid=bid_amount)
                            
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
                    
                    comment = comment_form.save()
                    print('comment', comment)
                    
                    return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
                else:
                    # messages.error(request, comment_form.errors)
                    return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': bid_form, 'bid_msg': bid_msg, 'comment_form': comment_form, 'comments':comments})
                
    elif request.method == "GET":
        
        if listing.sold:
            if listing.seller == listing.current_owner:
                closed_auction_msg = f"This Auction has been closed and wasn't sold to any one !, as there were no bidders"
                return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': AddBidForm(), 'bid_msg': bid_msg, 'comment_form': comment_form, 'closed_auction_msg': closed_auction_msg})
            else:
                closed_auction_msg = f"This Auction has been closed and sold to {listing.current_owner}"
                return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': AddBidForm(), 'bid_msg': bid_msg, 'comment_form': comment_form, 'closed_auction_msg': closed_auction_msg})
        else:
            return render(request, "auctions/listing_page.html", {"listing":listing, 'found_in_watchlist': found_in_watchlist, 'product_belong_to_current_user':product_belong_to_current_user, 'bid_form': bid_form, 'bid_msg': bid_msg, 'comment_form': comment_form, 'comments':comments})
        
        
def add_remove_to_watchlist(request):
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
    
    
def watchlist(request):
    
    user_id = User.objects.get(username=request.user.username).id
    watchlists = Watchlist.objects.filter(user=user_id)
    
    # if not watchlists:
    #     return HttpResponse("no watch")
        
    return render(request, "auctions/watchlist.html", {'watchlists': watchlists})


def get_categories(request):
    categories=['Fashion', 'Toys', 'Electronics', 'Home', 'Clothing', 'Shoes', 'Furniture and Decor', 'Food and Beverage']
    return render(request, "auctions/categories.html", {'categories': categories})


def get_listing_in_a_category(request, category):
    listings_in_category = AuctionListing.objects.filter(category=category)
    print('listings_in_category', listings_in_category)
    return render(request, "auctions/listings_in_a_category.html", {'listings_in_category': listings_in_category})