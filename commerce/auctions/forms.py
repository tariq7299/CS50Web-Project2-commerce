from django import forms
from .models import AuctionListing

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(max_digits=10, decimal_places=2)
    image = forms.ImageField(required=False)
    category = forms.ChoiceField(choices=[('Fashion', 'Fashion'), ('Toys', 'Toys'), ('Electronics', 'Electronics'), ('Home', 'Home')], required=False)