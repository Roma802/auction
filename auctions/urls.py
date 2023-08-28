
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import AuctionDetailView, AuctionListView

urlpatterns = [
    # path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_auction/", views.create_auction, name="create_auction"),
    path('auctions/<slug:slug>/', AuctionDetailView.as_view(), name='auction_detail'),
    path('auctions/', AuctionListView.as_view(), name='auction_list'),
    path('make_bid/<slug:slug>/', views.make_bid, name='make_bid'),
    path('add_watchlist/<slug:slug>/', views.add_watchlist, name='add_watchlist'),
    path('delete_watchlist/<slug:slug>/', views.delete_watchlist, name='delete_watchlist'),
    path('auction_watchlist', views.auction_watchlist, name='auction_watchlist'),
    path('close_auction/<slug:slug>/', views.close_auction, name='close_auction'),
    path('add_comment/<slug:slug>/', views.add_comment, name='add_comment'),
    path('categories/', views.categories, name='categories'),
    path('detail_category/<slug:slug>/', views.detail_category, name='detail_category'),
    path('__debug__/', include('debug_toolbar.urls')),
    # path('auction_search/', SearchAuctionListView.as_view(), name='auction_search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
