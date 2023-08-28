from django import forms
from django.core.exceptions import ValidationError

from .models import Auction, Bid, Comment
from .utils import last_bid_amount


# def validate_category_length(value):
#     if len(value) > 60:
#         raise ValidationError("The category name must be shorter than 60 characters.")


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['product_name', 'description', 'image_url', 'category']

    # category = forms.CharField(validators=[validate_category_length])

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if product_name:
            product_names = Auction.objects.filter(is_active=True).values_list('product_name', flat=True)
            if product_name in product_names:
                raise ValidationError('Such game already exists')
        if len(product_name) > 50:
            raise ValidationError('Too long value.')
        return product_name


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']

    # def clean_bid_amount(self):
    #     pass

    # def clean_bid_amount(self):
    #     min_value = last_bid_amount()
    #     if min_value is not None:
    #         if min_value >= self.cleaned_data['bid_amount']:
    #             raise ValidationError('The bid should be more than last one')
    #     return self.cleaned_data['bid_amount']


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), label='') # чтобы убрать label

    class Meta:
        model = Comment
        fields = ['text']


class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))
