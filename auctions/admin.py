from django.contrib import admin

# Register your models here.
from auctions.models import Auction, Bid, Comment, WatchListStorage, User, Category


class AuctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name')


class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'bidder', 'auction')

    def auction(self, obj):  # будем видеть для какого аукциона есть ставка.
        auctions = obj.auction_set.all()
        if auctions:
            return auctions[0]
        return None
    auction.short_description = 'Auction'


admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)
admin.site.register(WatchListStorage)
admin.site.register(User)
admin.site.register(Category)
