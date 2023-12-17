from django import forms
from django.core.validators import MinValueValidator
from .models import AuctionListing

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=10)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(label="Starting bid", max_digits=10, decimal_places=2, min_value=1)
    image = forms.ImageField(required=False)
    category = forms.ChoiceField(choices=[('Fashion', 'Fashion'), ('Toys', 'Toys'), ('Electronics', 'Electronics'), ('Home', 'Home')])
    
class AddBidForm(forms.Form):
    bid_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        label="",
        widget=forms.NumberInput(attrs={'placeholder': 'Bid', 'class': 'bid-input'})
    )