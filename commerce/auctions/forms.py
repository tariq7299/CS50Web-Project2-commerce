from django import forms
from django.core.validators import MinValueValidator
from .models import AuctionListing, Comment

class NewListingForm(forms.Form):
    title = forms.CharField(max_length=45)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(label="Starting bid", max_digits=10, decimal_places=2, min_value=1)
    image = forms.ImageField(required=False)
    category = forms.ChoiceField(choices=[('Fashion', 'Fashion'), ('Toys', 'Toys'), ('Electronics', 'Electronics'), ('Home', 'Home'), ('Clothing', 'Clothing'), ('Shoes', 'Shoes'), ('Furniture and Decor', 'Furniture and Decor'), ('Food and Beverage', 'Food and Beverage')])
    
class AddBidForm(forms.Form):
    bid_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        label="",
        widget=forms.NumberInput(attrs={'placeholder': 'Bid', 'class': 'bid-input'})
    )
    
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', 'commenter', 'product']
        widgets = {
            'commenter': forms.HiddenInput(),
            'product': forms.HiddenInput(),
            'comment' : forms.Textarea(attrs={'placeholder': 'Write your comment here...', 'class': 'comment-input', 'label': ''})
        }
        labels = {
            'comment': '',
        }
        
        def clean(self):
            cleaned_data = super().clean()
            comment = cleaned_data.get('comment')

            # Add your constraints here
            if len(comment) < 10:
                raise forms.ValidationError(
                    "Your comment must be at least 10 characters long."
                )

            # Always return cleaned_data
            return cleaned_data