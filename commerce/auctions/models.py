from django.contrib.auth.models import AbstractUser
from django.db import models
# from Pillow import ImageField

class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    start_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    sold = models.BooleanField(default=False)
    current_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_listings')
    image = models.ImageField(upload_to='auctions/images/')
    
    # THis will replace any image gets deleted by user and also place a default image when user doesn't provide an image
    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'auctions/images/default.png'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return 'title: {}, seller: {}, current_price: {}'.format(self.title, self.seller, self.current_bid)

    
class Bid(models.Model):
    bidder_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)
    product_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='product_bids')
    
    def __str__(self):
        return 'bidder_id: {}, bid_amount: {}, bid_date: {}, product_id: {}'.format(self.bidder_id, self.bid_amount, self.bid_date, self.product_id)
    

class Comment(models.Model):
    comment = models.TextField()
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_commnets')
    comment_date = models.DateTimeField(auto_now_add=True)
    product_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='product_comments')

    def __str__(self):
        return 'comment: {}, commenter: {}, comment_date: {}, product_id: {}'.format(self.comment, self.commenter, self.comment_date, self.product_id)
    
    
class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_watchlist')
    product_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='product_watchlist')
    
    def __str__(self):
        return 'user_id: {}, product_id: {}'.format(self.user_id, self.product_id)